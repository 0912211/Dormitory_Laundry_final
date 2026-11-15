from datetime import timedelta
from sqlalchemy import select
from database.db import SessionLocal
from models.machine import Machine
from models.laundry_cycle import LaundryCycle
from models.reservation import Reservation
from models.user import User
from services.clock import now_local
from services.notification_service import notify_completion

def start_cycle(user_id: int, machine_id: int, duration_minutes: int):
    now = now_local()
    end = now + timedelta(minutes=duration_minutes)
    with SessionLocal() as db:
        machine = db.get(Machine, machine_id)
        if not machine or not machine.is_active:
            return False, "這台洗衣機目前無法使用。"
        
        # 1. 檢查目前機台是否有正在使用或待取衣的行程
        current = db.scalar(select(LaundryCycle).where(
            LaundryCycle.machine_id == machine_id,
            LaundryCycle.status.in_(["washing", "finished"]),
        ).order_by(LaundryCycle.id.desc()))
        
        if current and current.status in ("washing", "finished"):
            if current.status == "washing" and current.end_time > now:
                return False, "這台洗衣機目前正在使用。"
            if current.status == "finished":
                return False, "上一位使用者尚未取走衣物。"

        # 2. 候補排隊制檢查：若該機台有人在排隊，檢查該使用者是否為第一順位（或已被通知）
        queue_items = db.scalars(select(Reservation).where(
            Reservation.machine_id == machine_id,
            Reservation.status.in_(["waiting", "notified"])
        ).order_by(Reservation.created_at.asc())).all()

        if queue_items:
            first_in_line = queue_items[0]
            if first_in_line.user_id != user_id and not any(q.user_id == user_id and q.status == "notified" for q in queue_items):
                return False, "此洗衣機目前有其他同學在排隊等候，請先加入排隊。"
            
            # 若自己是第一順位或被通知者，開始洗衣時將該排隊紀錄設為 completed
            for q in queue_items:
                if q.user_id == user_id:
                    q.status = "completed"

        db.add(LaundryCycle(user_id=user_id, machine_id=machine_id, start_time=now, end_time=end, status="washing"))
        db.commit()
    return True, "已開始洗衣，請留意剩餘時間。"

def collect_cycle(user_id: int, cycle_id: int):
    with SessionLocal() as db:
        cycle = db.get(LaundryCycle, cycle_id)
        if not cycle or cycle.user_id != user_id:
            return False, "找不到這筆洗衣紀錄或沒有權限。"
        if cycle.status != "finished":
            return False, "洗衣尚未完成，暫時不能確認取衣。"
        
        cycle.status = "collected"
        cycle.collected_at = now_local()
        
        # 3. 取衣完成後，自動尋找該機台排隊名單中的下一位，設為 notified 並寄送通知
        next_queue = db.scalar(select(Reservation).where(
            Reservation.machine_id == cycle.machine_id,
            Reservation.status == "waiting"
        ).order_by(Reservation.created_at.asc()))
        
        if next_queue:
            next_queue.status = "notified"
            next_user = db.get(User, next_queue.user_id)
            machine = db.get(Machine, cycle.machine_id)
            machine_name = machine.name if machine else str(cycle.machine_id)
            
            if next_user and next_user.email:
                msg = f"好消息！您排隊的【{machine_name}】前一位使用者已取衣完成，輪到您使用囉！請盡快前往開始洗衣。"
                print(f"📧 傳送排隊到位通知給: {next_user.email}")
                notify_completion(msg, recipient_email=next_user.email)

        db.commit()
    return True, "已確認取衣。"

def get_user_history(user_id: int):
    with SessionLocal() as db:
        rows = db.scalars(select(LaundryCycle).where(LaundryCycle.user_id == user_id)
                            .order_by(LaundryCycle.start_time.desc())).all()
        names = {m.id: m.name for m in db.scalars(select(Machine)).all()}
        return [dict(
            id=r.id, machine_id=r.machine_id, machine_name=names.get(r.machine_id, str(r.machine_id)),
            start_time=r.start_time, end_time=r.end_time, status=r.status,
            collected_at=r.collected_at
        ) for r in rows]

def update_expired_cycles():
    now = now_local()
    with SessionLocal() as db:
        rows = db.scalars(select(LaundryCycle).where(
            LaundryCycle.status == "washing"
        )).all()
        
        updated = False
        for r in rows:
            if now >= r.end_time:
                r.status = "finished"
                updated = True
                
                user = db.get(User, r.user_id)
                machine = db.get(Machine, r.machine_id)
                machine_name = machine.name if machine else str(r.machine_id)
                
                if user and user.email:
                    message = f"您的洗衣機（編號 {machine_name}）已經洗好囉！請盡快前往拿取並於系統確認取衣。"
                    print(f"📧 準備寄送完成通知給: {user.email}")
                    notify_completion(message, recipient_email=user.email)
        
        if updated:
            db.commit()

def get_user_active_cycles(user_id: int):
    update_expired_cycles()
    with SessionLocal() as db:
        rows = db.scalars(select(LaundryCycle).where(
            LaundryCycle.user_id == user_id, LaundryCycle.status.in_(["washing", "finished"])
        )).all()
        names = {m.id: m.name for m in db.scalars(select(Machine)).all()}
        return [dict(
            id=r.id, machine_id=r.machine_id, machine_name=names.get(r.machine_id, str(r.machine_id)),
            status=r.status, end_time=r.end_time
        ) for r in rows]
