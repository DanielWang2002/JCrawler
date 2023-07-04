import json
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from utils.apiTools import get

BASE_URL = 'https://api.pionex.com'

def get_timestamp():
    return str(int(time.time() * 1000))

def generate_signature(API_SECRET, url, sorted_body):
    # 將sorted_body轉成字串並放在url後面，例如b'GET/api/v1/trade/allOrders?limit=1&symbol=BTC_USDT&timestamp=1655896754515{"symbol": "BTC_USDT"}'
    url = url + json.dumps(dict(sorted_body))
    return hmac.new(API_SECRET.encode('utf-8'), url.encode('utf-8'), hashlib.sha256).hexdigest()

async def get_precesion(symbol, API_KEY, API_SECRET):
    path_url = '/api/v1/common/symbols'
    timestamp = get_timestamp()

    data = {
        "timestamp": timestamp,
        "symbols": symbol + "_USDT"
    }

    response = get(data, path_url, API_KEY, API_SECRET)

    if response.status_code == 200 and response.json()['result'] == True:
        return {"code": 200, "data": int(response.json()['data']['symbols'][0]['basePrecision'])}
    else:
        return {"code": response.status_code, "data": 0}
    
async def get_min_trade_size(symbol, API_KEY, API_SECRET):
    path_url = '/api/v1/common/symbols'
    timestamp = get_timestamp()
    
    data = {
        "timestamp": timestamp,
        "symbols": symbol + "_USDT"
    }

    response = get(data, path_url, API_KEY, API_SECRET)

    if response.status_code == 200 and response.json()['result'] == True:
        return {"code": 200, "data": (response.json()['data']['symbols'][0]['minTradeSize'])}
    else:
        return {"code": response.status_code, "data": response.json()}