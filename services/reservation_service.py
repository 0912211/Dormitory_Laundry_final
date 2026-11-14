from datetime import timedelta
from sqlalchemy import select
from database.db import SessionLocal
from models.machine import Machine
from models.reservation import Reservation
from models.laundry_cycle import LaundryCycle
from services.clock import now_local

def create_reservation(user_id: int, machine_id: int, start_time, duration_minutes: int):
    now = now_local()
    if start_time <= now:
        return False, "預約開始時間必須晚於現在。"
    end_time = start_time + timedelta(minutes=duration_minutes)
    with SessionLocal() as db:
        machine = db.get(Machine, machine_id)
        if not machine or not machine.is_active:
            return False, "選擇的洗衣機目前無法使用。"
        overlap = db.scalar(select(Reservation).where(
            Reservation.machine_id == machine_id, Reservation.status == "booked",
            Reservation.start_time < end_time, Reservation.end_time > start_time,
        ))
        if overlap:
            return False, "此時段已經有人預約，請更換時間。"
        busy = db.scalar(select(LaundryCycle).where(
            LaundryCycle.machine_id == machine_id, LaundryCycle.status.in_(["washing", "finished"]),
            LaundryCycle.start_time < end_time, LaundryCycle.end_time > start_time,
        ))
        if busy:
            return False, "此時段洗衣機正在使用，請更換時間。"
        db.add(Reservation(user_id=user_id, machine_id=machine_id,
                           start_time=start_time, end_time=end_time, status="booked"))
        db.commit()
    return True, "預約成功。"

def cancel_reservation(user_id: int, reservation_id: int):
    with SessionLocal() as db:
        reservation = db.get(Reservation, reservation_id)
        if not reservation or reservation.user_id != user_id or reservation.status != "booked":
            return False
        reservation.status = "cancelled"
        db.commit()
        return True

def list_user_reservations(user_id: int):
    with SessionLocal() as db:
        rows = db.scalars(select(Reservation).where(Reservation.user_id == user_id)
                          .order_by(Reservation.start_time.desc())).all()
        names = {m.id: m.name for m in db.scalars(select(Machine)).all()}
        return [dict(id=r.id, machine_id=r.machine_id, machine_name=names.get(r.machine_id, str(r.machine_id)),
                     start_time=r.start_time, end_time=r.end_time, status=r.status) for r in rows]
