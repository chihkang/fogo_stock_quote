import os
import time
import datetime
import requests
import logging
from logging import StreamHandler
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# 從環境變數讀取設定 (部署時請配置 .env 或平台環境變數)
# -----------------------------
MINIMAL_API_URL = os.environ.get("MINIMAL_API_URL")
FUGLE_API_KEY = os.environ.get("FUGLE_API_KEY")
FINNHUB_API_TOKEN = os.environ.get("FINNHUB_API_TOKEN")
UPDATE_API_URL = os.environ.get("UPDATE_API_URL")

# -----------------------------
# 日誌設定
# -----------------------------
def setup_logging():
    """配置控制台日誌"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-5s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

logger = setup_logging()

# -----------------------------
# 交易時間判斷函數 (Asia/Taipei)
# -----------------------------
def is_trading_time_taiwan():
    """
    判斷目前是否為台股交易時間 (09:00 - 13:30, 平日)
    """
    tz = pytz.timezone("Asia/Taipei")
    now = datetime.datetime.now(tz)
    if now.weekday() >= 5:
        return False
    start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end = now.replace(hour=13, minute=30, second=0, microsecond=0)
    return start <= now <= end

def is_trading_time_us():
    """
    判斷目前是否為美股交易時間 (22:30 - 23:59 或 00:00 - 05:30, 平日)
    """
    tz = pytz.timezone("Asia/Taipei")
    now = datetime.datetime.now(tz)
    if now.weekday() >= 5:
        return False
    # 當日 22:30 ~ 23:59
    if now.hour == 22 and now.minute >= 30:
        return True
    if now.hour == 23:
        return True
    # 跨午夜 00:00 ~ 05:30
    if 0 <= now.hour < 5:
        return True
    if now.hour == 5 and now.minute <= 30:
        return True
    return False

# -----------------------------
# 股票報價及更新處理
# -----------------------------
def fetch_taiwan_stock_quote(symbol):
    """
    呼叫 Fugle API 取得台股 symbol 的即時股價 (lastPrice)
    """
    url = f"https://api.fugle.tw/marketdata/v1.0/stock/intraday/quote/{symbol}"
    headers = {"X-API-KEY": FUGLE_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            last_price = data.get("lastPrice")
            logger.info(f"台股 {symbol} 現在股價: {last_price}")
            return last_price
        else:
            logger.error(f"Fugle API 呼叫錯誤, 狀態碼: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"取得台股 {symbol} 股價發生錯誤: {e}", exc_info=True)
        return None

def fetch_us_stock_quote(symbol):
    """
    呼叫 Finnhub API 取得美股 symbol 的即時股價 (取 JSON 的 "c" 欄位)
    """
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_TOKEN}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            current_price = data.get("c")
            logger.info(f"美股 {symbol} 現在股價: {current_price}")
            return current_price
        else:
            logger.error(f"Finnhub API 呼叫錯誤, 狀態碼: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"取得美股 {symbol} 股價發生錯誤: {e}", exc_info=True)
        return None

def update_stock_price(symbol, stock_id, price):
    """
    更新股價到後端 API
    """
    url = f"{UPDATE_API_URL}/{stock_id}/price?newPrice={price}"
    try:
        response = requests.put(url)
        if response.status_code == 200:
            logger.info(f"成功更新 {symbol} (ID: {stock_id}) 股價為 {price}")
        else:
            logger.error(f"更新 {symbol} 股價失敗, 狀態碼: {response.status_code}")
    except Exception as e:
        logger.error(f"更新 {symbol} 股價時發生錯誤: {e}")

def fetch_stock_list():
    """
    從 minimal API 取得股票清單，回傳所有股票代碼
    """
    try:
        response = requests.get(MINIMAL_API_URL)
        if response.status_code == 200:
            data = response.json()
            stocks = []
            for item in data:
                # 以 ":" 分割，取出左側的 symbol
                parts = item["name"].split(":")
                symbol = parts[0].strip()
                if symbol:
                    stocks.append(symbol)
            logger.info(f"取得 {len(stocks)} 檔股票清單")
            return stocks
        else:
            logger.error(f"取得股票清單失敗, 狀態碼: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"取得股票清單發生錯誤: {e}", exc_info=True)
        return []

def get_stock_id(symbol):
    """
    根據 symbol 從 minimal API 取得對應的 _id
    """
    try:
        response = requests.get(MINIMAL_API_URL)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                if symbol == item["name"].split(":")[0].strip():
                    return item["_id"]
            logger.error(f"找不到 {symbol} 對應的 stock_id")
            return None
        else:
            logger.error(f"取得股票清單錯誤, 狀態碼: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"取得股票 ID 發生錯誤: {e}")
        return None

# -----------------------------
# 合併更新任務，每次從 API 讀取股票清單並更新符合條件的股票
# 判斷方式：若代號第一個字元為數字，視為台股；否則視為美股。
# -----------------------------
def combined_update_stocks():
    logger.info("=== 開始合併更新股票價格 ===")
    stocks = fetch_stock_list()
    if not stocks:
        logger.warning("股票清單為空，跳過此次更新")
        return

    for symbol in stocks:
        # 判斷依據：只要第一個字元是數字，就視為台股
        if symbol[0].isdigit():
            if is_trading_time_taiwan():
                logger.info(f"更新台股 {symbol}")
                price = fetch_taiwan_stock_quote(symbol)
            else:
                logger.info(f"台股 {symbol} 非交易時間，略過")
                continue
        else:
            if is_trading_time_us():
                logger.info(f"更新美股 {symbol}")
                price = fetch_us_stock_quote(symbol)
            else:
                logger.info(f"美股 {symbol} 非交易時間，略過")
                continue

        if price is not None:
            stock_id = get_stock_id(symbol)
            if stock_id is not None:
                update_stock_price(symbol, stock_id, price)
            else:
                logger.error(f"{symbol} 的 stock_id 為 None，無法更新")
        else:
            logger.error(f"{symbol} 無法取得股價，略過更新")
    logger.info("=== 合併更新股票價格完成 ===")

# -----------------------------
# 主程式：使用 APScheduler 排程
# -----------------------------
def main():
    logger.info("開始啟動股票價格更新服務")
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Taipei"))
    scheduler.add_job(combined_update_stocks, "interval", minutes=1, id="combined_stock_update")
    scheduler.start()
    logger.info("APScheduler 已啟動，等待排程觸發...")

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("服務由使用者終止，正在關閉排程服務...")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
