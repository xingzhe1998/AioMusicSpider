# -*- coding: utf-8 -*-
'''
@version: old
@name: xyz
@date: 2020-05-06
@description: 抓取歌单详细信息
'''
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
from util.retry_helper import aio_retry


DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,"
              "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
}
API_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://emumo.xiami.com/song/8G4eN5eeff3?spm=a1z1s.6626001.229054121.14.mE6Jc8",
    "User-Agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
}
PUBLISH_QUEUE_NAME = ''
SUBSCRIBE_QUEUE_NAME = 'xiami_song_id_list'


class SongDetailSpider(BaseCrawl):

    fetch_url = "https://emumo.xiami.com/song/{song_id}"
    xiami_api = "https://emumo.xiami.com/count/getplaycount?id={song_id}&type=song"

    @BaseCrawl.start(queue_name=SUBSCRIBE_QUEUE_NAME)
    async def fetch(self, data: Dict[str, str], message: IncomingMessage):
        song_id = data['song_id']
        fetch_url = self.fetch_url.format(song_id=song_id)
        params_dict = {
            "url": fetch_url,
            "method": "GET",
            "headers": DEFAULT_HEADERS,
            "use_proxy": True,
            "timeout": 3,
            "parse_type": "text",
        }
        response = await self.http_client.crawl_site(**params_dict)
        if response.status == 200:
            # 必须要在处理完数据之后，使用ack方法确认数据已接收
            play_count = await self.get_play_count(song_id)
            await self.pipeline(play_count, response)
            await message.ack()
            return True
        else:
            return False

    @decorator(True)
    async def get_play_count(self, song_id):
        api_url = self.xiami_api.format(song_id=song_id)
        params_dict = {
            "url": api_url,
            "method": "GET",
            "headers": API_HEADERS,
            "use_proxy": True,
            "timeout": 3,
            "parse_type": "json",
        }
        response = await self.http_client.crawl_site(**params_dict)
        res = response.source
        play_count = IterGetDict.dict_get(res, "plays", 0)
        return play_count

    async def pipeline(self, play_count, response):
        # todo 处理数据 + 入库操作
        res = response.source
        upload_data = {}
        song_data_items = self.xpath(res, "//div[@id='sidebar']/div[@class='music_counts']/ul//li")
        song_data_mixin = {
            1: {"play_count": "./em[@id='play_count_num']/text()"},
            2: {"share_count": "./text()"},
            3: {"comment_count": "./a/text()"},
        }
        for index, data_item in enumerate(song_data_items, 1):
            mixin_data = song_data_mixin[index]
            for key, xpath_body in mixin_data.items():
                if key == "play_count":
                    upload_data["play_count"] = play_count
                else:
                    upload_data[key] = self.xpath(data_item, xpath_body)[0]
        song_info_items = self.xpath(res, "//table[@id='albums_info']//tr/td[2]")
        song_info_mixin = {
            1: {"album": "./div/a/text()"},
            2: {"singer": "./div/a/text()"},
            3: {"lyric": "./div/text()"},
            4: {"compose": "./div/text()"},
            5: {"arranger": "./div/text()"},
        }
        for index, info_item in enumerate(song_info_items, 1):
            mixin_info = song_info_mixin[index]
            for key, xpath_body in mixin_info.items():
                upload_data[key] = self.xpath(info_item, xpath_body)[0]
        print(upload_data)


if __name__ == '__main__':
    song_spider = SongDetailSpider()
    asyncio.run(song_spider.fetch())
