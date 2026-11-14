from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base

class Machine(Base):
    __tablename__ = "machines"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
