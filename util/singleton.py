# -*- coding: utf-8 -*-


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
