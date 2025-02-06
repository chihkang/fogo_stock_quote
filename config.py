import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置管理類別"""
    REQUIRED_ENV_VARS = [
        "MINIMAL_API_URL",
        "FUGLE_API_KEY",
        "FINNHUB_API_TOKEN",
        "UPDATE_API_URL"
    ]
    
    REQUEST_TIMEOUT = (3.05, 27)  # (連接超時, 讀取超時)
    
    @classmethod
    def validate_env(cls):
        """驗證必要的環境變數"""
        missing_vars = [var for var in cls.REQUIRED_ENV_VARS if not os.environ.get(var)]
        if missing_vars:
            raise EnvironmentError(f"缺少必要的環境變數: {', '.join(missing_vars)}")
    
    @classmethod
    def get_env(cls, key):
        """安全地獲取環境變數"""
        value = os.environ.get(key)
        if not value and key in cls.REQUIRED_ENV_VARS:
            raise EnvironmentError(f"環境變數 {key} 未設置")
        return value

# 初始化設定，可於其他模組中匯入使用
MINIMAL_API_URL = Config.get_env("MINIMAL_API_URL")
FUGLE_API_KEY = Config.get_env("FUGLE_API_KEY")
FINNHUB_API_TOKEN = Config.get_env("FINNHUB_API_TOKEN")
UPDATE_API_URL = Config.get_env("UPDATE_API_URL")
