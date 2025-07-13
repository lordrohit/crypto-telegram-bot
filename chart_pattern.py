def detect_all_patterns(df):
  flag = detect_flag(df)
  wedge = detect_wedge(df)
  hs = detect_head_shoulders(df)
  patterns = [p for p in [flag, wedge, hs] if p]
  return patterns if patterns else None