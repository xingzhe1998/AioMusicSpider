# encoding=utf-8 飞蚁代理
'''fy代理池1 proxy_ip_hash_fy 供前台访问'''
import sys, time, json, redis, datetime
import requests
sys.path.append("..")
from util.decorators import decorator


class CommonProxyServiceFy:

    def __init__(self):
        self.max_frequency = 25
        self.push_times = 5
        self.proxy_url = "http://112.17.250.28:88/open?user_name=hys_92418531_9dd1&timestamp=1565854349852" \
                         "&md5=C58101FAFFE2A5D634852DC40D672D32&pattern=json&fmt=1&number={}"
        self.pool = redis.ConnectionPool(host='172.16.0.27', port='6379', db=10, password='20A3NBVJnWZtNzxumYOz')
        self.redis_client = redis.Redis(connection_pool=self.pool)
        self.fy_proxy_list = 'proxy_ip_list_fy_advanced'
        self.fy_proxy_zset = 'proxy_ip_zset_fy_advanced'
        self.proxy_start_count = self.redis_client.llen(self.fy_proxy_list)
        self.today = datetime.date.today()
        self.start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.get_proxy_count = 0

    def qps_analysis(self, proxy_end_count):
        proxy_count_diff = self.proxy_start_count + self.get_proxy_count - proxy_end_count
        qps = int(proxy_count_diff / 12)
        self.redis_client.setex('proxy_qps', 70, qps)

    def get_proxy_rate(self):
        proxy_qps = self.redis_client.get('proxy_qps')
        if not proxy_qps:
            return 120
        return int((int(proxy_qps) / 1.1))

    def check_proxy_valid(self):
        # 可能有bug
        life_time = 40 if (str(self.today) + ' 07:00:00') > self.start_time > (str(self.today) + ' 18:00:00') else 25
        now = int(time.time())
        # 删除距离当前时间25s之外的代理ip
        self.redis_client.zremrangebyscore(self.fy_proxy_zset, 0, now-life_time)

    @decorator(True)
    def get_fy_proxy(self, count):
        url = self.proxy_url.format(count)
        res = requests.get(url=url).json()
        print(self.start_time, res, url)
        status = res['code']
        if status == 100:
            host = str(res['domain'])
            data_list = res['data']
            for data in data_list:
                port = str(data['port'])
                proxy_ip = host + ':' + port
                data = {
                    'proxy': proxy_ip,
                    'time': int(time.time()),
                    'last_used_time': '',
                    'province': data['province'],
                    'city': data['city']
                }
                # 推送5次
                [self.redis_client.lpush(self.fy_proxy_list, proxy_ip) for i in range(self.push_times)]
                # 源码中字典value作为zset的score进行排名
                self.redis_client.zadd(self.fy_proxy_zset, {json.dumps(data): int(time.time())})
                left_ip = res['left_ip']
                self.redis_client.set(
                    'proxy_fy', json.dumps({"left_ip": left_ip, "last_update_time": int(time.time())}))
        # todo 预警机制
        else:
            return None

    # 激活是指定时任务启动该脚本时
    def main(self):
        self.check_proxy_valid()
        # 第一、二次激活(时/期间)，集合数据小于400，
        # 说明代理使用时间过长，故清除`fy_proxy_list`
        # 整体运行结果就是一分钟刷新一次`fy_proxy_list`
        if self.redis_client.zcard(self.fy_proxy_zset) < 400:
            self.redis_client.delete(self.fy_proxy_list)
            self.get_fy_proxy(120)
        # 第一次激活、第二次运行时，redis队列数据过多，添加冷却
        elif self.redis_client.llen(self.fy_proxy_list) > self.get_proxy_rate()*2 and self.redis_client.zcard(self.fy_proxy_zset) > 120:
            time.sleep(2.3)
        # 理解为第二次激活时
        else:
            # count随着代理使用的qps的增加而增加，最多到500
            count = 150 if self.redis_client.llen(self.fy_proxy_list) < 100 and self.get_proxy_rate() < 150 else self.get_proxy_rate()
            count = count if count < 500 else 500
            # 保持zset里面有120个可用的ip
            self.get_fy_proxy(count)
            self.get_proxy_count += count * 2
            time.sleep(2.3)

    def finally_exec(self):
        proxy_end_count = self.redis_client.llen(self.fy_proxy_list)
        print(proxy_end_count)
        self.qps_analysis(proxy_end_count)


