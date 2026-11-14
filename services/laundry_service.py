from datetime import timedelta
from sqlalchemy import select
from database.db import SessionLocal
from models.machine import Machine
from models.laundry_cycle import LaundryCycle
from models.reservation import Reservation
from services.clock import now_local

def start_cycle(user_id: int, machine_id: int, duration_minutes: int):
    now = now_local()
    end = now + timedelta(minutes=duration_minutes)
    with SessionLocal() as db:
        machine = db.get(Machine, machine_id)
        if not machine or not machine.is_active:
            return False, "這台洗衣機目前無法使用。"
        current = db.scalar(select(LaundryCycle).where(
            LaundryCycle.machine_id == machine_id,
            LaundryCycle.status.in_(["washing", "finished"]),
        ).order_by(LaundryCycle.id.desc()))
        if current and current.status in ("washing", "finished"):
            if current.status == "washing" and current.end_time > now:
                return False, "這台洗衣機目前正在使用。"
            if current.status == "finished":
                return False, "上一位使用者尚未取走衣物。"
        bookings = db.scalars(select(Reservation).where(
            Reservation.machine_id == machine_id, Reservation.status == "booked",
            Reservation.start_time < end, Reservation.end_time > now,
        )).all()
        # 若有預約，只有該預約者能在預約時段內開始，且洗衣須在預約結束前完成
        if bookings:
            allowed = any(b.user_id == user_id and b.start_time <= now and end <= b.end_time for b in bookings)
            if not allowed:
                return False, "這台洗衣機在此時段已有預約，請選擇其他時段或先完成預約。"
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
        db.commit()
    return True, "已確認取衣。"

def get_user_history(user_id: int):
    with SessionLocal() as db:
        rows = db.scalars(select(LaundryCycle).where(LaundryCycle.user_id == user_id)
                          .order_by(LaundryCycle.start_time.desc())).all()
        names = {m.id: m.name for m in db.scalars(select(Machine)).all()}
        return [dict(id=r.id, machine_id=r.machine_id, machine_name=names.get(r.machine_id, str(r.machine_id)),
                     start_time=r.start_time, end_time=r.end_time, status=r.status,
                     collected_at=r.collected_at) for r in rows]

def get_user_active_cycles(user_id: int):
    with SessionLocal() as db:
        rows = db.scalars(select(LaundryCycle).where(
            LaundryCycle.user_id == user_id, LaundryCycle.status.in_(["washing", "finished"])
        )).all()
        names = {m.id: m.name for m in db.scalars(select(Machine)).all()}
        return [dict(id=r.id, machine_id=r.machine_id, machine_name=names.get(r.machine_id, str(r.machine_id)),
                     status=r.status, end_time=r.end_time) for r in rows]
