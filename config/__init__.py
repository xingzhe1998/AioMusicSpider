# -*- coding: utf-8 -*-
from config.config import config

c = config()
RabbitmqConfig = c.get("rabbitmq")
MongoConfig = c.get("mongo")
SpiderConfig = c.get("spider")
RedisConfig = c.get("redis")
__all__ = ["RabbitmqConfig", "MongoConfig", "SpiderConfig", "RedisConfig"]
