import requests

def get_candles(market, count=200, unit=5):
    """
    업비트 캔들 데이터 가져오기.
    """
    url = f"https://api.upbit.com/v1/candles/minutes/{unit}"
    params = {"market": market, "count": count}
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.status_code == 200 else None

def get_top_30_markets():
    """
    거래대금 기준 상위 30개의 KRW 코인 리스트를 가져옵니다.
    """
    url = "https://api.upbit.com/v1/ticker"
    headers = {"Accept": "application/json"}
    markets_response = requests.get("https://api.upbit.com/v1/market/all", headers=headers)
    all_markets = [market["market"] for market in markets_response.json() if market["market"].startswith("KRW")]

    params = {"markets": ",".join(all_markets)}
    ticker_response = requests.get(url, headers=headers, params=params)
    if ticker_response.status_code == 200:
        data = ticker_response.json()
        sorted_markets = sorted(data, key=lambda x: x["acc_trade_price_24h"], reverse=True)
        return [market["market"] for market in sorted_markets[:30]]
    return []