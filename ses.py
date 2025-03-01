from instagrapi import Client

cl = Client()

try:
    cl.login("id", "password")
except Exception as e:
    print("登入失敗，檢查是否需要額外驗證:", e)

    # 如果遇到 Checkpoint，手動解決驗證
    if cl.last_json.get("message") == "challenge_required":
        print("發現帳號需要進行額外驗證，請依指示完成驗證")
        
        challenge_url = cl.last_json["challenge"]["api_path"]
        print(f"請到 Instagram 確認安全驗證: {challenge_url}")

        # 等待用戶手動驗證
        input("請在手機上完成 Instagram 的驗證後，按 Enter 繼續...")
        
        # 嘗試解決驗證
        cl.challenge_resolve(challenge_url)
        print("驗證成功，繼續執行")

# 存取 session
cl.dump_settings("session.json")
print("Session 存儲成功")
