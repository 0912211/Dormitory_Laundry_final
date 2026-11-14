import os
from pathlib import Path
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parent
APP_NAME = "宿舍洗衣機管理系統"
APP_VERSION = "1.0.0"

try:
    TIMEZONE = ZoneInfo("Asia/Taipei")
except Exception:
    # Windows 若缺少時區資料，固定使用台灣 UTC+8
    TIMEZONE = timezone(timedelta(hours=8))

def _get_setting(name, default=None):
    """先讀環境變數，再讀 Streamlit Secrets。"""
    value = os.getenv(name)
    if value is None:
        try:
            import streamlit as st
            value = st.secrets.get(name)
        except Exception:
            value = None
    return default if value is None else value

# 可透過環境變數或 Streamlit Secrets 指定雲端 PostgreSQL
DATABASE_URL = _get_setting("DATABASE_URL")

# 🛡️ 自動防呆：如果讀到的字串包含錯誤參數，直接在程式中修正它！
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("requiresslmode=require", "sslmode=require")
    DATABASE_URL = DATABASE_URL.replace("&channel_binding=require", "")
    DATABASE_URL = DATABASE_URL.replace("channel_binding=require", "")

if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{(BASE_DIR / 'database' / 'laundry.db').as_posix()}"

def _parse_names(value) -> frozenset:
    if not value:
        return frozenset()
    if isinstance(value, str):
        value = value.split(",")
    return frozenset(str(v).strip().lower() for v in value if str(v).strip())


# 管理員帳號名稱（預設包含 user1，也支援透過環境變數或 Streamlit Secrets 自訂）
ADMIN_USERNAMES = _parse_names(_get_setting("ADMIN_USERNAMES", "user1"))

# 網站對外網址，用來產生每台洗衣機的 QR Code
APP_BASE_URL = str(_get_setting("APP_BASE_URL", "http://localhost:8501")).strip().rstrip("/")

# 🆕 加上 Gmail 寄信設定（會自動從環境變數或 Streamlit Secrets 讀取）
GMAIL_USER = str(_get_setting("GMAIL_USER", "")).strip()
GMAIL_APP_PASSWORD = str(_get_setting("GMAIL_APP_PASSWORD", "")).strip()

DEFAULT_MACHINE_COUNT = 3
MIN_WASH_TIME = 15
MAX_WASH_TIME = 120
DEFAULT_WASH_TIME = 40
MIN_RESERVATION_TIME = 15
MAX_RESERVATION_TIME = 120
REFRESH_INTERVAL = 5
MIN_PASSWORD_LENGTH = 8
