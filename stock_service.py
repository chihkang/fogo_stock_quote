import aiohttp
import asyncio
from logging_config import logger
from config import Config, MINIMAL_API_URL, FUGLE_API_KEY, FINNHUB_API_TOKEN, UPDATE_API_URL

def get_client_timeout():
    """根據 Config.REQUEST_TIMEOUT 回傳 aiohttp.ClientTimeout 物件"""
    connect, sock_read = Config.REQUEST_TIMEOUT
    return aiohttp.ClientTimeout(connect=connect, sock_read=sock_read)

async def fetch_taiwan_stock_quote(symbol):
    """非同步呼叫 Fugle API 取得台股 symbol 的即時股價"""
    url = f"https://api.fugle.tw/marketdata/v1.0/stock/intraday/quote/{symbol}"
    headers = {"X-API-KEY": FUGLE_API_KEY}
    try:
        timeout = get_client_timeout()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    last_price = data.get("lastPrice")
                    logger.info(f"台股 {symbol} 現在股價: {last_price}")
                    return last_price
                else:
                    logger.error(f"Fugle API 呼叫錯誤, 狀態碼: {response.status}")
                    return None
    except asyncio.TimeoutError:
        logger.error(f"取得台股 {symbol} 股價超時")
        return None
    except Exception as e:
        logger.error(f"取得台股 {symbol} 股價發生錯誤: {e}", exc_info=True)
        return None

async def fetch_us_stock_quote(symbol):
    """非同步呼叫 Finnhub API 取得美股 symbol 的即時股價"""
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_TOKEN}"
    try:
        timeout = get_client_timeout()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    current_price = data.get("c")
                    logger.info(f"美股 {symbol} 現在股價: {current_price}")
                    return current_price
                else:
                    logger.error(f"Finnhub API 呼叫錯誤, 狀態碼: {response.status}")
                    return None
    except asyncio.TimeoutError:
        logger.error(f"取得美股 {symbol} 股價超時")
        return None
    except Exception as e:
        logger.error(f"取得美股 {symbol} 股價發生錯誤: {e}", exc_info=True)
        return None

async def update_stock_price(symbol, stock_id, price):
    """非同步更新股價到後端 API"""
    url = f"{UPDATE_API_URL}/{stock_id}/price?newPrice={price}"
    try:
        timeout = get_client_timeout()
        async with aiohttp.ClientSession() as session:
            async with session.put(url, timeout=timeout) as response:
                if response.status == 200:
                    logger.info(f"成功更新 {symbol} (ID: {stock_id}) 股價為 {price}")
                else:
                    logger.error(f"更新 {symbol} 股價失敗, 狀態碼: {response.status}")
    except asyncio.TimeoutError:
        logger.error(f"更新 {symbol} 股價超時")
    except Exception as e:
        logger.error(f"更新 {symbol} 股價時發生錯誤: {e}")

async def fetch_stock_list():
    """非同步從 minimal API 取得股票清單"""
    try:
        timeout = get_client_timeout()
        async with aiohttp.ClientSession() as session:
            async with session.get(MINIMAL_API_URL, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    stocks = []
                    for item in data:
                        parts = item["name"].split(":")
                        symbol = parts[0].strip()
                        if symbol:
                            stocks.append(symbol)
                    logger.info(f"取得 {len(stocks)} 檔股票清單")
                    return stocks
                else:
                    logger.error(f"取得股票清單失敗, 狀態碼: {response.status}")
                    return []
    except asyncio.TimeoutError:
        logger.error("取得股票清單超時")
        return []
    except Exception as e:
        logger.error(f"取得股票清單發生錯誤: {e}", exc_info=True)
        return []

async def get_stock_id(symbol):
    """非同步根據 symbol 從 minimal API 取得對應的 _id"""
    try:
        timeout = get_client_timeout()
        async with aiohttp.ClientSession() as session:
            async with session.get(MINIMAL_API_URL, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data:
                        if symbol == item["name"].split(":")[0].strip():
                            return item["_id"]
                    logger.error(f"找不到 {symbol} 對應的 stock_id")
                    return None
                else:
                    logger.error(f"取得股票清單錯誤, 狀態碼: {response.status}")
                    return None
    except asyncio.TimeoutError:
        logger.error(f"取得股票 {symbol} ID 超時")
        return None
    except Exception as e:
        logger.error(f"取得股票 ID 發生錯誤: {e}")
        return None
