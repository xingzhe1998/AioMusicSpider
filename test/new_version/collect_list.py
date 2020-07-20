from multidict import CIMultiDict
import asyncio
import requests
import aiohttp
import json
import re
import hashlib


DEFAULT_HEADERS = CIMultiDict({
    "Accept": "application/json, text/plain, */*",
    "Cookie": "xm_sg_tk=1fb2ab3125452a9f3015b0af157f2b26_1587436018158; xm_sg_tk.sig=_ZEBBptdtWyxHmHOUnORngFjz6p_JRGMDJeuVjAYttQ",
    "Referer": "https://www.xiami.com/list?scene=main&type=collect",
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"),
})


def fetch_index(page):
    url = 'https://www.xiami.com/api/list/collect'
    query = {"dataType": "system", "pagingVO": {"page": page, "pageSize": 30}}
    query = json.dumps(query).replace(' ', '')
    sign = get_sign(query)
    print(sign)
    headers = DEFAULT_HEADERS
    parmas = {
        '_q': query,
        '_s': sign,
    }
    proxy = get_proxy()
    proxies = {'http': proxy, 'https': proxy}
    res = requests.get(url=url, params=parmas, headers=headers, proxies=proxies)
    print(res.json())
    # print(res.headers)


def get_sign(query):
    _url = '/api/list/collect'
    cookie = DEFAULT_HEADERS['cookie']
    xm_sg_tk = re.search(r'xm_sg_tk=(.*?);', cookie).group(1)
    new_parmas = ''.join([xm_sg_tk.split('_')[0], '_xmMain_']) + _url + '_' + query
    print(new_parmas)
    new_parmas = bytes(new_parmas, encoding='utf-8')
    m = hashlib.md5()
    m.update(new_parmas)
    return m.hexdigest()


def get_proxy():
    data = requests.get('proxy-api').json()
    return data['data']


def main():
    for page in range(1, 35):
        fetch_index(page)

if __name__ == '__main__':
    main()