if __name__ == '__main__':
    # */1 * * * *
    comm = CommonProxyServiceFy()
    for i in range(comm.max_frequency):
        comm.main()
    comm.finally_exec()
    # 25 * 2.3 < 60 -> 随眠时间不到一分钟


# redis_client = redis.Redis(host='172.16.0.27', port='6379', db=10, password='20A3NBVJnWZtNzxumYOz')
# proxy_hash_name = 'proxy_ip_list_fy_advanced'
# proxy_ip_zset_fy_advanced = 'proxy_ip_zset_fy_advanced'
# today = datetime.date.today()
# start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
# last_proxy_count = redis_client.llen(proxy_hash_name)
# get_proxy_count = 0


# # 计算代理使用的QPS
# def qps_analysis():
#     proxy_count_diff = last_proxy_count + get_proxy_count - redis_client.llen(proxy_hash_name)
#     qps = int(proxy_count_diff / 12)
#     redis_client.setex('proxy_qps', 70, qps)
#
#
# def get_proxy_rate():
#     proxy_qps = redis_client.get('proxy_qps')
#     if not proxy_qps:
#         return 120
#     return int((int(proxy_qps) / 1.1))
#
#
# # 清理过期ip
# def check_proxy_valid():
#     life_time = 40 if (str(today) + ' 07:00:00') > start_time > (str(today) + ' 18:00:00') else 25
#     redis_client.zremrangebyscore(proxy_ip_zset_fy_advanced, 0, int(time.time()) - life_time)
#
#
# def get_fy_proxy(count):
#     url = 'http://112.17.250.28:88/open?user_name=hys_92418531_9dd1&timestamp=1565854349852&md5' \
#           '=C58101FAFFE2A5D634852DC40D672D32&pattern=json&fmt=1&number=' + str(count)
#     req = request.Request(url)
#     res = request.urlopen(req)
#     res = res.read()
#     res = json.loads(res.decode('utf-8'))
#     print(now_time, res, url)
#     if res['code'] == 100:
#         ip = res['domain']
#         for proxy in res['data']:
#             proxy_ip = ip + ':' + str(proxy['port'])
#             data = {
#                 'proxy': proxy_ip,
#                 'time': int(time.time()),
#                 'last_used_time': '',
#                 'province': proxy['province'],
#                 'city': proxy['city']
#             }
#             redis_client.lpush(proxy_hash_name, proxy_ip)
#             redis_client.lpush(proxy_hash_name, proxy_ip)
#             redis_client.lpush(proxy_hash_name, proxy_ip)
#             redis_client.lpush(proxy_hash_name, proxy_ip)
#             redis_client.lpush(proxy_hash_name, proxy_ip)
#             redis_client.zadd(proxy_ip_zset_fy_advanced, {json.dumps(data): int(time.time())})
#             left_ip = res['left_ip']
#             redis_client.set('proxy_fy', json.dumps({"left_ip": left_ip, "last_update_time": int(time.time())}))
#
#
# for i in range(25):
#     check_proxy_valid()
#     now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#     if redis_client.zcard(proxy_ip_zset_fy_advanced) < 400:
#         redis_client.delete(proxy_hash_name)
#         get_fy_proxy(120)
#     elif redis_client.llen(proxy_hash_name) > get_proxy_rate()*2 and redis_client.zcard(proxy_ip_zset_fy_advanced) > 120:
#         time.sleep(2.3)
#     else:
#         count = 150 if redis_client.llen(proxy_hash_name) < 100 and get_proxy_rate() < 150 else get_proxy_rate()
#         count = count if count < 500 else 500
#         # if redis_client.llen(proxy_hash_name) < 100:
#         #     count = 150
#         # 保持zset里面有120个可用的ip
#         get_fy_proxy(count)
#         get_proxy_count += count * 2
#         time.sleep(2.3)
#
#
# next_proxy_count = redis_client.llen(proxy_hash_name)
# qps_analysis()
