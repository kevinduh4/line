import os
import requests
from datetime import datetime, timezone, timedelta
import subprocess
import json
import time
import shutil
import instaloader
import pickle



# 讀取環境變數
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
RENDER_API_URL = os.getenv("RENDER_API_URL")

# 要爬取的 IG 公開帳號
TARGET_IG_USERNAME = os.getenv("TARGET_IG_USERNAME")

# 檢查環境變數是否存在
if not all([IG_USERNAME, IG_PASSWORD, RENDER_API_URL, TARGET_IG_USERNAME]):
    print("錯誤：請確保設置了所有必要的環境變數（IG_USERNAME, IG_PASSWORD, RENDER_API_URL, TARGET_IG_USERNAME）")
    exit(1)

# 定義 session 檔案路徑（用於 instaloader）
current_dir = os.path.dirname(os.path.abspath(__file__))
instaloader_session_file = os.path.join(current_dir, "my_instaloader_session")

# 初始化 Instaloader 物件
L = instaloader.Instaloader()





# 嘗試載入或生成 Instaloader session
def ensure_instaloader_session():
    global L
    loaded_session = False

    # 檢查 session 檔案是否存在
    if os.path.exists(instaloader_session_file):
        try:
            with open(instaloader_session_file, "rb") as f:
                session = pickle.load(f)
            
            # 設置 session
            L.context._session = session
            print("成功載入 Instaloader session！")

            # 簡單請求以驗證 session 是否有效
            L.context.get_anonymous_session()
            if not L.context.username:
                print("無法獲取當前登入用戶，session 可能無效")
                raise Exception("用戶名為 None")

            loaded_session = True
            print(f"目前登入的 Instaloader 用戶是：{L.context.username}")

        except Exception as e:
            print("載入或驗證 Instaloader session 失敗:", e)
            print("嘗試重新生成 session...")

    # 如果 session 無效或不存在，重新登入並生成新 session
    if not loaded_session:
        print("嘗試從環境變數重新登入並生成新 Instaloader session...")
        try:
            L.login(IG_USERNAME, IG_PASSWORD)
            print("Instaloader 登入成功！")
            L.save_session_to_file(filename=instaloader_session_file)
            print(f"已儲存新 Instaloader session 到 {instaloader_session_file}")
        except Exception as e:
            print("Instaloader 重新登入失敗:", e)
            print("可能需要檢查帳號是否啟用了兩步驗證或是否被 Instagram 限制")
            exit(1)

# 爬取最新貼文的函數（使用 instaloader）
def get_latest_posts():
    print("等待 5 秒以避免速率限制...")
    time.sleep(5)  # 增加延遲時間，避免反爬蟲

    try:
        print(f"抓取 {TARGET_IG_USERNAME} 的貼文...")
        profile = instaloader.Profile.from_username(L.context, TARGET_IG_USERNAME)
        
        posts = []
        count = 0
        for post in profile.get_posts():
            if count >= 10:  # 限制抓取 10 篇貼文
                break
            posts.append(post)
            count += 1

        if not posts:
            print("未抓取到貼文，可能是帳號隱私設置或存取權限問題")
            return []

        now = datetime.now(timezone.utc)
        time_threshold = now - timedelta(hours=24)
        new_posts = []
        for post in posts:
            post_time = post.date_utc
            if post_time > time_threshold:
                new_posts.append(f"https://www.instagram.com/p/{post.shortcode}/")
        return new_posts

    except Exception as e:
        print(f"Instaloader 爬蟲錯誤: {e}")
        return []

def main():
    try:
        # 確保 Instaloader session 有效
        ensure_instaloader_session()

        # 使用 instaloader 爬取最新貼文
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
        exit(1)

if __name__ == "__main__":
    main()