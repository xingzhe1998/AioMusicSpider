# -*- coding: utf-8 -*-
'''
@version: old
@name: xyz
@date: 2020-04-23
@description: 抓取某一歌单列表页下所有歌单id以及一些基本信息
'''
import sys
from typing import Dict
from aio_pika import IncomingMessage
sys.path.append("..")
import re
import asyncio
from urllib.parse import quote
from loguru import logger
from common.mixin import HttpClient, BaseCrawl
from util.decorators import decorator


DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,"
              "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
}
PUBLISH_COLLECT_QUEUE_NAME = 'xiami_collect_id_list'
PUBLISH_USER_QUEUE_NAME = 'xiami_user_id_list'

fetch_url = 'https://emumo.xiami.com/search/collect/page/{page}?key={key_word}&order=play_count'
key_word = '民谣'
starts_url = [fetch_url.format(key_word=quote(key_word), page=page) for page in range(1, 6)]

"""fetch = start(..., )(fetch(..., ))

step1:
    start(..., ) -> __start

step2:
    @__start
    def fetch(..., ):
        func body ...

step3:
    __start(fetch(..., )) -> _wrap

fin:
    fetch -> _wrap
"""


class CollectListSpider(BaseCrawl):

    @BaseCrawl.start(init_mongo=False, starts_url=starts_url)
    async def fetch(self, url: str):
        params_dict = {
            "url": url,
            "method": "GET",
            "headers": DEFAULT_HEADERS,
            "use_proxy": True,
            "timeout": 5,
            "parse_type": "text",
        }
        response = await self.http_client.crawl_site(**params_dict)
        if response.status == 200:
            await self.pipeline(response)
            return True
        else:
            return False

    async def pipeline(self, response):
        res = response.source
        items = self.xpath(res, "//div[contains(@class, 'block_list')]/ul//li")
        for item in items:
            collect_info = self.xpath(item, ".//div[@class='block_cover']/a/@href")[0]
            user_info = self.xpath(item, ".//p[@class='collect_info']/span/a/@href")[0]
            collect_id = re.search(r'(\d+)', collect_info).group()
            user_id = re.search(r'(\d+)', user_info).group()
            print(f"collect_id: {collect_id}, user_id: {user_id}")
            await self.rabbitmq_pool.publish(PUBLISH_COLLECT_QUEUE_NAME, {"collect_id": collect_id})
            await self.rabbitmq_pool.publish(PUBLISH_USER_QUEUE_NAME, {"user_id": user_id})


if __name__ == '__main__':
    list_spider = CollectListSpider()
    asyncio.run(list_spider.fetch())

'''
    python_version = sys.version_info
    list_spider = CollectListSpider()
    if python_version >= (3, 7):
        asyncio.run(list_spider.fetch())
    else:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(list_spider.fetch())
        finally:
            loop.close()
'''
