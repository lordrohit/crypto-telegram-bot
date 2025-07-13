import os import requests import pandas as pd from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://fapi.binance.com"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_ohlcv(symbol, interval="15m", limit=100): url = f"{BASE_URL}/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}" res = requests.get(url).json() df = pd.DataFrame(res, columns=['time','open','high','low','close','volume','c1','c2','c3','c4','c5','c6']) df = df[['time','open','high','low','close','volume']].astype(float) df['time'] = pd.to_datetime(df['time'], unit='ms') return df

def send_photo(bot, photo_path, caption): with open(photo_path, "rb") as photo: bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=photo, caption=caption)

def send_message(bot, message): bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def calculate_atr(df, period=14): df['H-L'] = df['high'] - df['low'] df['H-PC'] = abs(df['high'] - df['close'].shift(1)) df['L-PC'] = abs(df['low'] - df['close'].shift(1)) tr = df[['H-L', 'H

