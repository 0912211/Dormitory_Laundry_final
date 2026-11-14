"""後台管理服務。每個函式都會在資料庫端重新驗證管理員身分，
不依賴前端畫面是否隱藏選單。"""
from collections import Counter
from sqlalchemy import select
from config import ADMIN_USERNAMES
from database.db import SessionLocal
from models.user import User
from models.machine import Machine
from models.laundry_cycle import LaundryCycle
from models.reservation import Reservation
from services.clock import now_local

NO_PERMISSION = "沒有管理員權限。"

def _is_admin(db, user_id) -> bool:
    user = db.get(User, user_id) if user_id else None
    return bool(user and user.username.lower() in ADMIN_USERNAMES)

def is_admin_user(user_id: int) -> bool:
    with SessionLocal() as db:
        return _is_admin(db, user_id)

def _clean_name(name):
    name = (name or "").strip()
    if not name:
        return None, "洗衣機名稱不可空白。"
    if len(name) > 50:
        return None, "洗衣機名稱不可超過 50 個字元。"
    return name, None

def add_machine(admin_id: int, name: str):
    name, error = _clean_name(name)
    if error:
        return False, error
    with SessionLocal() as db:
        if not _is_admin(db, admin_id):
            return False, NO_PERMISSION
        if db.scalar(select(Machine).where(Machine.name == name)):
            return False, "已經有同名的洗衣機。"
        db.add(Machine(name=name))
        db.commit()
    return True, f"已新增「{name}」。"

def rename_machine(admin_id: int, machine_id: int, name: str):
    name, error = _clean_name(name)
    if error:
        return False, error
    with SessionLocal() as db:
        if not _is_admin(db, admin_id):
            return False, NO_PERMISSION
        machine = db.get(Machine, machine_id)
        if not machine:
            return False, "找不到這台洗衣機。"
        duplicate = db.scalar(select(Machine).where(Machine.name == name, Machine.id != machine_id))
        if duplicate:
            return False, "已經有同名的洗衣機。"
        machine.name = name
        db.commit()
    return True, "已更新名稱。"

def _open_cycles(db, machine_id):
    return db.scalars(select(LaundryCycle).where(
        LaundryCycle.machine_id == machine_id,
        LaundryCycle.status.in_(["washing", "finished"]),
    )).all()

def set_machine_active(admin_id: int, machine_id: int, active: bool):
    with SessionLocal() as db:
        if not _is_admin(db, admin_id):
            return False, NO_PERMISSION
        machine = db.get(Machine, machine_id)
        if not machine:
            return False, "找不到這台洗衣機。"
        if not active and _open_cycles(db, machine_id):
            return False, "這台洗衣機仍有未結束的洗衣，請先「強制釋放」再停用。"
        machine.is_active = active
        db.commit()
    return True, "已啟用洗衣機。" if active else "已停用洗衣機。"

def force_release(admin_id: int, machine_id: int):
    """管理員強制結束該機器所有未取衣的洗衣紀錄。"""
    with SessionLocal() as db:
        if not _is_admin(db, admin_id):
            return False, NO_PERMISSION
        cycles = _open_cycles(db, machine_id)
        if not cycles:
            return False, "這台洗衣機目前沒有需要釋放的洗衣。"
        now = now_local()
        for cycle in cycles:
            cycle.status = "released"
            cycle.collected_at = now
        db.commit()
    return True, "已強制釋放洗衣機。"

def list_all_cycles(admin_id: int, limit: int = 200):
    with SessionLocal() as db:
        if not _is_admin(db, admin_id):
            return []
        names = {m.id: m.name for m in db.scalars(select(Machine)).all()}
        users = {u.id: u.username for u in db.scalars(select(User)).all()}
        rows = db.scalars(select(LaundryCycle).order_by(LaundryCycle.start_time.desc()).limit(limit)).all()
        return [dict(id=r.id, machine_name=names.get(r.machine_id, str(r.machine_id)),
                     username=users.get(r.user_id, str(r.user_id)), start_time=r.start_time,
                     end_time=r.end_time, status=r.status, collected_at=r.collected_at) for r in rows]

def list_all_reservations(admin_id: int, limit: int = 200):
    with SessionLocal() as db:
        if not _is_admin(db, admin_id):
            return []
        names = {m.id: m.name for m in db.scalars(select(Machine)).all()}
        users = {u.id: u.username for u in db.scalars(select(User)).all()}
        rows = db.scalars(select(Reservation).order_by(Reservation.start_time.desc()).limit(limit)).all()
        return [dict(id=r.id, machine_name=names.get(r.machine_id, str(r.machine_id)),
                     username=users.get(r.user_id, str(r.user_id)), start_time=r.start_time,
                     end_time=r.end_time, status=r.status) for r in rows]

def usage_stats(admin_id: int):
    """各機器使用次數與各小時開始洗衣次數。"""
    with SessionLocal() as db:
        if not _is_admin(db, admin_id):
            return None
        names = {m.id: m.name for m in db.scalars(select(Machine)).all()}
        cycles = db.scalars(select(LaundryCycle)).all()
        per_machine = Counter(names.get(c.machine_id, str(c.machine_id)) for c in cycles)
        per_hour = Counter(c.start_time.hour for c in cycles)
        return {
            "total": len(cycles),
            "per_machine": {name: per_machine.get(name, 0) for name in names.values()},
            "per_hour": {hour: per_hour.get(hour, 0) for hour in range(24)},
        }

def list_users(admin_id: int):
    with SessionLocal() as db:
        if not _is_admin(db, admin_id):
            return []
        users = db.scalars(select(User).order_by(User.id)).all()
        return [dict(id=u.id, username=u.username, created_at=u.created_at,
                     is_admin=u.username.lower() in ADMIN_USERNAMES) for u in users]
