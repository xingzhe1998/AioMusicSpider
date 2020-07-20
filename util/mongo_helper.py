from motor.motor_asyncio import AsyncIOMotorClient
from util.singleton import Singleton
import asyncio
from loguru import logger as storage
from pymongo import UpdateOne

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

db_configs = {
    'host': '127.0.0.1',
    'port': '27017',
    'db_name': 'aio_spider_data',
    'user': ''
}


class MongoPool(AsyncIOMotorClient, Singleton):
    """
    全局mongo连接池
    """
    pass


class MotorOperation:

    def __init__(self):
        self.__dict__.update(**db_configs)

    async def add_index(self, col="xiami_collect_detail_data"):
        # 添加索引
        mb = self.get_db()
        await mb[col].create_index('url')

    async def save_data(self, pool, items, col="xiami_collect_detail_data", key="obj_id"):
        '''
        :param pool: MongoPool类的实例对象
        :param items: 要插入mongo的数据
        :param col: 相当于关系型数据库里的table
        :param key: item.get(key) -> 主键
        :return: None
        '''
        mb = pool()[self.db_name]  # 继承类MongoPool，指定数据库名
        if isinstance(items, list):
            requests = list()
            r_a = requests.append
            for item in items:
                try:
                    r_a(UpdateOne({
                        key: item.get(key)},
                        {'$set': item},
                        upsert=True))
                except Exception as e:
                    storage.error(f"数据插入出错:{e.args}此时的item是:{item}")
            # bulk_write -> Send a batch of `write operations` to the server
            result = await mb[col].bulk_write(requests, ordered=False, bypass_document_validation=True)
            storage.info(f"modified_count:{result.modified_count}")
        elif isinstance(items, dict):
            try:
                # update_one -> Update a single document matching the filter
                await mb[col].update_one({
                    key: items.get(key)},
                    {'$set': items},
                    upsert=True)
            except Exception as e:
                storage.error(f"数据插入出错:{e.args}此时的item是:{items}")

    async def find_data(self, pool, col="xiami_collect_detail_data"):
        mb = pool()[self.db_name]
        cursor = mb[col].find({'status': 0}, {"_id": 0})
        async for item in cursor:
            yield item

    async def do_delete_many(self, pool):
        mb = pool()[self.db_name]
        await mb.discogs_details_data.delete_many({"flag": 0})


'''
db_configs = {
    'host': '127.0.0.1',
    'port': '27017',
    'db_name': 'aio_spider_data',
    'user': ''
}

self.db_name -> 
    def __init__(self) -> 
        self.__dict__.update(**db_configs) ->
            db_configs['db_name']
'''
