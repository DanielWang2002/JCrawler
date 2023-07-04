import json
import time
import hmac
import hashlib
import pandas as pd
import math
import asyncio
from asyncio import sleep
from urllib.parse import urlencode
from utils.jc_utils import logger
from utils.apiTools import post, get
from .account import get_balance
from .market import get_price
from .common import get_min_trade_size

BASE_URL = 'https://api.pionex.com'

def get_timestamp():
    return str(int(time.time() * 1000))

def generate_signature(API_SECRET, url, sorted_body, method):

    # POST需要將sorted_body轉成字串並放在url後面，例如b'GET/api/v1/trade/allOrders?limit=1&symbol=BTC_USDT&timestamp=1655896754515{"symbol": "BTC_USDT"}'
    if method == "POST": url = url + json.dumps(dict(sorted_body))

    return hmac.new(API_SECRET.encode('utf-8'), url.encode('utf-8'), hashlib.sha256).hexdigest()

def sort_body(body):
    return sorted(body.items(), key=lambda item: item[0])

def get_query_string(sorted_body):
    return "&".join(["{}={}".format(k, v) for k, v in sorted_body])

def get_datetime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def datetime_to_string(datetime):
    return datetime.replace("-", "").replace(" ", "").replace(":", "")

def timestamp_to_datetime(timestamp):
    # 傳入timestamp(ms)，回傳datetime
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000))

async def get_fills(symbol, order_id, API_KEY, API_SECRET):
    path_url = '/api/v1/trade/fillsByOrderId'
    timestamp = get_timestamp()

    data = {
        "timestamp": timestamp,
        "symbol": symbol + "_USDT",
        "orderId": order_id
    }
    
    response = get(data, path_url, API_KEY, API_SECRET)

    if response.status_code == 200 and response.json()['result'] == True:
        return {"code": 200, "data": response.json()}
    else:
        return {"code": response.status_code, "data": 0}
    
# 儲存下單記錄到csv，主要是供Sell時能知道當初買了多少幣
async def save_order(data):
    df = pd.read_csv('./record.csv')
    new_data = pd.DataFrame(data, index=[0])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv('./record.csv', index=False)
    logger("下單記錄已儲存\n" + str(data))

async def buy(signal, symbol, API_KEY, API_SECRET, order_amount):
    path_url = '/api/v1/trade/order'
    timestamp = get_timestamp()

    body = {
        "clientOrderId": datetime_to_string(get_datetime())
        + signal[symbol]['strategy']
        + symbol
        + signal[symbol]['action'][0],
        "symbol": symbol + "_USDT",
        "side": signal[symbol]['action'].upper(),
        "type": "MARKET",
        "amount": order_amount,
        "timestamp": timestamp
    }

    response = post(body, path_url, API_KEY, API_SECRET)

    if response.status_code == 200 and response.json()['result'] == True:
        logger(f"{symbol} 購買成功")

        await asyncio.sleep(1)

        order_id = response.json()['data']['orderId']
        await handel_order_success(order_id, symbol, signal, API_KEY, API_SECRET)
        
    else:
        logger(f"{symbol} 購買失敗\n" + response.text)

async def sell(signal, symbol, API_KEY, API_SECRET):
    df = pd.read_csv('./record.csv')
    try:
        # 找到指定symbol的資料的最後一筆
        df = df[df['symbol'] == (symbol + "_USDT")].tail(1)
        size = df['size'].values[0]
        min_trade_size = await get_min_trade_size(symbol, API_KEY, API_SECRET)
        decimal_places = len(min_trade_size['data'].split(".")[1])
        size = float(size) - float(min_trade_size['data'])
        size = f"{adjust_trade_size(size, decimal_places):.{decimal_places}f}"
    except Exception as e:
        print(f"售出時發生錯誤\n{e}")
        return 0
    
    path_url = '/api/v1/trade/order'
    timestamp = get_timestamp()

    body = {
        "clientOrderId": datetime_to_string(get_datetime())
        + signal[symbol]['strategy']
        + symbol
        + signal[symbol]['action'][0],
        "symbol": symbol + "_USDT",
        "side": signal[symbol]['action'].upper(),
        "type": "MARKET",
        "size": size,
        "timestamp": timestamp
    }

    response = post(body, path_url, API_KEY, API_SECRET)

    if response.status_code == 200 and response.json()['result'] == True:
        logger(f"{symbol} 售出成功")
        
        await asyncio.sleep(1)

        order_id = response.json()['data']['orderId']
        await handel_order_success(order_id, symbol, signal, API_KEY, API_SECRET)
    
    else:
        logger(f"{symbol} 售出失敗\n" + response.text)

async def handel_order_success(order_id, symbol, signal, API_KEY, API_SECRET):
    fills = await get_fills(symbol, order_id, API_KEY, API_SECRET)
        
    fill_data = {
        "orderId": fills['data']['data']['fills'][0]['orderId'],
        "symbol": fills['data']['data']['fills'][0]['symbol'],
        "side": fills['data']['data']['fills'][0]['side'],
        "price": fills['data']['data']['fills'][0]['price'],
        "size": fills['data']['data']['fills'][0]['size'],
        "fee": fills['data']['data']['fills'][0]['fee'],
        "date": timestamp_to_datetime(fills['data']['data']['fills'][0]['timestamp']),
        "strategy": signal[symbol]['strategy']
    }
    
    await save_order(fill_data)

def adjust_trade_size(size, decimal_places):
    # 修正size，使其能被min_trade_size整除
    return math.floor(size * 10**decimal_places) / 10**decimal_places

async def start_trading(queue, API_KEY, API_SECRET, order_amount):
    """
        queue: 用來接收telegram訊息的queue
        API_KEY: pionex的API_KEY
        API_SECRET: pionex的API_SECRET
        order_amount: 每筆交易的下單金額，在pionex/config.json更改，預設20
    """

    while True:
        signal = await queue.get()

        for symbol in signal:
            side = signal[symbol]['action']
            if side == "Buy":
                await buy(signal, symbol, API_KEY, API_SECRET, order_amount)
            elif side == "Sell":
                await sell(signal, symbol, API_KEY, API_SECRET)