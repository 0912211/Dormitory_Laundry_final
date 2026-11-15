from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import DATABASE_URL, BASE_DIR

class Base(DeclarativeBase):
    pass

# 根據 config.py 提供的 DATABASE_URL 建立連線
if DATABASE_URL.startswith("sqlite:"):
    (BASE_DIR / "database").mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# 💡 注意：這裡不要匯入 models，也不要在這裡執行 create_all，
# 這樣就能完全避免循環引用的問題！
