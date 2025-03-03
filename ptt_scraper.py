import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import time

def get_today_date():
    # 獲取當前 UTC 時間並轉換到台灣時區
    utc_now = datetime.now(timezone.utc)
    taiwan_tz = timezone(timedelta(hours=8))
    taiwan_now = utc_now.astimezone(taiwan_tz)
    return taiwan_now.strftime("%Y-%m-%d")

def get_ptt_posts(today):
    base_urls = [
        "https://www.ptt.cc/bbs/baseball/search?q=%E5%87%B1%E7%A8%8B",
        "https://www.ptt.cc/bbs/baseballxxxx/search?q=%E5%87%B1%E7%A8%8B",
        "https://www.ptt.cc/bbs/elephants/search?q=%E5%87%B1%E7%A8%8B"
    ]
    matched_posts = []
    max_posts = 10  # 限制最多 5 篇貼文，避免訊息過長

    for url in base_urls:
        try:
            response = requests.get(url, cookies={"over18": "1"}, timeout=10)  # 添加超時
            if response.status_code != 200:
                print(f"無法訪問 {url}，狀態碼：{response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            
            for title_div in soup.find_all("div", class_="title"):
                a_tag = title_div.find("a")
                if a_tag:
                    post_url = "https://www.ptt.cc" + a_tag["href"]
                    post_id = a_tag["href"].split("/")[-1].split(".")[1]
                    post_time = datetime.fromtimestamp(int(post_id), timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
                    
                    if post_time == today:
                        matched_posts.append(f"{a_tag.text}: {post_url}")
                        if len(matched_posts) >= max_posts:  # 限制貼文數量
                            break
            
            time.sleep(3)  # 每個看板之間等待，避免過快請求
        
        except Exception as e:
            print(f"訪問 {url} 時發生錯誤: {e}")
            continue
    
    return matched_posts

def main():
    try:
        # 在程式開始時固定當天的日期
        today = get_today_date()
        latest_posts = get_ptt_posts(today)
        if latest_posts:
            print("今天的新貼文：")
            for post in latest_posts:
                print(post)
        else:
            print("今天沒有新貼文")
    except Exception as e:
        print(f"執行錯誤: {e}")
        exit(1)

if __name__ == "__main__":
    main()