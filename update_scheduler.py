import asyncio
from logging_config import logger
from stock_service import (
    fetch_taiwan_stock_quote, fetch_us_stock_quote,
    fetch_stock_list, get_stock_id, update_stock_price
)
from trading_time import is_trading_time_taiwan, is_trading_time_us

async def update_taiwan_stocks():
    """非同步更新台股價格"""
    logger.info("=== 開始更新台股價格 ===")
    stocks = await fetch_stock_list()
    if not stocks:
        logger.warning("股票清單為空, 跳過台股更新")
        return

    tasks = []
    for symbol in stocks:
        if symbol[0].isdigit():
            if is_trading_time_taiwan():
                logger.info(f"台股: 更新 {symbol}")
                # 用台股 API 取得價格
                async def process(symbol=symbol):
                    price = await fetch_taiwan_stock_quote(symbol)
                    if price is not None:
                        stock_id = await get_stock_id(symbol)
                        if stock_id is not None:
                            await update_stock_price(symbol, stock_id, price)
                        else:
                            logger.error(f"{symbol} 的 stock_id 為 None, 無法更新")
                    else:
                        logger.error(f"{symbol} 無法取得股價, 略過更新")
                tasks.append(process())
            else:
                logger.info(f"台股: {symbol} 非交易時間, 略過")
    if tasks:
        await asyncio.gather(*tasks)
    logger.info("=== 台股更新完成 ===")

async def update_us_stocks():
    """非同步更新美股價格"""
    logger.info("=== 開始更新美股價格 ===")
    stocks = await fetch_stock_list()
    if not stocks:
        logger.warning("股票清單為空, 跳過美股更新")
        return

    tasks = []
    for symbol in stocks:
        if not symbol[0].isdigit():
            if is_trading_time_us():
                logger.info(f"美股: 更新 {symbol}")
                async def process(symbol=symbol):
                    price = await fetch_us_stock_quote(symbol)
                    if price is not None:
                        stock_id = await get_stock_id(symbol)
                        if stock_id is not None:
                            await update_stock_price(symbol, stock_id, price)
                        else:
                            logger.error(f"{symbol} 的 stock_id 為 None, 無法更新")
                    else:
                        logger.error(f"{symbol} 無法取得股價, 略過更新")
                tasks.append(process())
            else:
                logger.info(f"美股: {symbol} 非交易時間, 略過")
    if tasks:
        await asyncio.gather(*tasks)
    logger.info("=== 美股更新完成 ===")

def update_taiwan_stocks_sync():
    """
    提供 APScheduler 調用的同步介面，
    內部透過 asyncio.run 執行非同步台股更新
    """
    asyncio.run(update_taiwan_stocks())

def update_us_stocks_sync():
    """
    提供 APScheduler 調用的同步介面，
    內部透過 asyncio.run 執行非同步美股更新
    """
    asyncio.run(update_us_stocks())
