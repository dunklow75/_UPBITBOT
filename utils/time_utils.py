from datetime import datetime, timedelta
import pandas as pd

def get_last_completed_5min_time(latest_candle_time=None, adjust_previous=False):
    """
    캔들 데이터의 최신 시간을 기준으로 가장 최근 완료된 5분 단위 시간 반환.
    :param latest_candle_time: 캔들 데이터의 최신 시간 (선택 사항)
    :param adjust_previous: True일 경우, 이전 5분 단위 시간을 반환
    """
    if latest_candle_time:
        # 캔들 데이터의 최신 시간을 기준으로 계산
        latest_time = pd.to_datetime(latest_candle_time)
        last_5min = latest_time - timedelta(minutes=(latest_time.minute % 5), seconds=latest_time.second, microseconds=latest_time.microsecond)
        if adjust_previous:
            last_5min -= timedelta(minutes=5)  # 이전 5분 단위로 이동
    else:
        # 현재 시간을 기준으로 계산
        now = datetime.now()
        last_5min = now - timedelta(minutes=(now.minute % 5), seconds=now.second, microseconds=now.microsecond)
        if adjust_previous:
            last_5min -= timedelta(minutes=5)  # 이전 5분 단위로 이동

    return last_5min.strftime("%Y-%m-%d %H:%M:%S")