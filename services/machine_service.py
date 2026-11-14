from sqlalchemy import select
from database.db import SessionLocal
from models.machine import Machine
from models.laundry_cycle import LaundryCycle
from services.clock import now_local

def _machine_status(db, machine, now) -> dict:
    cycle = db.scalar(select(LaundryCycle).where(
        LaundryCycle.machine_id == machine.id,
        LaundryCycle.status.in_(["washing", "finished"]),
    ).order_by(LaundryCycle.id.desc()))
    info = {"id": machine.id, "name": machine.name, "is_active": machine.is_active,
            "cycle_status": "idle", "end_time": None, "cycle_id": None, "cycle_user_id": None}
    # 僅保留尚未取衣的最新一筆進行中/已完成紀錄
    if cycle and (cycle.status == "finished" or (cycle.status == "washing" and cycle.end_time > now)):
        info.update(cycle_status=cycle.status, end_time=cycle.end_time,
                    cycle_id=cycle.id, cycle_user_id=cycle.user_id)
    return info

def get_machines():
    now = now_local()
    with SessionLocal() as db:
        machines = db.scalars(select(Machine).order_by(Machine.id)).all()
        return [_machine_status(db, m, now) for m in machines]

def get_machine(machine_id: int):
    """取得單一洗衣機狀態；找不到時回傳 None。"""
    now = now_local()
    with SessionLocal() as db:
        machine = db.get(Machine, machine_id)
        return _machine_status(db, machine, now) if machine else None
