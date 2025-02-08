import aiohttp
import asyncio
import re
from logging_config import logger
from config import settings, MINIMAL_API_URL, FUGLE_API_KEY, FINNHUB_API_TOKEN, UPDATE_API_URL

class StockServiceError(Exception):
    """自定義股票服務異常"""
    pass

# 創建一個全域的 aiohttp.ClientSession 物件
client_session = None

async def get_client_session():
    global client_session
    if client_session is None:
        client_session = aiohttp.ClientSession()
    return client_session

async def close_client_session():
    if client_session:
        await client_session.close()

def get_client_timeout():
    """根據 Config.REQUEST_TIMEOUT 回傳 aiohttp.ClientTimeout 物件"""
    connect, sock_read = settings.request_timeout_tuple
    return aiohttp.ClientTimeout(connect=connect, sock_read=sock_read)

async def _fetch_stock_quote(symbol, url, headers=None):
    """非同步呼叫 API 取得股票 symbol 的即時股價"""
    try:
        timeout = get_client_timeout()
        session = await get_client_session()
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status == 200:
                data = await response.json()
                if "lastPrice" in data:
                    price = data.get("lastPrice")
                else:
                    price = data.get("c")
                logger.info(f"{symbol} 現在股價: {price}")
                return price
            else:
                logger.error(f"API 呼叫錯誤, 狀態碼: {response.status}")
                raise StockServiceError(f"API 呼叫錯誤, 狀態碼: {response.status}")
    except asyncio.TimeoutError:
        logger.error(f"取得 {symbol} 股價超時")
        raise StockServiceError(f"取得 {symbol} 股價超時")
    except StockServiceError as e:
        raise e
    except Exception as e:
        logger.error(f"取得 {symbol} 股價發生錯誤: {e}", exc_info=True)
        raise StockServiceError(f"取得 {symbol} 股價發生錯誤: {e}")

async def fetch_taiwan_stock_quote(symbol):
    """非同步呼叫 Fugle API 取得台股 symbol 的即時股價"""
    url = f"https://api.fugle.tw/marketdata/v1.0/stock/intraday/quote/{symbol}"
    headers = {"X-API-KEY": FUGLE_API_KEY}
    return await _fetch_stock_quote(symbol, url, headers)

async def fetch_us_stock_quote(symbol):
    """非同步呼叫 Finnhub API 取得美股 symbol 的即時股價"""
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_TOKEN}"
    return await _fetch_stock_quote(symbol, url)

async def update_stock_price(symbol, stock_id, price):
    """非同步更新股價到後端 API"""
    url = f"{UPDATE_API_URL}/{stock_id}/price?newPrice={price}"
    try:
        timeout = get_client_timeout()
        session = await get_client_session()
        async with session.put(url, timeout=timeout) as response:
            if response.status == 200:
                logger.info(f"成功更新 {symbol} (ID: {stock_id}) 股價為 {price}")
            else:
                logger.error(f"更新 {symbol} 股價失敗, 狀態碼: {response.status}")
                raise StockServiceError(f"更新 {symbol} 股價失敗, 狀態碼: {response.status}")
    except asyncio.TimeoutError:
        logger.error(f"更新 {symbol} 股價超時")
        raise StockServiceError(f"更新 {symbol} 股價超時")
    except StockServiceError as e:
        raise e
    except Exception as e:
        logger.error(f"更新 {symbol} 股價時發生錯誤: {e}")
        raise StockServiceError(f"更新 {symbol} 股價時發生錯誤: {e}")


async def fetch_stock_data():
    """非同步從 minimal API 取得股票清單和 stock_id"""
    try:
        timeout = get_client_timeout()
        session = await get_client_session()
        async with session.get(MINIMAL_API_URL, timeout=timeout) as response:
            if response.status == 200:
                data = await response.json()
                stock_data = []
                for item in data:
                    match = re.match(r"([^:]+):", item["name"])
                    if match:
                        symbol = match.group(1).strip()
                        if symbol:
                            stock_data.append({
                                "symbol": symbol,
                                "_id": item["_id"]
                            })
                logger.info(f"取得 {len(stock_data)} 檔股票清單")
                return stock_data
            else:
                logger.error(f"取得股票清單失敗, 狀態碼: {response.status}")
                raise StockServiceError(f"取得股票清單失敗, 狀態碼: {response.status}")
    except asyncio.TimeoutError:
        logger.error("取得股票清單超時")
        raise StockServiceError("取得股票清單超時")
    except StockServiceError as e:
        raise e
    except Exception as e:
        logger.error(f"取得股票清單發生錯誤: {e}", exc_info=True)
        raise StockServiceError(f"取得股票清單發生錯誤: {e}")

async def get_stock_id(symbol):
    """非同步根據 symbol 從 minimal API 取得對應的 _id"""
    stock_data = await fetch_stock_data()
    for item in stock_data:
        if symbol == item["symbol"]:
            return item["_id"]
    logger.error(f"找不到 {symbol} 對應的 stock_id")
    return None

async def fetch_stock_list():
    """非同步從 minimal API 取得股票清單"""
    stock_data = await fetch_stock_data()
    stock_list = [item["symbol"] for item in stock_data]
    return stock_list
