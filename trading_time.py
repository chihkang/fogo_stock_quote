import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

def _is_trading_time(timezone_str, start_time, end_time):
    """判斷目前是否為交易時間"""
    tz = pytz.timezone(timezone_str)
    now = datetime.datetime.now(tz).time()
    if datetime.datetime.now(tz).weekday() >= 5:
        logger.debug(f"{timezone_str}: 今天為週末,不屬於交易日")
        return False

    # 判斷是否在交易時間內
    if start_time < end_time:
        is_trading = start_time <= now <= end_time
    else:  # 跨日交易
        is_trading = now >= start_time or now <= end_time

    logger.debug(
        f"{timezone_str}交易時段判斷: now={now}, start={start_time}, end={end_time}, is_trading={is_trading}"
    )
    return is_trading

def is_trading_time_taiwan():
    """判斷目前是否為台股交易時間 (09:00 - 13:30, 平日)"""
    start_time = datetime.time(9, 0)
    end_time = datetime.time(13, 30)
    return _is_trading_time("Asia/Taipei", start_time, end_time)

def is_trading_time_us():
    """
    判斷目前是否為美股交易時間 (考慮夏令時間)
    美股交易時間為台北時間 22:30 - 隔日 5:00 (冬令時間)
    夏令時間則提前一小時,為 21:30 - 隔日 4:00
    """
    eastern_tz = pytz.timezone('US/Eastern')
    now_utc = datetime.datetime.utcnow()
    now_eastern = now_utc.replace(tzinfo=pytz.utc).astimezone(eastern_tz)

    # 檢查是否為週末
    if now_eastern.weekday() >= 5:
        logger.debug("美股: 今天為週末,不屬於交易日")
        return False

    # 冬令時間
    start_time_winter = datetime.time(22, 30)
    end_time_winter = datetime.time(5, 0)

    # 夏令時間
    start_time_summer = datetime.time(21, 30)
    end_time_summer = datetime.time(4, 0)

    # 判斷是否為夏令時間
    is_dst = now_eastern.dst() != datetime.timedelta(0)

    if is_dst:
        start_time = start_time_summer
        end_time = end_time_summer
    else:
        start_time = start_time_winter
        end_time = end_time_winter

    return _is_trading_time("US/Eastern", start_time, end_time)
