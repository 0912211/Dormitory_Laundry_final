from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base
from services.clock import now_local

class Reservation(Base):
    __tablename__ = "reservations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), index=True)
    
    # 🆕 改為記錄加入排隊的時間點（不再需要預約起訖時間）
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_local, index=True)
    
    # 狀態：waiting (排隊中), notified (已通知可洗衣), completed (已完成洗衣), cancelled (已取消)
    status: Mapped[str] = mapped_column(String(20), default="waiting", index=True)
