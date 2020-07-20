import redis


redis_key = 'proxy_ip_zset'
# redis_url = "redis://@127.0.0.1:6379/2"

pool = redis.ConnectionPool(host="127.0.0.1", port=6379, password="", db=3)
redis_client = redis.Redis(connection_pool=pool)
redis_client.zadd(redis_key, {"proxy_ip1": 234})
redis_client.zadd(redis_key, {"proxy_ip2": 345})
print(redis_client.zcard(redis_key))
