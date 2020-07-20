# -*- coding: utf-8 -*-
'''
@version: old
@name: xyz
@date: 2020-04-23
@description: 将某一分类下的所有歌单页面手动推入rabbitmq，提供给index爬虫
'''
import sys
sys.path.append("..")
import asyncio
import msgpack
from urllib.parse import quote
from util import RabbitMqPool
from config import RabbitmqConfig
from dataclasses import dataclass
from collections.abc import Mapping
from util.decorators import decorator


class StartFetch:

    # todo 后续将初始化步骤移植到公共类
    def __init__(self, QUEUE_NAME):
        self.rabbitmq_pool = RabbitMqPool()
        self.rabbitmq_config = RabbitmqConfig
        self.QUEUE_NAME = QUEUE_NAME

    # todo 后续将初始化步骤移植到公共类
    async def init(self):
        await self.rabbitmq_pool.init(
            addr=self.rabbitmq_config["addr"],
            port=self.rabbitmq_config["port"],
            vhost=self.rabbitmq_config["vhost"],
            username=self.rabbitmq_config["username"],
            password=self.rabbitmq_config["password"],
            max_size=self.rabbitmq_config["max_size"],
        )
        return self.rabbitmq_pool

    # todo 后续将初始化步骤移植到公共类
    @decorator(True)
    async def add_task(self):
        rabbitmq_pool = await self.init()
        key_word = '民谣'
        for page in range(1, 6):
            data = dict()
            data['key'] = quote(key_word)
            data['page'] = str(page)
            await rabbitmq_pool.publish(self.QUEUE_NAME, data)


"""该方法已整合至`xiami_collect_list_spider`脚本"""
if __name__ == '__main__':
    QUEUE_NAME = 'xiami_collect_list'
    stf = StartFetch(QUEUE_NAME)
    asyncio.run(stf.add_task())
