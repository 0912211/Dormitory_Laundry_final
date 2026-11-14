import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from config import GMAIL_USER, GMAIL_APP_PASSWORD

def notify_completion(message: str, recipient_email: str = None) -> None:
    """顯示頁面內提醒，並自動透過 Gmail 發送通知信給使用者。"""
    
    # 1. 顯示 Streamlit 網頁右下角的彈出提示
    st.toast(message, icon="🎉")
    
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
                
        except Exception as e:
            # 若寄信失敗（例如網路問題或密碼錯誤），在終端機印出錯誤但不影響網頁運作
            print(f"❌ Gmail 寄送失敗: {e}")
