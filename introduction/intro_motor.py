import functools


'''
Motor Mongo基于Pymongo库，可以在Tornado和Asyncio里使用的异步Mongodb库。在Motor-Asyncio中, 
Motor使用`ThreadPoolExecutor`将同步阻塞的`pymongo`请求放在多个线程中，通过`callback`回调来达到异步的效果。
Motor的核心函数: '''
def asynchronize(framework, sync_method, doc=None):
    """Decorate `sync_method` so it accepts a callback or returns a Future.

    The method runs on a thread and calls the callback or resolves
    the Future when the thread completes.

    :Parameters:
     - `motor_class`:       Motor class being created, e.g. MotorClient.
     - `framework`:         An asynchronous framework
     - `sync_method`:       Unbound method of pymongo Collection, Database,
                            MongoClient, etc.
     - `doc`:               Optionally override sync_method's docstring
    """
    @functools.wraps(sync_method)
    def method(self, *args, **kwargs):
        loop = self.get_io_loop()
        callback = kwargs.pop('callback', None)
        future = framework.run_on_executor(loop,
                                           sync_method,
                                           self.delegate,
                                           *args,
                                           **kwargs)

        return framework.future_or_callback(future, callback, loop)

    # This is for the benefit of motor_extensions.py, which needs this info to
    # generate documentation with Sphinx.
    method.is_async_method = True
    name = sync_method.__name__
    method.pymongo_method_name = name
    if doc is not None:
        method.__doc__ = doc

    return method



from motor.motor_asyncio import AsyncIOMotorClient
from util.singleton import Singleton
class MongoPool(AsyncIOMotorClient, Singleton):
    """
    全局mongo连接池
    """
    pass

value = MongoPool()['set_value']
print(value)
