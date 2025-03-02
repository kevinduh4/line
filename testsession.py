import instaloader
import os.path
import pickle
import getpass

# 獲取當前程式碼所在的目錄（根目錄）
current_dir = os.path.dirname(os.path.abspath(__file__))
session_file = os.path.join(current_dir, "my_instaloader_session")

# 建立 Instaloader 物件
L = instaloader.Instaloader()

# 檢查 session 檔案是否存在
if not os.path.exists(session_file):
    print(f"找不到 session 檔案：{session_file}")
    print("請先執行 generate_session.py 來生成檔案")
    exit(1)

# 手動載入 session 檔案
try:
    # 因為 session 是用 pickle 儲存的，直接讀取
    with open(session_file, "rb") as f:
        session = pickle.load(f)
    
    # 將 session 設置到 Instaloader
    L.context._session = session
    print("成功載入 session！")

    # 檢查用戶名是否為 None，並嘗試簡單請求驗證 session
    if not L.context.username:
        print("無法獲取當前登入用戶，session 可能無效或過期")
        print("嘗試重新登入...")
        username = input("請輸入 Instagram 用戶名：")
        password = getpass.getpass("請輸入 Instagram 密碼：")
        try:
            L.login(username, password)
            L.save_session_to_file(filename=session_file)
            print("已重新登入並儲存新 session")
        except Exception as e:
            print("重新登入失敗:", e)
            exit(1)

    # 測試 session 是否有效，例如獲取用戶資訊
    profile = instaloader.Profile.from_username(L.context, L.context.username)
    print(f"目前登入的用戶是：{profile.username}")

except Exception as e:
    print("載入 session 失敗:", e)
    exit(1)