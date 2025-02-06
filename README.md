# 股票更新服務 📈💹

這個專案是一個使用 Python 撰寫的股票價格更新服務，透過 [APScheduler](https://apscheduler.readthedocs.io/) 定時更新台股及美股最新股價，並將更新結果上傳到後端 API。專案同時支援環境變數管理，適合部署到 [Railway.app](https://railway.app/) 等 PaaS 平台 🚀

## 功能亮點 ✨

-  **定時更新**：每分鐘檢查是否在交易時段，符合條件則更新股票價格。
-  **市場分類**：依據股票代號第一個字元是否為數字，判斷為台股或美股：
   - 若第一個字元是數字（例如 "00687B"），則視為台股，依據台股交易時間 (09:00-13:30) 更新。
   - 否則視為美股，依據美股交易時間 (22:30-23:59 以及 00:00-05:30) 更新。
-  **環境變數管理**：採用 `.env` 檔案管理 API URL 與 Token，安全又方便 🔒
-  **詳細日誌**：內建 log 輸出 (INFO 與 ERROR) 方便追蹤及除錯 📝

## 安裝與設定 🛠️

### **1. Clone 專案**

```bash
git clone https://github.com/chihkang/fogo_stock_quote.git
cd fogo_stock_quote
```

### **2. 建立虛擬環境並安裝依賴**

使用 pip 建立虛擬環境（建議使用 [venv](https://docs.python.org/3/library/venv.html)）：

```bash
python -m venv venv

source venv/bin/activate  # Linux/macOS

venv\Scripts\activate    # Windows
```

然後使用 pip 安裝必要套件：

```bash
pip install -r requirements.txt
```

### **3. 配置環境變數** 🔑

建立一個 ⁠.env 檔案（請參考 ⁠.env.sample 範例），並設定下列變數：

MINIMAL_API_URL=

UPDATE_API_URL=

FUGLE_API_KEY=your_fugle_api_key

FINNHUB_API_TOKEN=your_finnhub_api_token

**使用說明** 📋

啟動程式後，APScheduler 會每分鐘執行一次合併更新任務：

​	•	當前時間在台股或美股的交易時段，對應市場的股票會更新股價。

​	•	每次更新會從最新的股票清單中讀取資料，確保若股票清單有任何變更，都能即時反映！

執行指令：

```bash
python main.py
```

**部署到 Railway.app** 🚀

​	1.	將專案推送到 GitHub。

​	2.	在 Railway.app 中建立專案，選擇 GitHub 存儲庫連線。

​	3.	Railway 會根據 ⁠requirements.txt 自動安裝依賴。

​	4.	設定環境變數（在 Railway 的 Dashboard 中設定），內容應與你的 ⁠.env 檔案保持一致。

​	5.	部署完成後，服務將自動運行，並依據排程定時更新股票價格。

**其他資訊** ℹ️

​	•	**Python 版本**：建議使用 Python 3.8+

​	•	**APScheduler**：用於後台定時排程

​	•	**dotenv**：用於讀取 ⁠.env 檔案

趕快試試看，讓你輕鬆掌握股市動態！💪📊

Happy Coding! 😄👍