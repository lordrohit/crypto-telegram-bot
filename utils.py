import os
import aiohttp
import mplfinance as mpf
import pandas as pd
from io import BytesIO

# Match these to your .env file
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials missing!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    error = await response.text()
                    print(f"Telegram error: {error}")
                return await response.text()
    except Exception as e:
        print(f"Telegram send failed: {e}")

async def generate_chart(df, symbol):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials missing!")
        return

    try:
        # Create a copy to avoid modifying original
        df = df.copy()

        # Correct column names (Binance API returns these exact names)
        df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']]

        # Convert timestamp to datetime index
        df.index = pd.to_datetime(df['open_time'], unit='ms')

        # Rename columns to match mplfinance requirements
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })

        # Get last 100 candles
        plot_df = df[['Open', 'High', 'Low', 'Close', 'Volume']].tail(100)

        # Create in-memory image
        buf = BytesIO()
        mpf.plot(
            plot_df, 
            type='candle', 
            style='charles',
            title=f"{symbol} 15m",
            volume=True,
            savefig=dict(fname=buf, dpi=100, pad_inches=0.25)
        )
        buf.seek(0)

        # Send via Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        form_data = aiohttp.FormData()
        form_data.add_field('chat_id', CHAT_ID)
        form_data.add_field('photo', buf, filename=f'{symbol}.png')

        async with aiohttp.ClientSession() as session:
            await session.post(url, data=form_data)

    except Exception as e:
        error_msg = f"🚨 Chart error for {symbol}: {str(e)[:200]}"
        print(error_msg)
        await send_telegram_message(error_msg)

def detect_patterns(df):
    try:
        # Simple pattern detection - replace with your actual logic
        current = df.iloc[-1]
        prev = df.iloc[-2]

        # Bullish pattern: green candle after red candle
        return current['close'] > current['open'] and prev['close'] < prev['open']
    except Exception as e:
        print(f"Pattern detection error: {e}")
        return False