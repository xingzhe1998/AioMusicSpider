# -*- coding: utf-8 -*-
import aio_pika
from typing import Callable, Dict
from logging import getLogger, WARNING
from aio_pika import connect_robust, Channel, pool, IncomingMessage, Message
from util.singleton import Singleton
from util.decorators import decorator
import msgpack
from config import SpiderConfig
from dataclasses import dataclass
from loguru import logger

# 消费并发量为5
CONCURRENCY_NUM = SpiderConfig.get("CONCURRENCY_NUM")


@dataclass
class RabbitMqPool(Singleton):

    _url: str = None
    _max_size: int = None
    _connection_pool: pool.Pool = None
    _channel_pool: pool.Pool = None

    def __post_init__(self):
        self._logger = getLogger()
        disable_aiopika_logger()

    async def init(self,
                   addr: str,
                   port: str,
                   vhost: str,
                   username: str,
                   password: str,
                   max_size: int):
        self._size = max_size
        self._url = f"amqp://{username}:{password}@{addr}:{port}/{vhost}"
        self._connection_pool = pool.Pool(
            self._get_connection, max_size=self._size)
        self._channel_pool = pool.Pool(self._get_channel, max_size=max_size)
        self._logger.debug(
            "Create rabbitmq connection pool success at %s:%s, max_size %s", addr, port, max_size)
        return self

    async def _get_connection(self) -> None:
        return await connect_robust(self._url)

    async def _get_channel(self) -> Channel:
        async with self._connection_pool.acquire() as connection:
            return await connection.channel()

    @decorator(True)
    async def subscribe(self,
                        queue_name: str,
                        callback: Callable[[IncomingMessage], None]) -> None:
        """消费数据"""
        async with self._channel_pool.acquire() as channel:
            await channel.set_qos(CONCURRENCY_NUM)
            queue = await channel.declare_queue(
                name=queue_name, passive=True
            )
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    """callback 
                        tp1 -> functools.partial object
                        tp2 -> function object"""
                    await callback(message)

    async def publish(self,
                      queue_name: str,
                      msg: Dict[str, str]) -> None:
        """数据入库"""
        task = msgpack.packb(msg)
        async with self._channel_pool.acquire() as channel:
            # 创建队列
            await channel.declare_queue(queue_name)
            # queue_name -> routing_key
            await channel.default_exchange.publish(
                Message(task), queue_name)


def disable_aiopika_logger():
    """
    禁用 aio-pika 的日志
    调用此函数之后可以屏蔽掉 aio-pika ``WARNING`` 等级以下的日志输出"""
    loggers = (
        aio_pika.channel.log,
        aio_pika.robust_channel.log,

        aio_pika.connection.log,
        aio_pika.robust_connection.log,

        aio_pika.exchange.log,
        aio_pika.robust_exchange.log,

        aio_pika.queue.log,
        aio_pika.robust_queue.log,

        aio_pika.pool.log,
        aio_pika.message.log,
        aio_pika.patterns.rpc.log,
        aio_pika.patterns.master.log,
    )
    for logger in loggers:
        logger.setLevel(WARNING)
