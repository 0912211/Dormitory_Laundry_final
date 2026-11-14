import hashlib
import hmac
import os
from sqlalchemy import select
from database.db import SessionLocal
from models.user import User
from config import MIN_PASSWORD_LENGTH, ADMIN_USERNAMES

_ITERATIONS = 310_000

def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"pbkdf2_sha256${_ITERATIONS}${salt.hex()}${digest.hex()}"

def _verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(actual.hex(), digest_hex)
    except (ValueError, TypeError):
        return False

# 🆕 加上 email 參數
def register(username: str, password: str, email: str):
    username = (username or "").strip()
    email = (email or "").strip()
    
    if len(username) < 3:
        return False, "帳號至少需要 3 個字元。"
    if len(username) > 50:
        return False, "帳號不可超過 50 個字元。"
    if not email:
        return False, "請輸入電子信箱（用於接收洗衣完成通知）。"
    if len(password or "") < MIN_PASSWORD_LENGTH:
        return False, f"密碼至少需要 {MIN_PASSWORD_LENGTH} 個字元。"
        
    with SessionLocal() as db:
        exists = db.scalar(select(User).where(User.username == username))
        if exists:
            return False, "這個帳號已經被使用。"
            
        # 🆕 建立使用者時將 email 一起寫入資料庫
        db.add(User(
            username=username, 
            password_hash=_hash_password(password),
            email=email
        ))
        db.commit()
    return True, "註冊成功，請登入。"

def login(username: str, password: str):
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == (username or "").strip()))
        if not user or not _verify_password(password or "", user.password_hash):
            return None
        return {"id": user.id, "username": user.username,
                "is_admin": user.username.lower() in ADMIN_USERNAMES}
