import asyncio
from logging_config import logger
from stock_service import (
    fetch_taiwan_stock_quote, fetch_us_stock_quote,
    fetch_stock_list, get_stock_id, update_stock_price
)
from trading_time import is_trading_time_taiwan, is_trading_time_us

import json

STOCK_LIST_FILE = "stock_list.json"

async def _load_stock_list():
    """從檔案或 API 載入股票清單"""
    try:
        with open(STOCK_LIST_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info("股票清單檔案不存在, 從 API 獲取")
        stocks = await fetch_stock_list()
        if stocks:
            with open(STOCK_LIST_FILE, "w") as f:
                json.dump(stocks, f)
            return stocks
        else:
            logger.warning("無法從 API 獲取股票清單")
            return []

async def _update_stocks(stock_type: str, is_trading_time_func, fetch_stock_quote_func):
    """非同步更新股票價格"""
    logger.info(f"=== 開始更新{stock_type}價格 ===")
    stocks = await _load_stock_list()
    if not stocks:
        logger.warning("股票清單為空, 跳過更新")
        return

    if not is_trading_time_func():
        logger.info(f"{stock_type}非交易時間, 略過")
        return

    tasks = []
    for symbol in stocks:
        if (stock_type == "台股" and symbol[0].isdigit()) or (stock_type == "美股" and not symbol[0].isdigit()):
            logger.info(f"{stock_type}: 更新 {symbol}")
            async def process(symbol=symbol):
                try:
                    price = await fetch_stock_quote_func(symbol)
                    if price is None:
                        logger.error(f"{symbol} 無法取得股價, 略過更新")
                        return

                    stock_id = await get_stock_id(symbol)
                    if stock_id is None:
                        logger.error(f"{symbol} 的 stock_id 為 None, 無法更新")
                        return

                    await update_stock_price(symbol, stock_id, price)

                except Exception as e:
                    logger.exception(f"更新 {symbol} 發生錯誤: {e}")
            tasks.append(process())
    if tasks:
        await asyncio.gather(*tasks)
    logger.info(f"=== {stock_type}更新完成 ===")

async def update_taiwan_stocks():
    """非同步更新台股價格"""
    await _update_stocks("台股", is_trading_time_taiwan, fetch_taiwan_stock_quote)

async def update_us_stocks():
    """非同步更新美股價格"""
    await _update_stocks("美股", is_trading_time_us, fetch_us_stock_quote)

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
