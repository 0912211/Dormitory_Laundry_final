from services.reservation_service import (
    join_queue,
    cancel_reservation,
    list_user_reservations,
    get_machine_queue_count
)

class ReservationController:
    def join_queue(self, user_id, machine_id):
        """讓使用者加入指定洗衣機的排隊"""
        return join_queue(user_id, machine_id)

    def cancel_reservation(self, user_id, reservation_id):
        """取消排隊"""
        return cancel_reservation(user_id, reservation_id)

    def get_user_reservations(self, user_id):
        """取得使用者的排隊紀錄"""
        return list_user_reservations(user_id)

    def get_queue_count(self, machine_id):
        """取得某台洗衣機目前的排隊人數"""
        return get_machine_queue_count(machine_id)
