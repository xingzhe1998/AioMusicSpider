# -*- coding: utf-8 -*-
'''
@version: old
@name: xyz
@date: 2020-04-24
@description: 本脚本作用是将一些爬虫程序之外的模块整合到一起，例如队列入库与消费请求体构建等等，
爬虫程序只负责请求->解析数据->传递数据
'''
import sys
import asyncio
import aiohttp
sys.path.append("..")
from util import aio_retry
from lxml import html
from util import RabbitMqPool, MongoPool, RedisPool
from config import MongoConfig, RabbitmqConfig, SpiderConfig, RedisConfig
from functools import wraps
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union, List, Callable, Type, AsyncIterator, Awaitable, Tuple
from types import TracebackType
from contextvars import ContextVar
import traceback
from loguru import logger
from pydantic import BaseModel
import hashlib
import msgpack
import aioredis
from functools import partial
from util.decorators import decorator


Node = List[str]
run_flag: ContextVar = ContextVar('which function will run in decorator')
run_flag.set(False)

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Response(BaseModel):
    status: int
    source: Any  # 表示任意数据类型<`str`, `dict`, ...>
    headers: Tuple[Tuple[bytes, bytes], ...]


class HttpClient:

    proxy_api = 'http://182.254.163.159:5050/api/v1/proxy/getProxy?proxy_type=proxy_fy&debug=100000&platform=pdd'

    @aio_retry(max=3)
    async def crawl_site(self, **kwargs):
        use_proxy = kwargs.pop("use_proxy", False)
        parse_type = kwargs.pop("parse_type", "text")
        spider_name = kwargs.pop("spider_name", "")
        proxy = await self.get_proxy() if use_proxy else None
        kwargs["proxy"] = proxy
        kwargs["verify_ssl"] = False
        async with aiohttp.ClientSession() as session:
            async with session.request(**kwargs) as response:
                status = response.status
                url = response.url
                logger.info(f"crawl url:{url},status:{status}")
                # 使用headers方法时，若出现key重复的情况时，会将数据覆盖
                headers = response.raw_headers
                if parse_type == "json":
                    if spider_name == "xiami_songs_list_spider":
                        source = await response.json(content_type="text/html; charset=utf-8")
                    else:
                        source = await response.json()
                elif parse_type == "text":
                    source = await response.text()
        source_data = Response(status=status, source=source, headers=headers)
        return source_data

    async def get_proxy(self):
        async with aiohttp.ClientSession() as session:
            async with session.request(method="GET", url=self.proxy_api) as res:
                res = await res.json()
                proxy = 'http://' + res['data']
                logger.info(f"get proxy:{proxy}")
                return proxy


@dataclass
class BaseCrawl:

    session_flag: bool = False
    redis_client: Optional[aioredis.create_redis_pool] = None

    def __post_init__(self):
        self.rabbitmq_pool = RabbitMqPool()
        self.http_client = HttpClient()
        self.spider_config = SpiderConfig
        self.mongo_config = MongoConfig
        self.mongo_pool = MongoPool
        self.rabbitmq_config = RabbitmqConfig
        self.redis_pool = RedisPool
        self.redis_config = RedisConfig

    async def init_all(self, init_rabbit, init_mongo):
        if init_rabbit and self.rabbitmq_pool:
            await self.rabbitmq_pool.init(
                addr=self.rabbitmq_config["addr"],
                port=self.rabbitmq_config["port"],
                vhost=self.rabbitmq_config["vhost"],
                username=self.rabbitmq_config["username"],
                password=self.rabbitmq_config["password"],
                max_size=self.rabbitmq_config["max_size"],
            )
        if init_mongo and self.mongo_pool:
            logger.info("init mongo")
            self.mongo_pool(
                host=self.mongo_config["host"],
                port=self.mongo_config["port"],
                maxPoolSize=self.mongo_config["max_pool_size"],
                minPoolSize=self.mongo_config["min_pool_size"]
            )

    async def init_redis(self):
        loop = asyncio.get_running_loop()
        self.redis_client = self.redis_pool(redis_url=self.redis_config["REDIS_URL"], loop=loop)
        pool = await self.redis_client.create_redis_pool()
        return pool

    @staticmethod
    def xpath(_response: Union[Response, str],
              rule: str,
              _attr: Optional[str] = None) -> Node:

        if isinstance(_response, Response):
            source = _response.source
            root = html.fromstring(source)
        elif isinstance(_response, str):
            source = _response
            root = html.fromstring(source)
        else:
            root = _response

        nodes = root.xpath(rule)
        if _attr:
            if _attr == "text":
                result = [entry.text for entry in nodes]
            else:
                result = [entry.get(_attr) for entry in nodes]
        else:
            result = nodes
        return result

    @staticmethod
    def gen_finger(data: Union[bytes, str]):
        """生成data的md5"""
        if isinstance(data, str):
            data = bytes(data, encoding="utf-8")
        m = hashlib.md5()
        m.update(data)
        return m.hexdigest()

    async def finger_dedup(self, queue_name, callback, msg):
        message = msg.body
        item = msgpack.unpackb(msg.body, raw=False)
        result = await self.__finger_dedup(key=queue_name, item=message, msg=msg)
        if result:
            await getattr(self, callback.__name__)(item, msg)
            # getattr(self, callback.__name__) -> self.fetch
        else:
            logger.info(f"spider task {message} is exists in request-history")

    async def __finger_dedup(self, *, key, item, msg):
        fp = self.gen_finger(item)
        pool = await self.init_redis()
        added = await pool.sadd(key, fp)
        flag = False
        if added == 0:
            # 过滤已经存在的请求
            await msg.ack()
        else:
            flag = True
        await self.redis_client.destroy_redis_pool()
        return flag

    async def fetch_start(self,
                          callback: Callable[..., Awaitable],
                          init_rabbit: bool = True,
                          init_mongo: bool = True,
                          queue_name: Optional[str] = None,
                          starts_url=None) -> None:
        try:
            run_flag.set(True)
            await self.init_all(init_rabbit, init_mongo)
            if starts_url is None:
                next_func = partial(self.finger_dedup, queue_name, callback)
                await self.rabbitmq_pool.subscribe(queue_name, next_func)
            else:
                res_list = [asyncio.ensure_future(getattr(self, callback.__name__)(url)) for url in starts_url]
                tasks = asyncio.wait(res_list)
                await tasks
        except (asyncio.CancelledError, asyncio.TimeoutError) as e:
            logger.error("asyncio cancelle or timeout error")
        except Exception as e:
            logger.error(f"else error:{traceback.format_exc()}")

    @staticmethod
    def start(init_mongo: bool = True,
              init_rabbit: bool = True,
              queue_name: str = None,
              starts_url: List[str] = None):
        # wraps装饰函数来确保原函数在被装饰时不改变自身的函数名及应有属性
        def __start(func):
            @wraps(func)
            async def _wrap(self, *args, **kwargs):
                try:
                    flag = run_flag.get()
                    if not flag:
                        await self.fetch_start(func,
                                               queue_name=queue_name,
                                               init_mongo=init_mongo,
                                               init_rabbit=init_rabbit,
                                               starts_url=starts_url)
                    else:
                        await func(self, *args, **kwargs)
                except asyncio.CancelledError as e:
                    logger.error(e.args)

            return _wrap

        return __start
