from sqlalchemy import select
from database.db import SessionLocal
from models.laundry_cycle import LaundryCycle
from models.reservation import Reservation
from models.user import User  # 用來查詢使用者的 Email
from services.clock import now_local
from services.notification_service import notify_completion  # 引入寄信服務

def finish_expired_cycles() -> int:
    now = now_local()
    with SessionLocal() as db:
        cycles = db.scalars(select(LaundryCycle).where(
            LaundryCycle.status == "washing",
            LaundryCycle.end_time <= now,
        )).all()
        
        for cycle in cycles:
            cycle.status = "finished"
            
            # 🔍 關鍵：當洗衣完成時，主動尋找使用者並發送 Email 通知
            if cycle.user_id:
                user = db.get(User, cycle.user_id)
                if user and user.email:
                    msg_text = f"您的洗衣行程已完成！請盡快前往洗衣間領取衣物。"
                    print(f"📧 [SCHEDULER] 準備發送完成通知給: {user.email}")
                    notify_completion(msg_text, user.email)

        expired = db.scalars(select(Reservation).where(
            Reservation.status == "booked",
            Reservation.end_time <= now,
        )).all()
        
        for reservation in expired:
            reservation.status = "expired"
            
        if cycles or expired:
            db.commit()
            
        return len(cycles)
