import cloudscraper
import time
import random
from datetime import datetime, timezone, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def get_today_date():
    # 獲取當前 UTC 時間並轉換到台灣時區
    utc_now = datetime.now(timezone.utc)
    taiwan_tz = timezone(timedelta(hours=8))
    taiwan_now = utc_now.astimezone(taiwan_tz)
    return taiwan_now.strftime("%Y-%m-%d")

def get_ptt_posts(today):
    matched_posts = []
    max_posts = 10

    # 使用 cloudscraper 獲取 cookies
    scraper = cloudscraper.create_scraper()
    response = scraper.get("https://www.instagram.com/k.c.wang_15/")
    cookies = response.cookies.get_dict()

    # 設置 Chrome 選項
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 將 cloudscraper 的 cookies 應用到 Selenium
        driver.get("https://www.instagram.com/")  # 先訪問根域名以設置 cookies
        for cookie_name, cookie_value in cookies.items():
            driver.add_cookie({"name": cookie_name, "value": cookie_value, "domain": ".instagram.com"})
        
        # 訪問目標頁面
        driver.get("https://www.instagram.com/k.c.wang_15/")
        time.sleep(5)  # 增加等待時間，讓頁面完全加載

        # 檢查當前 URL 和標題
        current_url = driver.current_url
        page_title = driver.title
        page_source = driver.page_source

        print(f"當前 URL: {current_url}")
        print(f"頁面標題: {page_title}")
        matched_posts.append(page_source)

        # 簡單判斷是否被重定向到登入頁面
        if "login" in current_url.lower() or "Login" in page_title:
            print("可能被重定向到登入頁面")
        elif "k.c.wang_15" in page_title:
            print("成功訪問目標用戶頁面")
        else:
            print("未知狀態，請檢查 page_source")

    finally:
        driver.quit()

    return matched_posts

def main():
    try:
        # 在程式開始時固定當天的日期
        today = get_today_date()
        latest_posts = get_ptt_posts(today)
        if latest_posts:
            print("今日 PTT 熱議:")
            for post in latest_posts:
                print(post)
        else:
            print("今天沒有新貼文")
    except Exception as e:
        print(f"執行錯誤: {e}")
        exit(1)

if __name__ == "__main__":
    main()