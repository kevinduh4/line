import os
import requests
from datetime import datetime, timezone, timedelta
import subprocess
import json
import time
import shutil
from instagrapi import Client


# 讀取環境變數
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
RENDER_API_URL = os.getenv("RENDER_API_URL")

# 要爬取的 IG 公開帳號
TARGET_IG_USERNAME = os.getenv("TARGET_IG_USERNAME")


def get_latest_posts():
    print("等待 5 秒以避免速率限制...")
    time.sleep(5)
    cl = Client()
    try:
        # 載入 session
        if os.path.exists("session.json"):
            cl.load_settings("session.json")
            cl.login("IG_USERNAME", "IG_PASSWORD")  # 仍需提供帳號密碼以驗證 session
        else:
            raise FileNotFoundError("session.json 不存在，請確保已上傳到倉庫！")

        user_id = cl.user_id_from_username(TARGET_IG_USERNAME)
        posts = cl.user_medias(user_id, amount=10)
        now = datetime.utcnow()
        time_threshold = now - timedelta(hours=24)
        new_posts = []
        for post in posts:
            post_time = post.taken_at
            if post_time > time_threshold:
                new_posts.append(f"https://www.instagram.com/p/{post.code}/")
        return new_posts
    except Exception as e:
        print(f"爬蟲錯誤: {e}")
        return []

def main():
    try:
        latest_posts = get_latest_posts()
        if latest_posts:
            message = f"{TARGET_IG_USERNAME} 在過去 24 小時內有新貼文！\n" + "\n".join(latest_posts)
            payload = {"message": message}
            response = requests.post(RENDER_API_URL, json=payload)
            if response.status_code == 200:
                print("成功發送到 Render")
            else:
                print(f"發送失敗: {response.status_code} - {response.text}")
        else:
            print("過去 24 小時內無新貼文")
    except Exception as e:
        print(f"執行錯誤: {e}")

if __name__ == "__main__":
    main()