from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import DATABASE_URL, BASE_DIR

class Base(DeclarativeBase):
    pass

# 根據 config.py 提供的 DATABASE_URL 建立連線（完全避開直接讀取 st.secrets 造成 KeyError）
if DATABASE_URL.startswith("sqlite:"):
    (BASE_DIR / "database").mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# 註冊所有資料庫模型（Model）
from models.user import User
from models.machine import Machine
from models.laundry_cycle import LaundryCycle
from models.reservation import Reservation

# 自動在資料庫中建立所有尚未存在的表格
Base.metadata.create_all(bind=engine)
