from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Tuple
import os

class Settings(BaseSettings):
    """配置管理類別"""
    minimal_api_url: str = Field(..., env="MINIMAL_API_URL")
    fugle_api_key: str = Field(..., env="FUGLE_API_KEY")
    finnhub_api_token: str = Field(..., env="FINNHUB_API_TOKEN")
    update_api_url: str = Field(..., env="UPDATE_API_URL")
    request_timeout: str = Field("3.05,27", env="REQUEST_TIMEOUT")  # (連接超時, 讀取超時)
    taiwan_stock_update_interval: int = Field(2, env="TAIWAN_STOCK_UPDATE_INTERVAL")
    us_stock_update_interval: int = Field(5, env="US_STOCK_UPDATE_INTERVAL")

    @property
    def request_timeout_tuple(self) -> Tuple[float, float]:
        """將 REQUEST_TIMEOUT 環境變數轉換為 Tuple[float, float]"""
        try:
            return tuple(map(float, self.request_timeout.split(",")))  # 將字串分割成 Tuple[float, float]
        except ValueError:
            raise ValueError("REQUEST_TIMEOUT 環境變數格式不正確, 應為 'float,float'")

    class Config:
        env_file = ".env"  # 讀取 .env 檔案
        env_file_encoding = "utf-8"

# 初始化設定,可於其他模組中匯入使用
settings = Settings()
MINIMAL_API_URL = settings.minimal_api_url
FUGLE_API_KEY = settings.fugle_api_key
FINNHUB_API_TOKEN = settings.finnhub_api_token
UPDATE_API_URL = settings.update_api_url
REQUEST_TIMEOUT = settings.request_timeout_tuple
TAIWAN_STOCK_UPDATE_INTERVAL = settings.taiwan_stock_update_interval
US_STOCK_UPDATE_INTERVAL = settings.us_stock_update_interval
