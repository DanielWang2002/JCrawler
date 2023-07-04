import hashlib
import json
import hmac
import time
from urllib.parse import urlencode
import requests

BASE_URL = 'https://api.pionex.com'

def get_timestamp():
    return str(int(time.time() * 1000))

def generate_signature(API_SECRET, url, sorted_body, method):

    # POST需要將sorted_body轉成字串並放在url後面，例如b'GET/api/v1/trade/allOrders?limit=1&symbol=BTC_USDT&timestamp=1655896754515{"symbol": "BTC_USDT"}'
    if method == "POST": url = url + json.dumps(dict(sorted_body))

    return hmac.new(API_SECRET.encode('utf-8'), url.encode('utf-8'), hashlib.sha256).hexdigest()

def get_datetime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def datetime_to_string(datetime):
    return datetime.replace("-", "").replace(" ", "").replace(":", "")

def post(body, path_url, API_KEY, API_SECRET):
    method = 'POST'

    query_string = urlencode(sorted(body.items()))
    url = method + path_url + "?" + query_string

    signature = generate_signature(API_SECRET, url, body, method)

    headers = {
        'PIONEX-KEY': API_KEY,
        'PIONEX-SIGNATURE': signature,
    }
    # print(f"post in apiTools.py: {url}")

    return requests.post(BASE_URL + path_url + "?" + query_string, headers=headers, json=body)

def get(body, path_url, API_KEY, API_SECRET):
    method = 'GET'

    query_string = urlencode(sorted(body.items()))
    url = method + path_url + "?" + query_string

    signature = generate_signature(API_SECRET, url, body, method)

    headers = {
        'PIONEX-KEY': API_KEY,
        'PIONEX-SIGNATURE': signature,
    }

    return requests.get(BASE_URL + path_url + "?" + query_string, headers=headers)