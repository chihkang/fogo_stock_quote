import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

def is_trading_time_taiwan():
    """判斷目前是否為台股交易時間 (09:00 - 13:30, 平日)"""
    tz = pytz.timezone("Asia/Taipei")
    now = datetime.datetime.now(tz)
    if now.weekday() >= 5:
        logger.debug("台股: 今天為週末，不屬於交易日")
        return False
    start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end = now.replace(hour=13, minute=30, second=0, microsecond=0)
    in_session = start <= now <= end
    logger.debug(f"台股交易時段判斷: now={now}, start={start}, end={end}, in_session={in_session}")
    return in_session

def is_trading_time_us():
    """
    判斷目前台北時間是否落在美股交易時段（台北時間換算後為前一日 22:30 至隔日 05:00）。
    注意：此函式未考慮美股夏令時間（DST）的影響，如需正確計算，建議根據東部時間動態轉換。
    """
    tz = pytz.timezone("Asia/Taipei")
    now = datetime.datetime.now(tz)
    logger.debug(f"美股交易: 當前時間 now = {now}")
    
    # 非平日直接返回 False
    if now.weekday() >= 5:
        logger.debug("美股: 今天為週末，不屬於交易日")
        return False

    # 設定交易時段起始（台北時間）：當天 22:30
    session_start = now.replace(hour=22, minute=30, second=0, microsecond=0)

    # 如果現在時間在凌晨 00:00 到 05:00，此時交易起始時間應該在前一天的 22:30
    if now.hour < 5:
        session_start = (now - datetime.timedelta(days=1)).replace(hour=22, minute=30, second=0, microsecond=0)
    
    # 計算交易時段結束：起始時間加上 6 小時 30 分鐘，即到隔日 05:00
    session_end = session_start + datetime.timedelta(hours=6, minutes=30)
    
    in_session = session_start <= now <= session_end
    logger.info(
        f"美股交易時段判斷: now={now}, session_start={session_start}, session_end={session_end}, in_session={in_session}"
    )
    return in_session
