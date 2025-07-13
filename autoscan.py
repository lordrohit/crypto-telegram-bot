import os
import requests
import pandas as pd
from dotenv import load_dotenv
from ta.volatility import AverageTrueRange
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from patterns import detect_all_patterns
from strategy import calculate_trade_levels
from main import create_chart, send_photo, get_ohlcv, TELEGRAM_CHAT_ID

load_dotenv()

BASE_URL = "https://fapi.binance.com"
SYMBOLS_TO_SCAN = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", 
    "XRPUSDT", "MATICUSDT", "PEPEUSDT", "DOGEUSDT"
]

def get_top_movers():
    url = f"{BASE_URL}/fapi/v1/ticker/24hr"
    res = requests.get(url).json()
    df = pd.DataFrame(res)
    df['priceChangePercent'] = df['priceChangePercent'].astype(float)
    df['quoteVolume'] = df['quoteVolume'].astype(float)
    df = df[df['symbol'].str.endswith("USDT")]
    df = df[df['symbol'].isin(SYMBOLS_TO_SCAN)]
    top = df.sort_values(by=['quoteVolume', 'priceChangePercent'], ascending=False).head(3)
    return top['symbol'].tolist()

def run_auto_scan(context):
    top_symbols = get_top_movers()

    for symbol in top_symbols:
        try:
            df = get_ohlcv(symbol)
            df['EMA20'] = EMAIndicator(df['close'], window=20).ema_indicator()
            df['EMA50'] = EMAIndicator(df['close'], window=50).ema_indicator()
            df['RSI'] = RSIIndicator(df['close'], window=14).rsi()
            df['ATR'] = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()

            patterns = detect_all_patterns(df)
            levels = calculate_trade_levels(df)

            if patterns and levels['rr'] >= 1.5:
                chart = create_chart(df, symbol)
                leverage = suggest_leverage(df['ATR'].iloc[-1])
                caption = (
                    f"🚀 Auto Scan Alert\n"
                    f"📊 Symbol: {symbol}\n"
                    f"📈 Entry: {levels['entry']:.2f}\n"
                    f"🎯 TP: {levels['tp']:.2f}\n"
                    f"🛡 SL: {levels['sl']:.2f}\n"
                    f"⚖ R:R = {levels['rr']:.2f}\n"
                    f"🔍 Pattern: {', '.join(patterns)}\n"
                    f"💥 Volatility (ATR): {df['ATR'].iloc[-1]:.2f}\n"
                    f"⚡ Suggested Leverage: {leverage}x"
                )
                send_photo(context, chart, caption)
        except Exception as e:
            context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ Error on {symbol}: {e}")

def suggest_leverage(atr):
    if atr > 50:
        return 5
    elif atr > 20:
        return 10
    else:
        return 15
