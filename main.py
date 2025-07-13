import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import mplfinance as mpf
from telegram.ext import Updater, CommandHandler
from patterns import detect_all_patterns
from strategy import calculate_trade_levels

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_URL = "https://fapi.binance.com"

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def get_ohlcv(symbol, interval="15m", limit=100):
    url = f"{BASE_URL}/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    res = requests.get(url).json()
    df = pd.DataFrame(res, columns=['time','open','high','low','close','volume','c1','c2','c3','c4','c5','c6'])
    df = df[['time','open','high','low','close','volume']].astype(float)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    return df

def create_chart(df, symbol):
    df_chart = df.copy()
    df_chart.set_index('time', inplace=True)
    df_chart.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

    apds = [
        mpf.make_addplot(df['EMA20'], color='orange'),
        mpf.make_addplot(df['EMA50'], color='red'),
    ]

    filename = f"{symbol}_chart.png"
    mpf.plot(df_chart, type='candle', style='yahoo', addplot=apds,
             title=f"{symbol} Chart (15m)", volume=True, savefig=filename)
    return filename

def send_photo(context, photo_path, caption):
    with open(photo_path, "rb") as photo:
        context.bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=photo, caption=caption)

def analyze(update, context):
    if not context.args:
        update.message.reply_text("Usage: /analyze btc")
        return

    symbol = context.args[0].upper() + "USDT"
    try:
        df = get_ohlcv(symbol)
        df['EMA20'] = EMAIndicator(df['close'], window=20).ema_indicator()
        df['EMA50'] = EMAIndicator(df['close'], window=50).ema_indicator()
        df['RSI'] = RSIIndicator(df['close'], window=14).rsi()

        patterns = detect_all_patterns(df)
        levels = calculate_trade_levels(df)

        if patterns and levels['rr'] >= 1.5:
            chart = create_chart(df, symbol)
            caption = (
                f"🧠 {', '.join(patterns)}\n"
                f"📊 Symbol: {symbol}\n"
                f"📈 Entry: {levels['entry']}\n"
                f"🎯 TP: {levels['tp']}\n"
                f"🛡 SL: {levels['sl']}\n"
                f"⚖ R:R = {levels['rr']}"
            )
            send_photo(context, chart, caption)
        else:
            context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"📉 No good setup found for {symbol}")

    except Exception as e:
        context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ Error: {e}")

dispatcher.add_handler(CommandHandler("analyze", analyze))

if __name__ == "__main__":
    print("🤖 Bot running... use /analyze btc")
    updater.start_polling()

    from threading import Thread
    from autoscan import run_auto_scan
    import time

    def auto_scan_loop(context):
        while True:
            run_auto_scan(context)
            time.sleep(600)

    def start_auto_scan(context):
        thread = Thread(target=auto_scan_loop, args=(context,))
        thread.daemon = True
        thread.start()

    start_auto_scan(updater.bot)
    updater.idle()
