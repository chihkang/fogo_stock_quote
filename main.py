import time
import sys
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from logging_config import logger
from config import Config
from update_scheduler import combined_update_stocks_sync

def main():
    """主程式入口"""
    try:
        # 驗證環境變數
        Config.validate_env()
        
        logger.info("開始啟動股票價格更新服務")
        scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Taipei"))
        # 排程採用同步包裝後的非同步更新函數
        scheduler.add_job(combined_update_stocks_sync, "interval", minutes=1, id="combined_stock_update")
        scheduler.start()
        logger.info("APScheduler 已啟動, 等待排程觸發...")

        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("服務由使用者終止, 正在關閉排程服務...")
        scheduler.shutdown()
    except EnvironmentError as e:
        logger.error(f"環境變數錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"服務執行發生錯誤: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
