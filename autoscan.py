import os
import pandas as pd
from dotenv import load_dotenv
from patterns_custom import detect_all_patterns
from strategy import calculate_trade_levels

load_dotenv()

symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

def run_auto_scan(bot):
    from main import get_ohlcv, create_chart, send_photo, TELEGRAM_CHAT_ID
    from patterns_custom import detect_all_patterns
    from strategy import calculate_trade_levels

    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

    for symbol in symbols:
        try:
            df = get_ohlcv(symbol)
            df['EMA20'] = df['close'].ewm(span=20).mean()
            df['EMA50'] = df['close'].ewm(span=50).mean()

            patterns = detect_all_patterns(df)

            for pattern in patterns:
                direction = pattern['direction']
                levels = calculate_trade_levels(df, direction)

                if levels and levels['rr'] >= 1.5:
                    chart = create_chart(df, symbol)
                    caption = (
                        f"🧠 {pattern['name']}\n"
                        f"📊 Symbol: {symbol}\n"
                        f"📈 Entry: {levels['entry']}\n"
                        f"🌟 TP: {levels['tp']}\n"
                        f"🛡 SL: {levels['sl']}\n"
                        f"⚖ R:R = {levels['rr']}"
                    )
                    send_photo(bot, chart, caption)
                else:
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"📉 No valid trade setup for {symbol} ({pattern['name']})")

        except Exception as e:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ Error on {symbol}: {e}")