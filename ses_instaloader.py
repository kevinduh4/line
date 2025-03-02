import instaloader
import getpass

# 建立 Instaloader 物件
L = instaloader.Instaloader()

# 設置用戶名和密碼（可手動輸入，避免硬編碼帳號密碼）
username = "wscwsc2025"
password = "qqwweerr112233!@"

try:
    # 嘗試使用用戶名和密碼登入
    L.login(username, password)
    print("登入成功！")

except instaloader.exceptions.TwoFactorAuthRequiredException:
    # 如果需要兩步驗證
    print("發現帳號需要兩步驗證，請輸入驗證碼")
    two_factor_code = input("請輸入 Instagram 發送的兩步驗證碼：")
    try:
        # 使用兩步驗證碼繼續登入
        L.two_factor_login(two_factor_code)
        print("兩步驗證成功，繼續執行")
    except Exception as e:
        print("兩步驗證失敗：", e)
        exit(1)

except instaloader.exceptions.ConnectionException as e:
    # 如果遇到 Checkpoint 或其他連線問題
    print("連線錯誤，可能是需要額外驗證:", e)
    if "checkpoint" in str(e).lower():
        print("發現帳號需要進行額外驗證，請到 Instagram 完成驗證")
        print("請在手機或瀏覽器完成驗證後繼續")
        input("驗證完成後按 Enter 繼續...")
        # 重新嘗試登入
        try:
            L.login(username, password)
            print("驗證成功，繼續執行")
        except Exception as e2:
            print("驗證後仍無法登入:", e2)
            exit(1)

except Exception as e:
    # 其他錯誤
    print("登入失敗，檢查是否需要額外驗證:", e)
    exit(1)

# 儲存 session 到新檔案
try:
    L.save_session_to_file(filename="my_instaloader_session")
    print("Session 儲存成功，已保存為 my_instaloader_session")
except Exception as e:
    print("儲存 session 失敗:", e)
    exit(1)