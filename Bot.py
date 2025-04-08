# bot.py

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import joblib
import time
from bitget_wrapper import get_latest_candles, place_order

model = joblib.load("dogeusdt_model.pkl")
capital = 10
position = 0
entry_price = 0
symbol = "DOGEUSDT_UMCBL"

while True:
    df = get_latest_candles(symbol)

    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
    bb = BollingerBands(df['close'], window=20)
    df['bb_width'] = bb.bollinger_wband()
    df['return_5'] = df['close'].pct_change(5)
    for i in range(1, 6):
        df[f'lag_{i}'] = df['close'].shift(i)
    df.dropna(inplace=True)

    features = ['rsi', 'bb_width', 'return_5'] + [f'lag_{i}' for i in range(1, 6)]
    latest = df[features].iloc[-1:]
    signal = model.predict(latest)[0]

    print(f"Signal: {signal}")
    if signal == 1 and position == 0:
        entry_price = df['close'].iloc[-1]
        position = capital * 10
        size = position / entry_price
        place_order(symbol, "open_long", size=size)
        print("Order Placed!")
    elif position > 0:
        current_price = df['close'].iloc[-1]
        size = position / entry_price
        pnl = (current_price - entry_price) * size
        if pnl >= 0.05 * position or pnl <= -0.02 * position:
            capital += pnl
            position = 0
            print(f"Trade closed. PnL: {pnl:.2f}")
            place_order(symbol, "close_long", size=size)

    time.sleep(300)
