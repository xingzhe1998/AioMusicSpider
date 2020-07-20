import asyncio
import aioredis


loop = asyncio.get_event_loop()


async def go():
    conn = await aioredis.create_connection(
        ('localhost', 6379), loop=loop)
    await conn.execute('set', 'my-key', 'value')
    val = await conn.execute('get', 'my-key')
    print(val)
    conn.close()
    await conn.wait_closed()
loop.run_until_complete(go())


async def go():
    redis = await aioredis.create_redis(
        ('localhost', 6379), loop=loop)
    await redis.set('my-key', 'value')
    val = await redis.get('my-key')
    print(val)
    redis.close()
    await redis.wait_closed()
loop.run_until_complete(go())


async def go():
    pool = await aioredis.create_pool(
        ('localhost', 6379),
        minsize=5, maxsize=10,
        loop=loop)
    with await pool as redis:    # high-level redis API instance
        await redis.set('my-key', 'value')
        print(await redis.get('my-key'))
    # graceful shutdown
    pool.close()
    await pool.wait_closed()
loop.run_until_complete(go())


"""brief introduction
class Redis:

    _redis = None

    async def get_redis_pool(self, *args, **kwargs):
        if not self._redis:
            self._redis = await aioredis.create_redis_pool(*args, **kwargs)
        return self._redis

    async def close(self):
        if self._redis:
            self._redis.close()
            await self._redis.wait_closed()


async def get_value(key):
    redis = Redis()
    r = await redis.get_redis_pool(('127.0.0.1', 6379), db=7, encoding='utf-8')
    value = await r.get(key)
    print(f'{key!r}: {value!r}')
    await redis.close()

if __name__ == '__main__':
    asyncio.run(get_value('key'))  # need python3.7
"""