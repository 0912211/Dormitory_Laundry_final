from config import MIN_RESERVATION_TIME, MAX_RESERVATION_TIME
from services.reservation_service import create_reservation, cancel_reservation, list_user_reservations

class ReservationController:
    def create_reservation(self, user_id, machine_id, start_time, duration_minutes):
        if not MIN_RESERVATION_TIME <= duration_minutes <= MAX_RESERVATION_TIME:
            return False, f"預約時間必須介於 {MIN_RESERVATION_TIME} 至 {MAX_RESERVATION_TIME} 分鐘。"
        return create_reservation(user_id, machine_id, start_time, duration_minutes)

    def cancel_reservation(self, user_id, reservation_id):
        return cancel_reservation(user_id, reservation_id)

    def get_user_reservations(self, user_id):
        return list_user_reservations(user_id)
