from googleapiclient.discovery import build # API client library
from googleapiclient.errors import HttpError
import datetime
import csv
import os
import requests


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
DEVELOPER_KEY = YOUTUBE_API_KEY
youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)
RENDER_API_URL = os.getenv("RENDER_API_URL")
api_url = f"{RENDER_API_URL}/notify_youtube"


# channel_id_list = ['UCMNRAapvcYtQks_QmfiTGkA']
channel_id_list = os.getenv("channel_id_list")

# 取得頻道的影片清單（只取第一頁）
def get_channel_videos(channel_id):
    # 取得頻道的 "Uploads" 播放清單 ID
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()
    
    if not response["items"]:
        print(f"⚠️ 無法找到頻道 {channel_id}")
        return []

    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # 只請求第一頁的影片（最多 50 部）
    playlist_request = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=50  # 取最多 50 部影片
    )
    playlist_response = playlist_request.execute()

    videos = [
        {
            'title': item['snippet']['title'],
            'upload_time': item['snippet']['publishedAt'],
            'short_url': f"https://youtu.be/{item['snippet']['resourceId']['videoId']}"
        }
        for item in playlist_response.get("items", [])
    ]

    return videos


# 產生或更新 CSV 檔案（新影片插入最前面）
def save_to_csv(channel_id, videos):
    filename = "brothers_videos.csv"

    # 讀取現有的 CSV 檔案（如果存在）
    existing_videos = []
    if os.path.exists(filename):
        with open(filename, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            existing_videos = list(reader)  # 轉成 list 方便排序

    # 用 short_url 建立 set 判斷影片是否已存在
    existing_urls = {video["short_url"] for video in existing_videos}
    
    # 過濾出新的影片
    new_videos = [video for video in videos if video["short_url"] not in existing_urls]

    if not new_videos:
        print("沒有新影片，無需更新。")
        return

    # 1️⃣ 檢查是否有標題包含「凱程」的影片
    keyword_videos = [video for video in new_videos if "凱程" in video["title"]]

    # 2️⃣ 發送 HTTP POST 給 Flask，請 Flask 負責推播 LINE
    if keyword_videos:
        message_text = "📢快來欣賞凱程的精彩鏡頭！\n"
        for video in keyword_videos:
            message_text += f"\n {video['title']}\n {video['short_url']}\n"

        # 發送 POST 請求給 Flask API
        try:
            response = requests.post(api_url, json={"message": message_text})
            if response.status_code == 200:
                print("成功通知 Flask 伺服器，讓 LINE Bot 推播")
            else:
                print(f"通知 Flask 失敗: {response.text}")
        except Exception as e:
            print(f"發送 HTTP POST 給 Flask 時出錯: {str(e)}")


    # 合併新舊影片，並根據上傳時間排序（降冪）
    all_videos = new_videos + existing_videos  # 新的影片放前面
    all_videos.sort(key=lambda x: x["upload_time"], reverse=True)  # 依據 upload_time 降冪排序

    # 覆寫 CSV，確保新影片在最前面
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "upload_time", "short_url"])
        writer.writeheader()
        writer.writerows(all_videos)

    print(f"新增 {len(new_videos)} 部新影片，已更新 {filename}")

# 主程式
for channel_id in channel_id_list:
    print(f"正在處理頻道: {channel_id}")
    videos = get_channel_videos(channel_id)

    if videos:
        save_to_csv(channel_id, videos)
    else:
        print(f"{channel_id} 無法獲取影片資訊，請檢查頻道 ID 是否正確。")