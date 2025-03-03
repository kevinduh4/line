from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, ImageSendMessage, AudioSendMessage
from dotenv import load_dotenv
from linebot.exceptions import LineBotApiError
import os
import random
import json



app = Flask(__name__)

# 設定 LINE Bot 的 Channel Access Token 和 Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 你的 LINE 使用者 ID
LINE_USER_ID = os.getenv("LINE_USER_ID")





@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK", 200






# 讀取 JSON 檔案中的圖片 URL
def load_image_gallery():
    with open('images.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data["image_gallery"]

# 圖庫
image_gallery = load_image_gallery()

text_responses = {
    "大谷翔平": "2026WBC等著被我三振",
    "自我介紹": "你好，我是凱程鬧鐘，我會提醒你準時收看，\n鐵漢柔情!王凱程!"
}

audio_responses = {
    # "asmr": "https://on.soundcloud.com/zR6SWtgavphGNJ1z5"
    "asmr" : "https://dl.dropboxusercontent.com/scl/fi/n663bzcn4itd3notonu0g/asmr_final-online-audio-converter.com.m4a?rlkey=puiw8cvvvkh892uxvcajcvc04"
}

image_responses = {
    "陳重羽": "https://i.imgur.com/8zghr6d.jpeg",  # 替換為實際的圖片 URL
    "跨": "https://i.imgur.com/Nc9DaqP.png"  # 替換為實際的圖片 URL
}





# ---------------加好友後發訊息
@handler.add(FollowEvent)
def handle_follow(event):
    # 用戶加為好友後，發送歡迎訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="你好，我是凱程鬧鐘，我會提醒你準時收看，\n鐵漢柔情!王凱程!")
    )



# --------------爬蟲，凱程ig發文便推送-------壞掉，基本做不到
@app.route("/notify_ig_post", methods=["POST"])
def notify_ig_post():
    data = request.get_json()
    message = data.get("message", "Instagram 爬蟲通知失敗")

    try:
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message))
        return jsonify({"status": "success", "message": "通知已發送"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
# --------------爬蟲，凱程ptt發文便推送
@app.route("/notify_ptt_post", methods=["POST"])
def notify_ptt_post():
    data = request.get_json()
    message = data.get("message", "PTT 爬蟲通知失敗")

    try:
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message))
        return jsonify({"status": "success", "message": "通知已發送"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# ------------------回覆訊息功能

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.lower()
    # 當用戶輸入 "抽" 時，隨機選擇一張圖片回傳
    if "抽" in user_msg:
        selected_image_url = random.choice(image_gallery)  # 隨機選擇圖片
        try:
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=selected_image_url,
                    preview_image_url=selected_image_url  # 預覽圖像使用相同的 URL
                )
            )
        except LineBotApiError as e:
            print("圖片回應錯誤:", e)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="圖片回應失敗。"))

        # 先檢查是否為音訊關鍵字
    if user_msg in audio_responses:
        try:
            audio_url = audio_responses[user_msg]
            line_bot_api.reply_message(
                event.reply_token,
                AudioSendMessage(
                    original_content_url=audio_url,
                    duration=20000  # 設定音訊持續時間（以毫秒為單位），這裡設為 1 分鐘
                )
            )
        except LineBotApiError as e:
            print("音訊回應錯誤:", e)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="音訊回應失敗。"))
        return

    # 再檢查是否為圖片關鍵字
    if user_msg in image_responses:
        try:
            image_url = image_responses[user_msg]
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url  # 預覽圖像使用相同的 URL
                )
            )
        except LineBotApiError as e:
            print("圖片回應錯誤:", e)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="圖片回應失敗。"))
        return

    # 默認文字回應
    reply_msg = text_responses.get(user_msg, "抱歉，凱程忙著重訓，現在無法抽空回應，\n請繼續支持鐵漢柔情!王凱程!")
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 預設 5000，但 Render 會動態設定 PORT
    app.run(host="0.0.0.0", port=port)
