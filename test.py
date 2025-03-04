import time
import random
from datetime import datetime, timezone, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import selenium
print(selenium.__version__)


def get_today_date():
    utc_now = datetime.now(timezone.utc)
    taiwan_tz = timezone(timedelta(hours=8))
    taiwan_now = utc_now.astimezone(taiwan_tz)
    return taiwan_now.strftime("%Y-%m-%d")

def get_ptt_posts(today):
    base_urls = [
        "https://www.ptt.cc/bbs/baseball/search?q=%E5%87%B1%E7%A8%8B",
        "https://www.ptt.cc/bbs/baseballxxxx/search?q=%E5%87%B1%E7%A8%8B",
        "https://www.ptt.cc/bbs/elephants/search?q=%E5%87%B1%E7%A8%8B",
        "https://www.ptt.cc/bbs/BaseballXXXX/search?q=wj"
    ]
    matched_posts = []
    max_posts = 10

    # 使用 Microsoft Edge
    edge_options = Options()
    # 取消 headless 模式以便看到瀏覽器畫面
    # edge_options.add_argument("--headless")  # 若不需要 headless，可註解掉這行
    # edge_options.add_argument("--no-sandbox")
    # edge_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)

    try:
        driver.get("https://www.ptt.cc/ask/over18")
        time.sleep(2)
        try:
            yes_button = driver.find_element(By.NAME, "yes")
            yes_button.click()
            time.sleep(2)
        except NoSuchElementException:
            print("未找到 'over18' 按鈕，可能已經設置過")

        for url in base_urls:
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 5))

                titles = driver.find_elements(By.CLASS_NAME, "title")
                for title in titles:
                    try:
                        a_tag = title.find_element(By.TAG_NAME, "a")
                        post_title = a_tag.text
                        post_url = a_tag.get_attribute("href")

                        post_id = post_url.split('/')[-1].split('.')[1]
                        post_time = datetime.fromtimestamp(int(post_id), timezone(timedelta(hours=8))).strftime("%Y-%m-%d")

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
