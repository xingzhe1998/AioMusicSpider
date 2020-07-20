import time
import asyncio
import requests
import json
import re
from multidict import CIMultiDict
import sys
sys.path.append('..')
from common.mixin import BaseCrawl
from util.params_encrypt import ParamsEncrypt


PUBLISH_QUEUE_NAME = "xiami_cookie_list"
URL = 'https://www.xiami.com/api/collect/getRecommendTags'
QUERY = {"recommend": 1}
DEFAULT_HEADERS = CIMultiDict({
    "Accept": "application/json, text/plain, */*",
    "Cookie": "xm_sg_tk=0ef69d42c9a51cd08a6ec06ebabb0ee0_1589552865600; xm_sg_tk.sig=N6KMwY-QNG5ca1SuDZ-TGU70QXYwLrwB-zgsfgs5hVM;",
    "Referer": "https://www.xiami.com/list?scene=main&type=collect",
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"),
})


class GenXMCookie(BaseCrawl):

    def build_params(self, url):
        query = json.dumps(QUERY).replace(' ', '')
        _url = re.search(r"com(.*)", url).group(1)
        xm_sg_tk = re.search(r'xm_sg_tk=(.*?);', DEFAULT_HEADERS["cookie"]).group(1)
        prefix_params = {
            "query": query,
            "_url": _url,
            "xm_sg_tk": xm_sg_tk,
        }
        sign = ParamsEncrypt.get_sign(**prefix_params)
        params = {
            '_q': query,
            '_s': sign,
        }
        headers = DEFAULT_HEADERS
        fetch_params = {
            "url": url,
            "headers": headers,
            "params": params,
        }
        return fetch_params

    @BaseCrawl.start(init_mongo=False, starts_url=[URL])
    async def update_cookie(self, url):
        fetch_params = self.build_params(url)
        params_dict = {
            **fetch_params,
            "method": "GET",
            "use_proxy": False,
            "timeout": 3,
            "parse_type": "json",
        }
        response = await self.http_client.crawl_site(**params_dict)
        source = response.source
        raw_headers = response.headers
        # 令牌过期
        if source["code"] == "SG_TOKEN_EXPIRED":
            cookie = self.build_cookie(raw_headers=raw_headers)
            print(f"generate new cookie: {cookie}")
        # 参数正确
        else:
            cookie = DEFAULT_HEADERS['cookie']
            print(f"use old cookie: {cookie}")
        await self.rabbitmq_pool.publish(PUBLISH_QUEUE_NAME, {"cookie": cookie, "update_time": int(time.time())})

    @staticmethod
    def build_cookie(raw_headers):
        xst = "xm_sg_tk"
        xsts = "xm_sg_tk.sig"
        xm_sg_tk = ""
        xm_sg_tk_sig = ""
        for tuple_field in raw_headers:
            tup_key = tuple_field[0].decode().lower()
            tup_val = tuple_field[1].decode()
            if tup_key == "set-cookie":
                # 注意先后顺序，必须是xsts在第一位置
                if xsts in tup_val:
                    xm_sg_tk_sig = xsts + "=" + re.search(f"{xsts}=(.*?);", tup_val).group(1)
                elif xst in tup_val:
                    xm_sg_tk = xst + "=" + re.search(f"{xst}=(.*?);", tup_val).group(1)
        cookie = xm_sg_tk + "; " + xm_sg_tk_sig
        return cookie

    @staticmethod
    def get_proxy():
        data = requests.get('proxy-api').json()
        return data['data']


if __name__ == '__main__':
    crawler = GenXMCookie()
    asyncio.run(crawler.update_cookie())
