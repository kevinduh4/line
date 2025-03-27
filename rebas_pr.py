from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import pyimgur
import os
import requests

# Imgur API 設定
CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
IMAGE_PATH = "prChart_svg.png"


def capture_svg_screenshot(url, save_path):
    """使用 Selenium 擷取 SVG 截圖並儲存"""
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")  # 無頭模式
    options.add_argument("--window-size=1920,1080")  # 避免 SVG 沒載入

    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)

    driver.get(url)

    try:
        # 等待 SVG 載入
        svg_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.prChart svg"))
        )

        # 隱藏 navbar 以防擋住 SVG
        driver.execute_script("document.getElementById('navbar-wrapper').style.display = 'none';")

        # 捲動到 SVG 位置
        driver.execute_script("arguments[0].scrollIntoView();", svg_element)

        # 擷取 SVG 截圖
        svg_element.screenshot(save_path)
        print(f"已儲存 SVG 截圖：{save_path}")

    except Exception as e:
        print("擷取 SVG 失敗:", e)

    finally:
        driver.quit()


def upload_to_imgur(image_path, client_id):
    """將圖片上傳到 Imgur 並回傳短網址"""
    im = pyimgur.Imgur(client_id)
    uploaded_image = im.upload_image(image_path, title="prChart Screenshot")
    print("圖片短網址:", uploaded_image.link)
    return uploaded_image.link


if __name__ == "__main__":
    # 設定目標網址
    target_url = "https://www.rebas.tw/player/b76lK"

    # 擷取圖片
    capture_svg_screenshot(target_url, IMAGE_PATH)

    # 上傳到 Imgur
    imgur_url = upload_to_imgur(IMAGE_PATH, CLIENT_ID)
    print("最終圖片連結:", imgur_url)

    render_api_url = f"{os.getenv("RENDER_API_URL")}/rebas_pr"
    payload = {"image_url": imgur_url}
    try:
        response = requests.post(render_api_url, json=payload, timeout=30)
        print("成功發送到 API:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("發送失敗:", str(e))
