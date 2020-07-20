import time


def singleton(cls, *args, **kw):
    instances = {}
    def wrapper():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return wrapper


@singleton
class Animal(object):
    def __init__(self):
        pass


animal1 = Animal()
animal2 = Animal()
print(id(animal1))
print(id(animal2))






'''测试python元类机制'''
class MyMeta(type):

    def __new__(cls, *args, **kwargs):  # cls -> MyMeta
        print('===>MyMeta.__new__')
        print(cls.__name__)
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, classname, superclasses, attributedict):  # self -> Foo
        super().__init__(classname, superclasses, attributedict)
        print('===>MyMeta.__init__')
        print(self.__name__)
        print(attributedict)
        print(self.tag)

    def __call__(self, *args, **kwargs):  # self -> Foo
        print('===>MyMeta.__call__')
        obj = self.__new__(self, *args, **kwargs)
        self.__init__(self, *args, **kwargs)
        return obj


class Foo(object, metaclass=MyMeta):

    tag = '!Foo'

    def __new__(cls, *args, **kwargs):
        print('===>Foo.__new__')
        return super().__new__(cls)

    def __init__(self, name):
        print('===>Foo.__init__')
        self.name = name


print('test start')
foo = Foo('test')
print('test end')




import asyncio
from config import MongoConfig
from motor.motor_asyncio import AsyncIOMotorClient
# from util.singleton import Singleton
from loguru import logger as storage
from pymongo import UpdateOne

db_configs = {
    'host': '127.0.0.1',
    'port': '27017',
    'db_name': 'aio_spider_data',
    'user': ''
}


class SingletonMetaclass(type):  # SingletonMetaclass -> type
    """单例元类"""

    _instances = {}

    def __call__(cls, *args: tuple, **kwargs: dict):
        """调用 魔术方法"""
        instances = cls._instances

        if cls not in instances:
            instances[cls] = super(SingletonMetaclass, cls).__call__(*args, **kwargs)

        # 返回唯一实例
        return instances[cls]


class Singleton(metaclass=SingletonMetaclass):  # Singleton -> object
    """单例基类
    所有继承此类的类都将成为单例类，在本次项目
    运行的全部周期中成为唯一的单一实例。
    """
    pass


class MongoPool(AsyncIOMotorClient, Singleton):
    """全局mongo连接池"""
    pass


mongo_pool = MongoPool
mongo_config = MongoConfig
mongo_pool(
    host=mongo_config["host"],
    port=mongo_config["port"],
    maxPoolSize=mongo_config["max_pool_size"],
    minPoolSize=mongo_config["min_pool_size"]
                )
