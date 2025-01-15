# SD-LINE-BOT Flask App

這是一個使用 Flask 構建的 LINE Bot 應用程式，能夠生成圖像並回覆用戶。這個應用程式集成了 SD-WebUI API，允許用戶通過 LINE 與應用程式互動，並生成基於提示的圖像。

## 功能

- 通過 LINE Bot 接受用戶消息
- 使用 SD-WebUI API 生成圖像
- 回覆用戶生成的圖像或文本消息
- 限制用戶請求頻率，避免過多請求

## 技術棧

- Python
- Flask
- LINE Messaging API
- SD-WebUI API
- dotenv (環境變數管理)
- ngrok_url
  
![LINE-BOT生成圖像](https://github.com/githubde1017/sd-line-bot/blob/main/sd-img-bot-userguide.jpg)

## 設置

### 先決條件

- 確保您已經安裝了 Python 3.x 和 pip。
- 確保您已經安裝 sd-webui-forge(https://github.com/lllyasviel/stable-diffusion-webui-forge) or Stable Diffusion(https://github.com/AUTOMATIC1111/stable-diffusion-webui)。

### 克隆專案

1. 克隆這個庫：
   ```bash
   git clone https://github.com/githubde1017/sd-line-bot.git
   cd sd-line-bot

### 安裝依賴包
2. 安裝所需的依賴包：
    ```bash
    pip install -r requirements.txt

### 配置環境變數
3. 創建 .env 文件並添加您的環境變數：
    ```bash
    LINE_CHANNEL_ACCESS_TOKEN=your_access_token
    NGROK_URL=https://your-ngrok-url
    LINE_CHANNEL_ACCESS_TOKEN：您的 LINE 頻道訪問令牌。
    NGROK_URL：您的 Ngrok URL。

### 運行應用程式
4. 運行應用程式：
    ```bash
    python sd-line-bot.py
    
應用程式將在 http://localhost:8080 上運行。

### 使用說明
- 當應用程式運行後，您可以通過 LINE 與 Bot 互動。用戶可以發送以 --prompt 開頭的消息來生成圖像，例如：

--prompt a cute cat,

## 注意事項
- 確保 .env 文件不被上傳到 Git，以保護您的敏感資料。
- 每次更新 .env 文件後，需要重新啟動應用程式以加載新的環境變數。

## 貢獻
### 歡迎任何貢獻！請提出問題或提交拉取請求。

## 授權
### 本專案使用 MIT 授權，詳情請參見 LICENSE 文件。

您可以根據實際情況修改內容。如果有其他問題或需要進一步的幫助，請告訴我！
