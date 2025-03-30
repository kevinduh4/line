from selenium import webdriver
# from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
import pyimgur
import os
import requests
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Imgur API 設定
CLIENT_ID = os.getenv("IMGUR_CLIENT_ID") #沒用到了，改用imgbb
IMAGE_PATH = "prChart_svg.png"
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")


def capture_svg_screenshot(url, save_path):
    """使用 Selenium 擷取 SVG 截圖並儲存"""
    # options = webdriver.EdgeOptions()
    # options.add_argument("--headless")  # 無頭模式
    # options.add_argument("--window-size=1920,1080")  # 避免 SVG 沒載入

    # service = Service(EdgeChromiumDriverManager().install())
    # driver = webdriver.Edge(service=service, options=options)

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



    driver.get(url)
    time.sleep(2)

    try:
        # 等待 SVG 載入
        svg_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.prChart svg"))
        )

        # 隱藏 navbar 以防擋住 SVG
        driver.execute_script("document.getElementById('navbar-wrapper').style.display = 'none';")

        # 捲動到 SVG 位置
        driver.execute_script("arguments[0].scrollIntoView();", svg_element)
        time.sleep(2)

        # 擷取 SVG 截圖
        svg_element.screenshot(save_path)
        print(f"已儲存 SVG 截圖：{save_path}")

    except Exception as e:
        print("擷取 SVG 失敗:", e)

    finally:
        driver.quit()


# def upload_to_imgur(image_path, client_id):
#     """將圖片上傳到 Imgur 並回傳短網址"""
#     im = pyimgur.Imgur(client_id)
#     uploaded_image = im.upload_image(image_path, title="prChart Screenshot")
#     print("圖片短網址:", uploaded_image.link)
#     return uploaded_image.link

def upload_to_imgbb(image_path, api_key):
    """使用 ImgBB API 上傳圖片並回傳圖片連結"""
    url = "https://api.imgbb.com/1/upload"
    with open(image_path, "rb") as file:
        payload = {"key": api_key}
        files = {"image": file}  # 這裡應該用 "image"，符合 ImgBB API
        response = requests.post(url, data=payload, files=files)

    if response.status_code == 200:
        image_data = response.json()["data"]
        print("完整 API 回傳:", response.json())  # ✅ 新增這一行來檢查
        return image_data["display_url"]  # ✅ 這裡會回傳 .png 結尾的連結
    else:
        print("上傳失敗:", response.text)
        return None


if __name__ == "__main__":
    # 設定目標網址
    target_url = "https://www.rebas.tw/player/b76lK"

    # 擷取圖片
    capture_svg_screenshot(target_url, IMAGE_PATH)

    # 上傳到 Imgur
    # imgur_url = upload_to_imgur(IMAGE_PATH, CLIENT_ID)
    # print("最終圖片連結:", imgur_url)


    # 上傳到 ImgBB
    imgur_url = upload_to_imgbb(IMAGE_PATH, IMGBB_API_KEY)
    print("圖片短網址:", imgur_url)

    render_api_url = f"{os.getenv('RENDER_API_URL')}/rebas_pr"
    payload = {"image_url": imgur_url}
    try:
        response = requests.post(render_api_url, json=payload, timeout=30)
        print("成功發送到 API:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("發送失敗:", str(e))
