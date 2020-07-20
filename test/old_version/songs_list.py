import requests
import json

DEFAULT_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://emumo.xiami.com/collect/363133540",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
}
url = 'https://emumo.xiami.com/collect/ajax-get-list?_=1588909083219&id=8406001&p=1&limit=50'
res = requests.get(url=url, headers=DEFAULT_HEADERS).json()
print(res)
