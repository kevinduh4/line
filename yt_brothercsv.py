from googleapiclient.discovery import build # API client library
from googleapiclient.errors import HttpError
import datetime
import csv
import os


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
DEVELOPER_KEY = YOUTUBE_API_KEY
youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)


# channel_id_list = ['UCMNRAapvcYtQks_QmfiTGkA']
channel_id_list = os.getenv("channel_id_list")

def get_channel_videos(channel_id):
    # 獲取頻道的 "Uploads" 播放清單 ID
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()

    # 從回應中提取上傳播放清單 ID
    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # 獲取播放清單中的影片
    videos = []
    next_page_token = None

    while True:
        playlist_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,  # 每頁最多 50 個結果，可調整
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()

        for item in playlist_response['items']:
            video_info = {
                'title': item['snippet']['title'],
                'upload_time': item['snippet']['publishedAt'],
                'short_url': f"https://youtu.be/{item['snippet']['resourceId']['videoId']}"
            }
            videos.append(video_info)

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break  # 沒有下一頁就結束

    return videos

# 產生 CSV 檔案
def save_to_csv(channel_id, videos):
    today_date = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"brothers_videos.csv"

    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "upload_time", "short_url"])
        writer.writeheader()
        writer.writerows(videos)

    print(f"資料已儲存至 {filename}")

# 主程式
for channel_id in channel_id_list:
    print(f"正在處理頻道: {channel_id}")
    videos = get_channel_videos(channel_id)

    if videos:
        save_to_csv(channel_id, videos)
    else:
        print(f"{channel_id} 無法獲取影片資訊，請檢查頻道 ID 是否正確。")