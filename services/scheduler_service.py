from datetime import timedelta
from sqlalchemy import select
from database.db import SessionLocal
from models.laundry_cycle import LaundryCycle
from models.user import User
from models.machine import Machine
from services.clock import now_local
from services.notification_service import notify_completion

def finish_expired_cycles() -> int:
    now = now_local()
    with SessionLocal() as db:
        # 1. 處理剛好時間到、從 washing 轉為 finished 的行程
        expired_washing = db.scalars(select(LaundryCycle).where(
            LaundryCycle.status == "washing",
            LaundryCycle.end_time <= now,
        )).all()
        
        for cycle in expired_washing:
            cycle.status = "finished"
            cycle.last_reminder_time = now  # 記錄首次提醒時間
            send_pickup_reminder(db, cycle, is_first=True)

        # 2. 處理已經是 finished 但尚未取衣的行程（每 10 分鐘重複提醒一次）
        finished_cycles = db.scalars(select(LaundryCycle).where(
            LaundryCycle.status == "finished"
        )).all()
        
        for cycle in finished_cycles:
            if cycle.last_reminder_time and (now - cycle.last_reminder_time) >= timedelta(minutes=10):
                cycle.last_reminder_time = now  # 更新上次提醒時間
                send_pickup_reminder(db, cycle, is_first=False)

        if expired_washing or finished_cycles:
            db.commit()
            
        return len(expired_washing)

def send_pickup_reminder(db, cycle, is_first: bool):
    user = db.get(User, cycle.user_id)
    machine = db.get(Machine, cycle.machine_id)
    machine_name = machine.name if machine else f"機器 #{cycle.machine_id}"
    
    if user and user.email:
        app_url = "https://dormitory-laundry.streamlit.app"  
        title_prefix = "🧺 【洗衣完成通知】" if is_first else "⏰ 【取衣提醒】您的衣物尚未領取！"
        
        message = (
            f"{title_prefix}\n\n"
            f"您的洗衣機（{machine_name}）衣物已經洗好囉！\n"
            f"請盡快前往洗衣間領取衣物。\n\n"
            f"⚠️ 重要提醒：領取衣物後，請務必登入系統點擊【標記取衣】以釋放洗衣機給其他同學使用！\n\n"
            f"🔗 系統快速連結：{app_url}"
        )
        print(f"📧 [REMINDER] 發送取衣提醒給: {user.email} (是否首次: {is_first})")
        notify_completion(message, recipient_email=user.email)
