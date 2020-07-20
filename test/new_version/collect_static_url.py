from multidict import CIMultiDict
import asyncio
import requests
import aiohttp
import json
import re
import hashlib


DEFAULT_HEADERS = CIMultiDict({
    "Accept": "application/json, text/plain, */*",
    "Cookie": "xm_sg_tk=5d6900addb98a4cf409ae66a8f035d38_1589250735020; xm_sg_tk.sig=04dDg_DG3Q9hb4BjNc6PaCBm9FAjrwEofChRb4gsuxE",
    "Referer": "https://www.xiami.com/collect/1132898094",
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"),
})


def parse_index():
    bs_url = 'https://www.xiami.com/api/collect/getCollectStaticUrl'
    _q = json.dumps({"listId":1132898094}).replace(' ', '')
    print(_q)
    _s = get_sign(_q)
    print(_s)
    params = {
        '_q': _q,
        '_s': _s
    }
    res = requests.get(url=bs_url, params=params, headers=DEFAULT_HEADERS, verify=False).json()
    print(res)


def get_sign(query):
    _url = '/api/collect/getCollectStaticUrl'
    cookie = DEFAULT_HEADERS['cookie']
    xm_sg_tk = re.search(r'xm_sg_tk=(.*?);', cookie).group(1)
    new_parmas = ''.join([xm_sg_tk.split('_')[0], '_xmMain_']) + _url + '_' + query
    print(new_parmas)
    new_parmas = bytes(new_parmas, encoding='utf-8')
    m = hashlib.md5()
    m.update(new_parmas)
    return m.hexdigest()


if __name__ == '__main__':
    parse_index()
