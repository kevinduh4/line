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

def get_latest_post():
    loader = instaloader.Instaloader()
    loader.login(IG_USERNAME, IG_PASSWORD)  # 登入 IG
    profile = instaloader.Profile.from_username(loader.context, TARGET_IG_USERNAME)

    # 設定查詢時間範圍（過去 24 小時）
    now = datetime.now(taiwan_tz)
    past_24_hours = now - timedelta(days=1)

    for post in profile.get_posts():
        post_date = post.date.replace(tzinfo=timezone.utc).astimezone(taiwan_tz)

        # **修正：抓過去 24 小時內的貼文**
        if post_date >= past_24_hours:
            return post.url  # 回傳最新貼文網址
        break  # 只檢查最新的貼文，不往回搜尋

    return None

def notify_line_bot(post_url):
    if not post_url:
        print(" 過去 24 小時內沒有新貼文")
        return

    payload = {"message": f" {TARGET_IG_USERNAME} 發布了新貼文！ {post_url}"}
    response = requests.post(RENDER_API_URL, json=payload)
    
    if response.status_code == 200:
        print("成功通知 LINE Bot")
    else:
        print("通知失敗:", response.text)

if __name__ == "__main__":
    latest_post = get_latest_post()
    notify_line_bot(latest_post)