from multidict import CIMultiDict
import asyncio
import requests
import aiohttp
import json
import re
import hashlib


DEFAULT_HEADERS = CIMultiDict({
    "Accept": "application/json, text/plain, */*",
    "Cookie": "xm_sg_tk=0ef69d42c9a51cd08a6ec06ebabb0ee0_1589552865600; xm_sg_tk.sig=N6KMwY-QNG5ca1SuDZ-TGU70QXYwLrwB-zgsfgs5hVM;",
    "Referer": "https://www.xiami.com/list?scene=main&type=collect",
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"),
})

def fetch_index():
    url = 'https://www.xiami.com/api/collect/getRecommendTags'
    query = {"recommend": 1}
    query = json.dumps(query).replace(' ', '')
    sign = get_sign(query)
    print(sign)
    # headers = DEFAULT_HEADERS
    # parmas = {
    #     '_q': query,
    #     '_s': sign,
    # }
    # proxy = get_proxy()
    # proxies = {'http': proxy, 'https': proxy}
    # res = requests.get(url=url, params=parmas, headers=headers, proxies=proxies)
    # response_headers = res.headers
    # set_cookie = response_headers['set-cookie']
    # source_data = res.json()
    # print(source_data)
    # if source_data['code'] != 'SUCCESS':
    #     cookie = update_cookie(set_cookie)
    #     print(cookie)
    #     DEFAULT_HEADERS['Cookie'] = cookie
    #     print(DEFAULT_HEADERS)
    #     return fetch_index()
    # else:
    #     with open('XiamiMusicCate', 'w+', encoding='utf-8') as fp:
    #         fp.write(json.dumps(source_data, ensure_ascii=False))

def update_cookie(set_cookie):
    data_list = set_cookie.split(';')
    cookier = {data.split('=')[0].lstrip(' '): data.split('=')[1] for data in data_list if len(data.split('=')) == 2}
    xm_sg_tk = cookier['httponly, xm_sg_tk']
    xm_sg_tk_sig = cookier['secure, xm_sg_tk.sig']
    cookie = 'xm_sg_tk=' + xm_sg_tk + '; ' + 'xm_sg_tk.sig=' + xm_sg_tk_sig
    return cookie

def get_sign(query):
    _url = '/api/collect/getRecommendTags'
    cookie = DEFAULT_HEADERS['cookie']
    xm_sg_tk = re.search(r'xm_sg_tk=(.*?);', cookie).group(1)
    new_parmas = ''.join([xm_sg_tk.split('_')[0], '_xmMain_']) + _url + '_' + query
    print(new_parmas, query, xm_sg_tk)
    new_parmas = bytes(new_parmas, encoding='utf-8')
    m = hashlib.md5()
    m.update(new_parmas)
    return m.hexdigest()

def get_proxy():
    data = requests.get('proxy-api').json()
    return data['data']


if __name__ == '__main__':
    fetch_index()

'''
1. 去除xm_sg_tk.sig -> {'code': 'SG_TOKEN_EMPTY', 'msg': '令牌为空'}
2. xm_sg_tk与xm_sg_tk.sig必须成对出现，同时更新

{
    "Date": "Mon, 20 Apr 2020 08:28:57 GMT",
    "Content-Type": "text/html; charset=utf-8",
    "Transfer-Encoding": "chunked",
    "Connection": "keep-alive",
    "Vary": "Accept-Encoding, Origin",
    "x-server-id": "d13efb081692434771eeb81362c88ff7b4ee09a8d4600af6d54b2f265097c0a52cf1c5e237654db40e2d64673c9cedab",
    "set-cookie": "_xm_cf_=qp_PcE9WddJxDvc02EuprinF; path=/; secure, xmgid=79ca59ce-7e68-49fe-b6d9-36652d23d2bd; path=/; expires=Thu, 20 Apr 2023 08:28:57 GMT; domain=.test.com; httponly, xm_sg_tk=76014e20b9979e2209afa9584cbe0e7a_1587371337480; path=/; expires=Wed, 22 Apr 2020 08:28:57 GMT; domain=.test.com; secure, xm_sg_tk.sig=f8QYxT8-LikXZ8I2Ldy1kBagx6PHcQhZqTPyFhgdhY0; path=/; expires=Wed, 22 Apr 2020 08:28:57 GMT; domain=.test.com; secure, xm_traceid=0b52068f15873713374744083eef39; path=/; expires=Mon, 20 Apr 2020 09:28:57 GMT; domain=.test.com; secure, xm_oauth_state=fb88e6004b6e5ebe1b6740aa981e057b; path=/; expires=Mon, 20 Apr 2020 09:28:57 GMT; domain=.test.com; secure; httponly",
    "x-frame-options": "SAMEORIGIN",
    "x-xss-protection": "1; mode=block",
    "x-content-type-options": "nosniff",
    "x-download-options": "noopen",
    "strict-transport-security": "max-age=31536000, max-age=31536000",
    "x-readtime": "274",
    "Content-Encoding": "gzip",
    "Server": "Tengine/Aserver",
    "EagleEye-TraceId": "0b52068f15873713374744083eef39",
    "Timing-Allow-Origin": "*"
}
'''
