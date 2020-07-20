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


DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,"
              "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
}
PUBLISH_QUEUE_NAME = 'xiami_songs_list'
SUBSCRIBE_QUEUE_NAME = 'xiami_collect_id_list'


class CollectDetailSpider(BaseCrawl):

    fetch_url = 'https://emumo.xiami.com/collect/{collect_id}'

    @BaseCrawl.start(queue_name=SUBSCRIBE_QUEUE_NAME)
    async def fetch(self, data: Dict[str, str], message: IncomingMessage):
        collect_id = data['collect_id']
        fetch_url = self.fetch_url.format(collect_id=collect_id)
        params_dict = {
            "url": fetch_url,
            "method": "GET",
            "headers": DEFAULT_HEADERS,
            "use_proxy": True,
            "timeout": 5,
            "parse_type": "text",
        }
        response = await self.http_client.crawl_site(**params_dict)
        if response.status == 200:
            # 必须要在处理完数据之后，使用ack方法确认数据已接收
            await self.pipeline(collect_id, response)
            await message.ack()
            return True
        else:
            return False

    async def pipeline(self, collect_id, response):
        # todo 处理数据 + 入库操作
        res = response.source
        upload_data = {}
        collect_cover = "https:" + self.xpath(
            res, "//div[@id='info_collect']/div[@class='clearfix']/p/span/a/@href")[0]
        upload_data['collect_cover'] = collect_cover
        collect_title = self.xpath(
            res, "//div[@id='info_collect']/div[@class='clearfix']/div/h2/text()")[0]
        collect_title = re.search(r'(\S+)', collect_title).group()
        upload_data['collect_title'] = collect_title
        collect_intro = self.xpath(res, "//div[@id='info_intro']/div[@class='info_intro_full']/text()")
        if not len(collect_intro):
            collect_intro = '暂无歌单简介'
        upload_data['collect_intro'] = collect_intro
        col_items = self.xpath(res, "//div[@id='info_collect']//div[@class='cdinfo']//li")
        mixin = {
            1: {"producer_name": "./a/text()"},
            2: {"songs_num": "./text()"},
            3: {"collect_tag": ".//a/text()"},
            4: {"update_time": "./text()"},
            5: {"collect_data": "./text()"}
        }
        for index, col_item in enumerate(col_items, 1):
            mixin_body = mixin[index]
            for key, xpath_body in mixin_body.items():
                upload_data[key] = self.xpath(col_item, xpath_body)
        tp = {1: "试听", 2: "分享", 3: "收藏"}
        for k, val in upload_data.items():
            if type(val).__name__ == "list":
                nval = [re.sub(r'[\s, \xa0]', '', v) for v in val]
                nv = [v for v in nval if v]
                if len(val) > 1:
                    if k == "collect_data":
                        val = {tp[ind]: val for ind, val in enumerate(nv, 1)}
                    elif k == "collect_tag":
                        val = nv
                    else:
                        val = ''.join(nv)
                else: val = val[0]
            upload_data[k] = val
        songs_num = upload_data["songs_num"]
        print(upload_data)
        total_page = math.ceil(int(songs_num) / 50)
        for page in range(1, total_page + 1):
            data = {collect_id: page}
            print(data)
            await self.rabbitmq_pool.publish(PUBLISH_QUEUE_NAME, data)
            await asyncio.sleep(0.01)


if __name__ == '__main__':
    list_spider = CollectDetailSpider()
    asyncio.run(list_spider.fetch())
