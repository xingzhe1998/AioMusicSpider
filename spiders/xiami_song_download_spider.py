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
from util.params_encrypt import ParamsEncrypt


DEFAULT_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://emumo.xiami.com/collect/363133540",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
}
PUBLISH_QUEUE_NAME = 'xiami_song_download_url_list'
SUBSCRIBE_SONG_QUEUE_NAME = 'xiami_song_id_list'
SUBSCRIBE_COOKIE_QUEUE_NAME = 'xiami_cookie_list'


class SongDownloadSpider(BaseCrawl):

    api_url = 'https://www.xiami.com/api/song/getPlayInfo'

    def build_params(self, url):
        query = json.dumps("").replace(' ', '')
        _url = re.search(r"com(.*)", url).group(1)
        xm_sg_tk = re.search(r'xm_sg_tk=(.*?);', DEFAULT_HEADERS["cookie"]).group(1)
        prefix_params = {
            "query": query,
            "_url": _url,
            "xm_sg_tk": xm_sg_tk,
        }
        sign = ParamsEncrypt.get_sign(**prefix_params)
        params = {
            '_q': query,
            '_s': sign,
        }
        headers = DEFAULT_HEADERS
        fetch_params = {
            "url": url,
            "headers": headers,
            "params": params,
        }
        return fetch_params

    @BaseCrawl.start(queue_name=SUBSCRIBE_SONG_QUEUE_NAME)
    async def fetch(self, data: Dict[str, str], message: IncomingMessage):
        # todo 从rabbitmq队列中一次性获取多条数据
        song_id = data["song_id"]

        fetch_url = ""
        params_dict = {

            "method": "GET",
            "use_proxy": False,
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
        pass


if __name__ == '__main__':
    pass
