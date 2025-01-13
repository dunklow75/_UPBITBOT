import asyncio
from datetime import datetime, timedelta
from utils.time_utils import get_last_completed_5min_time
from utils.upbit_api import get_top_30_markets, get_candles
from utils.rsi_calculator import rsi_calc
from utils.telegram_bot import send_telegram_message

async def wait_until_next_5min():
    """
    다음 5분 단위 시간까지 대기합니다.
    """
    now = datetime.now()
    next_5min = now + timedelta(minutes=5 - (now.minute % 5), seconds=-now.second, microseconds=-now.microsecond)
    wait_time = (next_5min - now).total_seconds()
    print(f"[알림] 다음 작업까지 대기: {wait_time:.0f}초")
    await asyncio.sleep(wait_time)

async def calculate_and_collect_rsi(symbol, interval=5, period=14):
    """
    특정 코인의 RSI를 계산하고 RSI < 30 조건을 만족하면 메시지를 반환합니다.
    """
    try:
        print(f"[디버깅] {symbol}: 캔들 데이터 요청 시작 (interval={interval}, period={period})")
        df_data = get_candles(market=symbol, count=200, unit=interval)
        if not df_data:
            print(f"[오류] {symbol}: 데이터가 없습니다.")
            return None

        import pandas as pd
        df = pd.DataFrame(df_data)
        df = df.sort_values(by="candle_date_time_kst").reset_index(drop=True)
        df["close"] = df["trade_price"]

        # 캔들 데이터의 최신 시간 가져오기
        latest_candle_time = df["candle_date_time_kst"].iloc[-1]
        last_completed_time = get_last_completed_5min_time(latest_candle_time, adjust_previous=True)

        # 디버깅: 기준 시간과 캔들 데이터 최신 시간 확인
        print(f"[디버깅] {symbol}: 캔들 데이터 최신 시간: {latest_candle_time}")
        print(f"[디버깅] {symbol}: 기준 시간: {last_completed_time}")

        df = rsi_calc(df, period)
        df["candle_date_time_kst"] = pd.to_datetime(df["candle_date_time_kst"])

        matching_candles = df[df["candle_date_time_kst"] == pd.to_datetime(last_completed_time)]

        if not matching_candles.empty:
            latest_rsi = matching_candles["RSI"].iloc[0]
            if pd.isna(latest_rsi):
                print(f"[오류] {symbol}: RSI 값이 nan입니다. (기준 시간: {last_completed_time})")
                return None
            print(f"[디버깅] {symbol}: 기준 시간 {last_completed_time}, RSI 값: {latest_rsi:.2f}")
            if latest_rsi < 30:  # RSI < 30 조건
                coin_symbol = symbol.split("-")[1]
                return f"🟢 {coin_symbol} / {interval}분봉 / {last_completed_time[11:16]}기준 / RSI : {latest_rsi:.2f}"
        else:
            print(f"[오류] {symbol}: 현재 기준 시간에 해당하는 캔들이 없습니다. (기준 시간: {last_completed_time})")
    except Exception as e:
        print(f"[오류] {symbol} 처리 중 오류 발생: {e}")
    return None

async def main():
    """
    거래대금 상위 30개의 KRW 코인을 감시하여 RSI < 30 조건 충족 시 알림을 한 메시지로 전송합니다.
    """
    await send_telegram_message("🔵 프로그램 시작: 업비트 5분봉 RSI 감시 시작")
    print("[알림] 데이터 수집 프로그램이 시작되었습니다.")

    while True:
        await wait_until_next_5min()

        print("[알림] 거래대금 상위 30개 코인 가져오기 시작")
        top_30_symbols = get_top_30_markets()

        await asyncio.sleep(30)

        alert_messages = []
        tasks = [calculate_and_collect_rsi(symbol) for symbol in top_30_symbols]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                alert_messages.append(result)

        if alert_messages:
            await send_telegram_message("\n".join(alert_messages))

        print("[알림] 감시 완료. 다음 주기를 기다립니다.")

async def shutdown():
    """
    프로그램 종료 시 텔레그램 메시지를 안전하게 전송합니다.
    """
    try:
        await send_telegram_message("🔴 프로그램 종료: 데이터 감시 종료")
        print("[알림] 종료 메시지가 전송되었습니다.")
    except Exception as e:
        print(f"[오류] 종료 메시지 전송 중 문제 발생: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("[알림] 프로그램이 종료됩니다.")
        loop.run_until_complete(shutdown())
    finally:
        loop.close()