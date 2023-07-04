import json
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from utils.apiTools import get

BASE_URL = 'https://api.pionex.com'

def load_config():
    with open('./pionex/config.json', 'r') as f:
        config = json.load(f)
        return config['key'], config['secret']

def get_timestamp():
    return str(int(time.time() * 1000))

def generate_signature(API_SECRET, url, sorted_body):
    # 將sorted_body轉成字串並放在url後面，例如b'GET/api/v1/trade/allOrders?limit=1&symbol=BTC_USDT&timestamp=1655896754515{"symbol": "BTC_USDT"}'
    url = url + json.dumps(dict(sorted_body))
    return hmac.new(API_SECRET.encode('utf-8'), url.encode('utf-8'), hashlib.sha256).hexdigest()

async def get_price(symbol, API_KEY, API_SECRET):
    path_url = '/api/v1/market/trades'
    timestamp = get_timestamp()

    data = {
        "timestamp": timestamp,
        "symbol": symbol + "_USDT",
        "limit": 1
    }

    response = get(data, path_url, API_KEY, API_SECRET)

    if response.status_code == 200 and response.json()['result'] == True:
        return {"code": 200, "data": float(response.json()['data']['trades'][0]['price'])}
    else:
        return {"code": response.status_code, "data": 0}