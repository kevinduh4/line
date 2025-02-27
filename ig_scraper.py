import os
import requests
from datetime import datetime, timezone, timedelta
import subprocess
import json
import time
import shutil




# 讀取環境變數
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
RENDER_API_URL = os.getenv("RENDER_API_URL")

# 要爬取的 IG 公開帳號
TARGET_IG_USERNAME = os.getenv("TARGET_IG_USERNAME")


def get_latest_posts():
    # 在執行爬取前加入延遲，避免過快請求
    print("等待 5 秒以避免速率限制...")
    time.sleep(5)

    # 執行 instagram-scraper 命令，抓取最新 10 篇貼文
    try:
        subprocess.run([
            "instagram-scraper", TARGET_IG_USERNAME,
            "--media-types", "none",  # 只抓貼文基本資訊，不下載媒體
            "--maximum", "10",       # 限制抓取數量
            "--destination", "temp_data"  # 輸出到臨時資料夾
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"instagram-scraper 執行失敗: {e}")
        return []

    # 讀取輸出的 JSON 文件
    json_file = f"temp_data/{TARGET_IG_USERNAME}.json"
    if not os.path.exists(json_file):
        print(f"未找到 {json_file}")
        return []

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 計算 24 小時前的時間
    now = datetime.utcnow()
    time_threshold = now - timedelta(hours=24)

    # 過濾過去 24 小時的貼文
    new_posts = []
    for post in data["GraphImages"]:
        post_time = datetime.fromtimestamp(post["taken_at_timestamp"])
        if post_time > time_threshold:
            post_url = f"https://www.instagram.com/p/{post['shortcode']}/"
            new_posts.append(post_url)

    return new_posts

def main():
    try:
        latest_posts = get_latest_posts()
        if latest_posts:
            # 格式化訊息，準備發送到 Line Bot
            message = f"{TARGET_IG_USERNAME} 在過去 24 小時內有新貼文！\n" + "\n".join(latest_posts)
            payload = {"message": message}
            response = requests.post(RENDER_API_URL, json=payload)
            if response.status_code == 200:
                print("成功發送到 Render，Line 通知已觸發")
            else:
                print(f"發送到 Render 失敗: {response.status_code} - {response.text}")
        else:
            print("過去 24 小時內無新貼文")
    except Exception as e:
        print(f"執行錯誤: {e}")
    finally:
        # 清理臨時資料夾
        print("清理臨時檔案...")
        shutil.rmtree("temp_data", ignore_errors=True)

if __name__ == "__main__":
    main()