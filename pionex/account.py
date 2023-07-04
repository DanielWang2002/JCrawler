import json
import time
import hmac
import hashlib
import requests

BASE_URL = 'https://api.pionex.com'

def get_timestamp():
    return str(int(time.time() * 1000))

def generate_signature(API_SECRET, method, path_url, query_string):
    message = method + path_url + "?" + query_string
    # print(message)
    return hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()

async def get_balance(API_KEY, API_SECRET):
    method = 'GET'
    path_url = '/api/v1/account/balances'
    timestamp = get_timestamp()
    query_string = f"timestamp={timestamp}"
    # print(query_string)
    signature = generate_signature(API_SECRET, method, path_url, query_string)

    headers = {
        'PIONEX-KEY': API_KEY,
        'PIONEX-SIGNATURE': signature,
    }

    response = requests.get(BASE_URL + path_url + '?' + query_string, headers=headers)

    if response.status_code == 200:
        print(response.json())
    else:
        print("Error:", response.status_code)
        print(response.json())