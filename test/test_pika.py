# -*- coding: utf-8 -*-
from urllib.parse import quote
import pytest
from util import RabbitMqPool
from config import RabbitmqConfig
import msgpack
from collections.abc import Mapping
import asyncio


async def init():
    rabbitmq_pool = RabbitMqPool()
    rabbitmq_config = RabbitmqConfig
    await rabbitmq_pool.init(
        addr=rabbitmq_config["addr"],
        port=rabbitmq_config["port"],
        vhost=rabbitmq_config["vhost"],
        username=rabbitmq_config["username"],
        password=rabbitmq_config["password"],
        max_size=rabbitmq_config["max_size"],
    )
    return rabbitmq_pool


async def callback(msg):
    item = msgpack.unpackb(msg.body, raw=False)
    # `item` -> `dict`
    # 集合查询的时间复杂度小于列表
    # set > dict > list
    results = list()
    if item not in results:
        print("添加",item)
        # filter.add(item)
        results.append(item)
    else:
        print("已经存在",item)
    # 确认消费
    # await msg.ack()


'''rabbitmq 队列不会自动去重，需要借助三方工具'''
async def test_publish():
    rabbitmq_pool = await init()
    key_word = '民谣'
    for page in range(1, 10):
        data = dict()
        data['key'] = quote(key_word)
        data['page'] = str(page)
        await rabbitmq_pool.publish(QUEUE_NAME, data)


'''
1. 不使用ack()方法
    一次请求后结束程序处于暂停阶段，程序终止后，数据重新推回mq队列
2. 当使用ack()方法
    mq队列数据全部推出，程序终止后，mq队列为空
3. 小结
    mq作为消息中间件有确认消息发出/接收的功能，ack()方法就是消费方用来
    向mq发出消息已处理的信号，此时mq才会将队列中对应的消息删除'''
async def test_subscribe():
    rabbitmq_pool = await init()
    await rabbitmq_pool.subscribe(QUEUE_NAME, callback)


if __name__ == '__main__':
    QUEUE_NAME = "xiami_collect_list"
    asyncio.run(test_subscribe())
