from config import MIN_WASH_TIME, MAX_WASH_TIME
from services.laundry_service import start_cycle, collect_cycle, get_user_history, get_user_active_cycles
from services.scheduler_service import finish_expired_cycles

class LaundryController:
    def start_cycle(self, user_id, machine_id, duration_minutes):
        if not MIN_WASH_TIME <= duration_minutes <= MAX_WASH_TIME:
            return False, f"洗衣時間必須介於 {MIN_WASH_TIME} 至 {MAX_WASH_TIME} 分鐘。"
        return start_cycle(user_id, machine_id, duration_minutes)

    def collect_cycle(self, user_id, cycle_id):
        return collect_cycle(user_id, cycle_id)

    def get_user_history(self, user_id):
        return get_user_history(user_id)

    def get_user_active_cycles(self, user_id):
        return get_user_active_cycles(user_id)

    def update_expired_cycles(self):
        return finish_expired_cycles()
