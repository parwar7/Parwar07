# bitget_wrapper.py

import time
import requests
import hmac
import hashlib
import base64
import json
import pandas as pd

API_KEY = "your_demo_api_key"
API_SECRET = "your_demo_api_secret"
PASSPHRASE = "your_demo_passphrase"
BASE_URL = "https://api-demo.bitget.com"

def sign_request(timestamp, method, request_path, body=''):
    message = f'{timestamp}{method}{request_path}{body}'
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    return signature

def get_headers(method, request_path, body=''):
    timestamp = str(int(time.time() * 1000))
    signature = sign_request(timestamp, method, request_path, body)
    return {
        'ACCESS-KEY': API_KEY,
        'ACCESS-SIGN': signature,
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }

def get_latest_candles(symbol='DOGEUSDT_UMCBL'):
    url = f"/api/mix/v1/market/candles?symbol={symbol}&granularity=5min&limit=100"
    r = requests.get(BASE_URL + url)
    data = r.json()['data']
    df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume','turnover','confirm'])
    df = df[['timestamp','open','high','low','close','volume']]
    df.columns = ['timestamp','open','high','low','close','volume']
    df = df.iloc[::-1].astype(float).reset_index(drop=True)
    return df

def place_order(symbol, side, size=50):
    url = "/api/mix/v1/order/placeOrder"
    body = json.dumps({
        "symbol": symbol,
        "marginCoin": "USDT",
        "side": side,
        "orderType": "market",
        "size": str(size),
        "tradeSide": "open",
        "productType": "umcbl"
    })
    headers = get_headers("POST", url, body)
    r = requests.post(BASE_URL + url, headers=headers, data=body)
    return r.json()
