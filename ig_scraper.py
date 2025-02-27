import os
import instaloader
import requests
from datetime import datetime, timezone, timedelta

# 讀取環境變數
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
RENDER_API_URL = os.getenv("RENDER_API_URL")

# 要爬取的 IG 公開帳號
TARGET_IG_USERNAME = os.getenv("TARGET_IG_USERNAME")

# 設定台灣時區
taiwan_tz = timezone(timedelta(hours=8))

def get_latest_posts():
    loader = instaloader.Instaloader(request_timeout=60)
    # loader.login(IG_USERNAME, IG_PASSWORD)  # 登入 IG
    profile = instaloader.Profile.from_username(loader.context, TARGET_IG_USERNAME)

    now = datetime.now(taiwan_tz)
    past_24_hours = now - timedelta(days=1)
    
    post_urls = []

    for post in profile.get_posts():
        post_date = post.date.replace(tzinfo=timezone.utc).astimezone(taiwan_tz)
        if post_date >= past_24_hours:
            post_urls.append(post.url)  # 儲存所有 24 小時內的貼文
        else:
            break  # 只要遇到 24 小時前的貼文，就停止

    return post_urls

def notify_line_bot(post_urls):
    if not post_urls:
        print("過去 24 小時內沒有新貼文")
        return

    for url in post_urls:
        payload = {"message": f"{TARGET_IG_USERNAME} \n發布了新貼文！ {url}"}
        response = requests.post(RENDER_API_URL, json=payload)
        
        if response.status_code == 200:
            print(f"成功通知 LINE Bot: {url}")
        else:
            print(f"通知失敗: {response.text}")

if __name__ == "__main__":
    latest_posts = get_latest_posts()
    notify_line_bot(latest_posts)
