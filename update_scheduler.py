import asyncio
from logging_config import logger
from stock_service import (
    fetch_taiwan_stock_quote, fetch_us_stock_quote,
    fetch_stock_list, get_stock_id, update_stock_price
)
from trading_time import is_trading_time_taiwan, is_trading_time_us

async def process_stock(symbol):
    if symbol[0].isdigit():
        if is_trading_time_taiwan():
            logger.info(f"更新台股 {symbol}")
            price = await fetch_taiwan_stock_quote(symbol)
        else:
            logger.info(f"台股 {symbol} 非交易時間, 略過")
            return
    else:
        if is_trading_time_us():
            logger.info(f"更新美股 {symbol}")
            price = await fetch_us_stock_quote(symbol)
        else:
            logger.info(f"美股 {symbol} 非交易時間, 略過")
            return

    if price is not None:
        stock_id = await get_stock_id(symbol)
        if stock_id is not None:
            await update_stock_price(symbol, stock_id, price)
        else:
            logger.error(f"{symbol} 的 stock_id 為 None, 無法更新")
    else:
        logger.error(f"{symbol} 無法取得股價, 略過更新")

async def combined_update_stocks():
    """合併更新台股和美股價格 (非同步)"""
    logger.info("=== 開始合併更新股票價格 ===")
    stocks = await fetch_stock_list()
    if not stocks:
        logger.warning("股票清單為空, 跳過此次更新")
        return

    tasks = [process_stock(symbol) for symbol in stocks]
    await asyncio.gather(*tasks)
    logger.info("=== 合併更新股票價格完成 ===")

def combined_update_stocks_sync():
    """
    提供給 APScheduler 調用的同步介面，
    內部透過 asyncio.run 處理非同步邏輯
    """
    asyncio.run(combined_update_stocks())
