def rsi_calc(df, period=14):
    """
    RSI 계산 함수 (EMA 기반).
    """
    delta = df["close"].diff()
    gains = delta.clip(lower=0)
    declines = -delta.clip(upper=0)

    _gain = gains.ewm(com=(period - 1), min_periods=period).mean()
    _loss = declines.ewm(com=(period - 1), min_periods=period).mean()

    RS = _gain / _loss
    df["RSI"] = 100 - (100 / (1 + RS))
    return df