from datetime import datetime
from config import TIMEZONE

def now_local() -> datetime:
    """回傳台灣當地時間，使用不含時區資訊的 datetime 存入資料庫。"""
    return datetime.now(TIMEZONE).replace(tzinfo=None)
