import pandas as pd

def detect_bull_flag(df):
    df['EMA20'] = df['close'].ewm(span=20).mean()

    trend_strength = df['close'].iloc[-20:-10].mean() < df['close'].iloc[-10:].mean()

    pullback = (
        df['close'].iloc[-3] > df['close'].iloc[-2] < df['close'].iloc[-1] and
        df['close'].iloc[-1] > df['EMA20'].iloc[-1]
    )

    return trend_strength and pullback

def detect_bear_flag(df):
    df['EMA20'] = df['close'].ewm(span=20).mean()

    trend_strength = df['close'].iloc[-20:-10].mean() > df['close'].iloc[-10:].mean()

    pullback = (
        df['close'].iloc[-3] < df['close'].iloc[-2] > df['close'].iloc[-1] and
        df['close'].iloc[-1] < df['EMA20'].iloc[-1]
    )

    return trend_strength and pullback

def detect_all_patterns(df):
    patterns = []

    if detect_bull_flag(df):  # this is now defined above
        patterns.append({"name": "Bull Flag", "direction": "bullish"})

    if detect_bear_flag(df):  # also defined above
        patterns.append({"name": "Bear Flag", "direction": "bearish"})

    return patterns