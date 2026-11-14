from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import DATABASE_URL, BASE_DIR

class Base(DeclarativeBase):
    pass

if DATABASE_URL.startswith("sqlite:"):
    (BASE_DIR / "database").mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# 💡 1. 務必在這裡把所有資料庫模型（Model）都匯入進來
# 這樣 Base 才能夠註冊它們的結構
from models.user import User
from models.machine import Machine
from models.laundry_cycle import LaundryCycle
from models.reservation import Reservation

# 💡 2. 自動在資料庫中建立所有尚未存在的表格（包含我們剛新增的 email 欄位）
Base.metadata.create_all(bind=engine)
