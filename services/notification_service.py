import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from config import GMAIL_USER, GMAIL_APP_PASSWORD

def notify_completion(message: str, recipient_email: str = None) -> None:
    """顯示頁面內提醒，並自動透過 Gmail 發送通知信給使用者。"""
    
    # 1. 顯示 Streamlit 網頁右下角的彈出提示
    try:
        st.toast(message, icon="🎉")
    except Exception as e:
        print(f"⚠️ [DEBUG] st.toast 顯示失敗: {e}")
    
    # 🔍 診斷：印出目前收到的參數狀態
    print(f"🔍 [DEBUG check] 準備寄信檢查 -> recipient_email: '{recipient_email}' | GMAIL_USER: '{GMAIL_USER}' | 密碼長度: {len(GMAIL_APP_PASSWORD) if GMAIL_APP_PASSWORD else 0}")

    # 2. 如果有提供收件者信箱，且後端有設定好 Gmail 帳號與應用程式密碼，就發送郵件
    if recipient_email and GMAIL_USER and GMAIL_APP_PASSWORD:
        try:
            msg = MIMEMultipart()
            msg["From"] = GMAIL_USER
            msg["To"] = recipient_email
            msg["Subject"] = "🧺 宿舍洗衣完成通知"
            
            # 信件內文
            msg.attach(MIMEText(message, "plain", "utf-8"))
            
            # 使用 SSL 連線到 Gmail 伺服器發送郵件
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_USER, recipient_email, msg.as_string())
                
            print(f"✅ [SUCCESS] 成功寄送通知信至: {recipient_email}")
                
        except Exception as e:
            print(f"❌ Gmail 寄送失敗: {e}")
    else:
        print("⚠️ [DEBUG] 寄信條件不成立：收件者信箱、GMAIL_USER 或密碼其中一項為空，因此略過寄信。")
