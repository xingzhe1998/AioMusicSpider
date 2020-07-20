import base64
import requests
import json
import time


record_dict = {
    "request_times": 0,
    "right_user": 0,
    "sign_error": 0,
    "other_error": 0,
    "proxy_error": 0,
}


def timmer(func):
    def wrap(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        cost_time = time.time() - start_time
        record_dict["cost_time"] = cost_time
    return wrap


def get_zmdl_proxy():
    proxy_api = "http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=&city=0&yys=0&port=1&pack=99387&ts=0&ys=0&cs=0&lb=1&sb=0&pb=5&mr=1&regions=&gm=4&username=chukou01&spec=1"
    res = requests.get(proxy_api).json()
    data = res["data"][0]
    proxy = str(data["ip"]) + ":" + str(data["port"])
    return proxy


def get_abyun_proxy():
    proxy_url = "http://H8R4I3H0U025558D:09E9C05215724AE8@http-dyn.abuyun.com:9020"
    return proxy_url


def get_yry_proxy():
    proxy_url = "http://2120051800054601735:j7rLo9pg7xQUgvzA@forward.apeyun.com:9082"
    # proxyServer = "http://forward.apeyun.com:9082"
    # # 代理隧道验证信息
    # proxyUser = "2120051700260820155"
    # proxyPass = "j7rLo9pg7xQUgvzA"
    # proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")
    return proxy_url


def get_mgdl_proxy():
    proxy_api = "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=17dc19e3cb1f434cae13c7da28afc803&count=10&expiryDate=0&format=1&newLine=2"
    res = requests.get(proxy_api).json()
    print(res)
    data = res["msg"]
    return data


def get_kdl_proxy():
    proxy_api = "http://dps.kdlapi.com/api/getdps/?orderid=958980533537219&num=1&pt=1&format=json&sep=1"
    res = requests.get(proxy_api).json()
    proxy = res["data"]["proxy_list"][0]
    proxy = "1632253107:rwy1ruyp@"+proxy
    return proxy


def get_jg_proxy():
    proxy_api = "http://d.jghttp.golangapi.com/getip?num=1&type=2&pro=&city=0&yys=0&port=1&pack=22861&ts=0&ys=0&cs=0&lb=1&sb=0&pb=5&mr=1&regions=&username=chukou01&spec=1"
    res = requests.get(proxy_api).json()
    data = res["data"][0]
    proxy = str(data["ip"]) + ":" + str(data["port"])
    return proxy


def get_zdy_proxy():
    proxy_api = "http://www.zdopen.com/ShortProxy/GetIP/?api=202005181956564944&akey=1702cf27bbea9fdf&count=1&order=2&type=3"
    res = requests.get(proxy_api).json()
    data = res["data"]["proxy_list"][0]
    proxy = str(data["ip"]) + ":" + str(data["port"])
    return proxy


def get_ty_proxy():
    proxy_api = "http://http.tiqu.qingjuhe.cn/getip?num=1&type=2&pack=50107&port=1&lb=1&pb=4&regions=&big_num=1000"
    res = requests.get(proxy_api).json()
    data = res["data"][0]
    proxy = str(data["ip"]) + ":" + str(data["port"])
    return proxy


def get_params():
    api_url = "http://129.204.8.31/api/v1/user_sec_id?count=1"
    res = requests.get(url=api_url).json()
    params_list = res["data"]
    return params_list


@timmer
def fetch_site(url, headers):
    proxy = get_zmdl_proxy()
    record_dict["proxy"] = proxy
    # proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
    proxies = {"http": proxy, "https": proxy}
    record_dict["request_times"] += 1
    try:
        res = requests.get(
            url=url,
            headers=headers,
            proxies=proxies,
            timeout=30
        ).json()
        user_info = res["user"] if "user" in res else ""
        if user_info:
            print(f"请求成功")  # {res}
            record_dict["right_user"] += 1
        elif res["status_code"] == 5:
            print(f"签名错误 {res}")
            record_dict["proxy_error"] += 1
        else:
            print(f"其它错误 {res}")
            record_dict["other_error"] += 1
    except Exception as e:
        print(e)
        # print(f"代理超时 {proxy}")
        record_dict["proxy_error"] += 1


def main():
    # data_list = get_mgdl_proxy()
    # for data in data_list:
    #     proxy = data["ip"] + ":" + data["port"]
    #     record_dict["proxy"] = proxy
    params_list = get_params()
    params_data = params_list[0]
    headers = params_data["headers"]
    url = params_data["url"]
    fetch_site(url=url, headers=headers)
    print(record_dict)
    time.sleep(1)


if __name__ == '__main__':
    test_times = 1000
    for i in range(test_times):
        main()


# 16yun -> {'request_times': 11961, 'proxy_error': 17, 'device_id': '37267595752', 'sign_error': 0, 'right_user': 1771, 'other_error': 10140}
    # rate -> 15%
# ty -> {'request_times': 301, 'right_user': 44, 'sign_error': 0, 'other_error': 250, 'proxy_error': 7, 'proxy': '113.120.35.30:4364', 'cost_time': 1.1200060844421387}
    # rate -> 10%
# zdy -> {'request_times': 100, 'right_user': 16, 'sign_error': 0, 'other_error': 82, 'proxy_error': 2, 'proxy': '123.246.73.90:48521', 'cost_time': 1.8986451625823975}
    # rate -> 16%
# jg -> {'request_times': 157, 'right_user': 17, 'sign_error': 0, 'other_error': 106, 'proxy_error': 34, 'proxy': '220.164.227.54:45621', 'cost_time': 0.47766709327697754}
    # -> 10%
    # between 1-2s
# kdl -> {'request_times': 115, 'right_user': 5, 'sign_error': 0, 'other_error': 110, 'proxy_error': 0, 'proxy': '1632253107:rwy1ruyp@117.90.109.14:21557', 'cost_time': 0.7031176090240479}
    # rate -> 5%
    # between 0.5-1.5s
# mgdl -> {'request_times': 30, 'right_user': 4, 'sign_error': 0, 'other_error': 24, 'proxy_error': 2, 'proxy': '58.19.12.12:40033', 'cost_time': 0.3590366840362549}
    # -> 不合适业务场景
# zmdl -> {'request_times': 1000, 'right_user': 676, 'sign_error': 0, 'other_error': 274, 'proxy_error': 50, 'proxy': '58.218.214.132:8382', 'cost_time': 1.2458841800689697}
    # -> 67.6%
    # between 1-2s
# yry -> {'other_error': 8881, 'request_times': 10000, 'proxy_error': 0, 'right_user': 1086, 'device_id': '35013556610', 'sign_error': 0}
    # rate -> 10%
