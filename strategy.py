def calculate_trade_levels(df):
  last_close = df['close'].iloc[-1]
  atr = df['ATR'].iloc[-1] if 'ATR' in df.columns else 20

  entry = last_close
  sl = entry - atr * 1.2
  tp = entry + atr * 2.5
  rr = (tp - entry) / (entry - sl) if (entry - sl) != 0 else 0

  return {
      "entry": round(entry, 4),
      "sl": round(sl, 4),
      "tp": round(tp, 4),
      "rr": round(rr, 2)
  }