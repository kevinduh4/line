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
    base_urls = [
        # "https://www.ptt.cc/bbs/baseball/search?q=%E5%87%B1%E7%A8%8B",
        # "https://www.ptt.cc/bbs/baseballxxxx/search?q=%E5%87%B1%E7%A8%8B",
        # "https://www.ptt.cc/bbs/elephants/search?q=%E5%87%B1%E7%A8%8B",
        "https://www.ptt.cc/bbs/BaseballXXXX" #wj
    ]
    matched_posts = []
    max_posts = 10  # 限制最多 5 篇貼文，避免訊息過長

    # 使用 cloudscraper 獲取 cookies
    scraper = cloudscraper.create_scraper()
    response = scraper.get("https://www.ptt.cc/ask/over18")
    cookies = response.cookies.get_dict()

    # 設置 Chrome 選項
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無頭模式，適合 GitHub Actions
    chrome_options.add_argument("--no-sandbox")  # 必須，GitHub Actions 環境需要
    chrome_options.add_argument("--disable-dev-shm-usage")  # 避免共享內存問題
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速 2
    chrome_options.add_argument("--window-size=1920,1080")  # 設置窗口大小 2
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-extensions")  # 禁用擴展 3
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 隱藏 Selenium 特徵 3
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 移除自動化標誌 3



    # 使用 webdriver-manager 自動設置 ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


    try:
        # 先訪問首頁並設置 over18 Cookie
        # driver.get("https://www.ptt.cc/ask/over18")
        driver.get("https://www.ptt.cc/bbs/index.html")
        time.sleep(2)  # 等待頁面加載
        matched_posts.append(page_source) #here
        try:
            yes_button = driver.find_element(By.NAME, "yes")
            yes_button.click()
            time.sleep(2)
        except NoSuchElementException:
            print("未找到 'over18' 按鈕，可能已經設置過或頁面有變化")

        for url in base_urls:
            
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 5))  # 模擬真實用戶等待

                # 在這裡使用 cookies 來繞過 Cloudflare 防護
                for cookie_name, cookie_value in cookies.items():
                    driver.add_cookie({
                        "name": cookie_name,
                        "value": cookie_value,
                        "domain": "www.ptt.cc",  # 設置適當的域名
                    })

                # 刷新頁面以應用 cookies
                driver.refresh()


                page_source = driver.page_source
                # matched_posts.append(page_source) #here
                # 解析貼文
                titles = driver.find_elements(By.CLASS_NAME, "title")
                # matched_posts.append(titles) #here
                time.sleep(10)
                for title in titles:
                    try:
                        a_tag = title.find_element(By.TAG_NAME, "a")
                        post_title = a_tag.text
                        post_url = a_tag.get_attribute("href")
                        post_id = post_url.split('/')[-1].split('.')[1]
                        post_time = datetime.fromtimestamp(int(post_id), timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
                        matched_posts.append("正常拜訪") #here

                        if post_time == today:
                            matched_posts.append(f"{post_title}\n {post_url}\n")
                            if len(matched_posts) >= max_posts:
                                break
                    except Exception as e:
                        print(f"解析單篇貼文時發生錯誤: {e}")
                        continue

            except Exception as e:
                print(f"訪問 {url} 時發生錯誤: {e}")
                continue

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