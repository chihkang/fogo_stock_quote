import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from logging_config import logger
from config import settings
from update_scheduler import update_taiwan_stocks_sync, update_us_stocks_sync

def main():
    """主程式入口"""
    logger.info("開始啟動股票價格更新服務")
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Taipei"))
    # 台股每 {settings.taiwan_stock_update_interval} 分鐘更新一次
    scheduler.add_job(update_taiwan_stocks_sync, "interval", minutes=settings.taiwan_stock_update_interval, id="taiwan_stock_update")
    # 美股每 {settings.us_stock_update_interval} 分鐘更新一次
    scheduler.add_job(update_us_stocks_sync, "interval", minutes=settings.us_stock_update_interval, id="us_stock_update")

    scheduler.start()
    logger.info("APScheduler 已啟動, 等待排程觸發...")

    try:
        # 讓 APScheduler 直接管理程式的生命週期, 避免使用無限迴圈
        # scheduler.start()  # 啟動排程器
        while True:
            pass  # 保持主線程運行,讓排程器工作
    except (KeyboardInterrupt, SystemExit):
        logger.info("接收到終止訊號,關閉排程器...")
    finally:
        scheduler.shutdown(wait=False)  # 立即關閉排程器
        logger.info("排程器已關閉")

if __name__ == "__main__":
    main()
