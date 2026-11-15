from sqlalchemy import select, func
from database.db import SessionLocal
from models.machine import Machine
from models.reservation import Reservation
from models.laundry_cycle import LaundryCycle
from services.clock import now_local

def join_queue(user_id: int, machine_id: int):
    """加入指定洗衣機的排隊佇列（取代原本的時間預約）"""
    with SessionLocal() as db:
        machine = db.get(Machine, machine_id)
        if not machine or not machine.is_active:
            return False, "選擇的洗衣機目前無法使用。"

        # 1. 檢查該使用者是否已經在這台機器的排隊名單中（waiting 或 notified）
        already_in = db.scalar(select(Reservation).where(
            Reservation.user_id == user_id,
            Reservation.machine_id == machine_id,
            Reservation.status.in_(["waiting", "notified"])
        ))
        if already_in:
            return False, "您已經在這台洗衣機的排隊名單中囉！"

        # 2. 檢查洗衣機是否目前完全空閒（無人洗衣、也無人洗好待取、且無人排隊）
        active_cycle = db.scalar(select(LaundryCycle).where(
            LaundryCycle.machine_id == machine_id,
            LaundryCycle.status.in_(["washing", "finished"])
        ))
        existing_queue = db.scalar(select(Reservation).where(
            Reservation.machine_id == machine_id,
            Reservation.status.in_(["waiting", "notified"])
        ))

        if not active_cycle and not existing_queue:
            return False, "這台洗衣機目前完全空閒，不需要排隊，請直接開始洗衣！"

        # 3. 成功加入排隊
        db.add(Reservation(
            user_id=user_id,
            machine_id=machine_id,
            created_at=now_local(),
            status="waiting"
        ))
        db.commit()
    return True, "已成功加入排隊！當洗衣機空閒時，系統會自動發送通知給第一順位的您。"

def cancel_reservation(user_id: int, reservation_id: int):
    """取消排隊（保留函式名稱以相容原本的 Controller/View）"""
    with SessionLocal() as db:
        reservation = db.get(Reservation, reservation_id)
        if not reservation or reservation.user_id != user_id or reservation.status not in ("waiting", "notified"):
            return False, "找不到這筆排隊紀錄或無法取消。"
        reservation.status = "cancelled"
        db.commit()
    return True, "已成功取消排隊。"

def list_user_reservations(user_id: int):
    """列出使用者的排隊紀錄（保留函式名稱與格式，改為顯示加入時間與排隊狀態）"""
    with SessionLocal() as db:
        rows = db.scalars(select(Reservation).where(Reservation.user_id == user_id)
                          .order_by(Reservation.created_at.desc())).all()
        names = {m.id: m.name for m in db.scalars(select(Machine)).all()}
        return [dict(
            id=r.id, 
            machine_id=r.machine_id, 
            machine_name=names.get(r.machine_id, str(r.machine_id)),
            created_at=r.created_at, 
            status=r.status
        ) for r in rows]

def get_machine_queue_count(machine_id: int) -> int:
    """取得某台洗衣機目前正在排隊（waiting 或 notified）的總人數"""
    with SessionLocal() as db:
        count = db.scalar(
            select(func.count(Reservation.id)).where(
                Reservation.machine_id == machine_id,
                Reservation.status.in_(["waiting", "notified"])
            )
        )
        return count or 0
