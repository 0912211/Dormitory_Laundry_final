from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base

class LaundryCycle(Base):
    __tablename__ = "laundry_cycles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, index=True)  # 修正此處，移除多餘的賦值
    status: Mapped[str] = mapped_column(String(20), default="washing")
    collected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # 🆕 新增：記錄上次發送取衣提醒的時間（用於每 10 分鐘自動重複推播）
    last_reminder_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
