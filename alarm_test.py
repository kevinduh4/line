from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# 設定 Edge WebDriver
options = webdriver.EdgeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-software-rasterizer")
# options.add_argument("--headless")  # 測試時可開啟無頭模式

# 啟動 WebDriver
service = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service, options=options)

# 目標網址
url = "https://www.cpbl.com.tw/"
driver.get(url)

try:
    # 等待頁面載入
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.team_name a"))
    )

    # 查找所有比賽的主隊和客隊
    teams = driver.find_elements(By.CSS_SELECTOR, "div.team")

    for team in teams:
        try:
            team_name_element = team.find_element(By.XPATH, ".//div[@class='team_name']/a[@href='/team/index?teamNo=ACN011']")
            team_name = team_name_element.text.strip()

            print("中信兄弟連結:", team_name_element.get_attribute("href"))

                # 嘗試尋找比賽時間
            try:
                match_info = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.PlaceInfo div.time"))
                )
                match_time = match_info.text.strip()  # 直接抓取文本內容
                print("比賽時間:", match_time)
                match_no1 = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.Tags div.tag.game_no a"))
                )
                match_no2 = match_no1.text.strip()  # 直接抓取文本內容
                print("比賽編號:", match_no2)
            except Exception as e:
                print("找不到比賽時間，可能需要更新 XPath")

            break
        except Exception as e:
            print(f"發生錯誤: {e}")

except Exception as e:
    print(f"發生錯誤，無法找到比賽資訊: {e}")

# 關閉 WebDriver
driver.quit()
