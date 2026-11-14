from sqlalchemy import select
from database.db import SessionLocal
from models.laundry_cycle import LaundryCycle
from models.reservation import Reservation
from services.clock import now_local

def finish_expired_cycles() -> int:
    now = now_local()
    with SessionLocal() as db:
        cycles = db.scalars(select(LaundryCycle).where(
            LaundryCycle.status == "washing",
            LaundryCycle.end_time <= now,
        )).all()
        for cycle in cycles:
            cycle.status = "finished"
        expired = db.scalars(select(Reservation).where(
            Reservation.status == "booked",
            Reservation.end_time <= now,
        )).all()
        for reservation in expired:
            reservation.status = "expired"
        if cycles or expired:
            db.commit()
        return len(cycles)
