# -*- coding: utf-8 -*-
'''
@version: old
@name: xyz
@date: 2020-05-06
@description: 抓取歌单详细信息
'''
import json
import sys
sys.path.append("..")
import re
import math
import msgpack
import asyncio
from loguru import logger
from typing import Dict
from aio_pika import IncomingMessage
from common.mixin import BaseCrawl
from util.decorators import decorator
from common.iter_get_dict import IterGetDict


DEFAULT_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://emumo.xiami.com/collect/363133540",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
}
PUBLISH_SONG_QUEUE_NAME = 'xiami_song_id_list'
PUBLISH_USER_QUEUE_NAME = 'xiami_user_id_list'
SUBSCRIBE_QUEUE_NAME = 'xiami_songs_list'


class SongsListSpider(BaseCrawl):

    fetch_url = 'https://emumo.xiami.com/collect/ajax-get-list?_=1588909083219&id={collect_id}&p={page}&limit=50'

    @BaseCrawl.start(queue_name=SUBSCRIBE_QUEUE_NAME)
    async def fetch(self, data: Dict[str, str], message: IncomingMessage):
        collect_id = list(data.keys())[0]
        page = list(data.values())[0]
        if int(page) >= 2:
            await message.ack()
            return None
        fetch_url = self.fetch_url.format(collect_id=collect_id, page=page)
        params_dict = {
            "url": fetch_url,
            "method": "GET",
            "headers": DEFAULT_HEADERS,
            "use_proxy": True,
            "timeout": 5,
            "parse_type": "json",
            "spider_name": "xiami_songs_list_spider",
        }
        response = await self.http_client.crawl_site(**params_dict)
        if response.status == 200:
            # 必须要在处理完数据之后，使用ack方法确认数据已接收
            await self.pipeline(response)
            await message.ack()
            return True
        else:
            return False

    async def pipeline(self, response):
        # todo 处理数据 + 入库操作
        res = response.source
        data_list = IterGetDict.dict_get(res, "data", None)
        if data_list:
            for data in data_list:
                song_id = data["song_id"]
                user_id = data["user_id"]
                print({"song_id": song_id, "user_id": user_id})
                await self.rabbitmq_pool.publish(PUBLISH_SONG_QUEUE_NAME, {"song_id": song_id})
                await self.rabbitmq_pool.publish(PUBLISH_USER_QUEUE_NAME, {"user_id": user_id})


if __name__ == '__main__':
    sl_spider = SongsListSpider()
    asyncio.run(sl_spider.fetch())
