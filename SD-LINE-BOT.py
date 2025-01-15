from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import base64
import logging
from dotenv import load_dotenv
import uuid
import time

# 設置日誌
logging.basicConfig(level=logging.INFO)

# 使用完整路徑加載 .env 文件
dotenv_path = os.path.join(os.getcwd(), '.env')
if not load_dotenv(dotenv_path):
    logging.error(f"Failed to load .env file from {dotenv_path}. Please check the file location and name.")
else:
    logging.info("Successfully loaded .env file.")

# 獲取環境變數
SD_WEBUI_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"  # SD-WebUI API URL
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")  # LINE Channel Access Token
NGROK_URL = os.getenv("NGROK_URL")  # Ngrok URL

if LINE_CHANNEL_ACCESS_TOKEN is None or NGROK_URL is None:
    logging.error("Environment variables LINE_CHANNEL_ACCESS_TOKEN or NGROK_URL are not set.")
    exit(1)
else:
    logging.info(f"Loaded LINE_CHANNEL_ACCESS_TOKEN: {LINE_CHANNEL_ACCESS_TOKEN}")
    logging.info(f"Loaded NGROK_URL: {NGROK_URL}")

IMAGE_DIR = os.path.join(os.getcwd(), 'SD', '01_py', 'images')

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# 記錄用戶生成圖片的時間
user_last_request_time = {}

# 初始化 Flask 應用
app = Flask(__name__, static_folder=IMAGE_DIR)  # 指定靜態文件夾

# LINE Bot 回覆函數
def line_reply(reply_token, message, is_image=False):
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "replyToken": reply_token,
        "messages": []
    }
    if is_image:
        payload["messages"].append({
            "type": "image",
            "originalContentUrl": message,
            "previewImageUrl": message
        })
    else:
        payload["messages"].append({
            "type": "text",
            "text": message
        })

    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=payload)
    if response.status_code != 200:
        logging.error(f"Failed to reply to LINE: {response.text}")

@app.route('/')
def index():
    return "LINE Bot is running!"

@app.route('/callback', methods=['POST'])
def callback():
    body = request.json
    logging.info(f'Received body: {body}')

    if 'events' not in body:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    for event in body['events']:
        if event.get('type') == 'message':
            user_message = event['message']['text']
            reply_token = event['replyToken']
            user_id = event['source']['userId']
            current_time = time.time()

            logging.info(f'User message: {user_message}, User ID: {user_id}, Reply Token: {reply_token}')

            # 檢查用戶是否已經發送過生成圖片的請求
            last_request_time = user_last_request_time.get(user_id, 0)
            if current_time - last_request_time < 10:  # 限制每 10 秒生成一次圖片
                line_reply(reply_token, "請稍等，您發送的請求過於頻繁。")
                continue

            # 更新用戶的請求時間
            user_last_request_time[user_id] = current_time

            # 檢查用戶消息
            if user_message.startswith("--prompt"):
                # 使用 txt2img 生成圖像
                try:
                    sd_response = requests.post(SD_WEBUI_URL, json={
                        "prompt": user_message.replace("--prompt ", ""),
                        "num_images": 1
                    })

                    if sd_response.status_code == 200:
                        response_data = sd_response.json()
                        logging.info(f"Response data from SD-WebUI: {response_data}")

                        if 'images' in response_data and isinstance(response_data['images'], list) and len(response_data['images']) > 0:
                            image_data = response_data['images'][0]

                            if isinstance(image_data, str):
                                image_bytes = base64.b64decode(image_data)

                                # 使用 UUID 隨機命名圖片
                                unique_filename = f"{uuid.uuid4()}.png"
                                image_filename = os.path.join(IMAGE_DIR, unique_filename)
                                
                                with open(image_filename, 'wb') as f:
                                    f.write(image_bytes)

                                if os.path.exists(image_filename):
                                    image_url = f"{NGROK_URL}/SD/01_py/images/{unique_filename}"
                                    logging.info(f"Generated image URL: {image_url}")
                                    line_reply(reply_token, image_url, is_image=True)  # 自動回復圖片
                                else:
                                    logging.error("Image was not saved.")
                                    line_reply(reply_token, "圖片生成成功，但無法保存。")
                            else:
                                logging.error("Image data is not a string.")
                                line_reply(reply_token, "生成圖片時出錯，請稍後再試。")
                        else:
                            logging.error("No valid images received from SD-webui.")
                            line_reply(reply_token, "未能生成圖片，請稍後再試。")
                    else:
                        logging.error(f"SD-webui returned unexpected status: {sd_response.status_code}")
                        line_reply(reply_token, "生成圖片時出錯，請稍後再試。")

                except Exception as e:
                    logging.error(f"Error during image generation: {e}")
                    line_reply(reply_token, "生成圖片時出錯，請稍後再試。")

            elif user_message == "生成圖像":
                line_reply(reply_token, "請輸入英文提示詞以生成圖像，請以 '--prompt' 開頭。")
            else:
                line_reply(reply_token, "請輸入有效的英文提示詞來開始。")

    return jsonify({'status': 'ok'})

@app.route('/SD/01_py/images/<path:filename>', methods=['GET'])
def send_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == '__main__':
    app.run(port=8080)