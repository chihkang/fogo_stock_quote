import datetime
import pytz

def is_trading_time_taiwan():
    """判斷目前是否為台股交易時間 (09:00 - 13:30, 平日)"""
    tz = pytz.timezone("Asia/Taipei")
    now = datetime.datetime.now(tz)
    if now.weekday() >= 5:
        return False
    start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end = now.replace(hour=13, minute=30, second=0, microsecond=0)
    return start <= now <= end

def is_trading_time_us():
    """
    判斷目前是否為美股交易時間 (台北時間)
    - 平日
    - 22:30 到 23:59
    - 00:00 到 05:00 (含 05:00:00)
    """
    tz = pytz.timezone("Asia/Taipei")
    now = datetime.datetime.now(tz)

    if now.weekday() >= 5:
        return False

    if now.hour == 22 and now.minute >= 30:
        return True
    if now.hour == 23:
        return True
    if 0 <= now.hour < 5:
        return True
    if now.hour == 5 and now.minute == 0:
        return True

    return False
