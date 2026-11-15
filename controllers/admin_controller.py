from services import admin_service, qr_service

class AdminController:
    """所有方法都以登入者 id 驗證管理員身分（由 service 在資料庫端檢查）。"""

    def is_admin(self, user_id):
        return admin_service.is_admin_user(user_id)

    def add_machine(self, admin_id, name):
        return admin_service.add_machine(admin_id, name)

    def rename_machine(self, admin_id, machine_id, name):
        return admin_service.rename_machine(admin_id, machine_id, name)

    def set_machine_active(self, admin_id, machine_id, active):
        return admin_service.set_machine_active(admin_id, machine_id, active)

    def force_release(self, admin_id, machine_id):
        return admin_service.force_release(admin_id, machine_id)

    def list_all_cycles(self, admin_id):
        return admin_service.list_all_cycles(admin_id)

    def list_all_reservations(self, admin_id):
        return admin_service.list_all_reservations(admin_id)

    def get_machines_queue_status(self, admin_id):
        """🆕 取得所有洗衣機目前的排隊人數與詳細名單"""
        return admin_service.get_machines_queue_status(admin_id)

    def usage_stats(self, admin_id):
        return admin_service.usage_stats(admin_id)

    def list_users(self, admin_id):
        return admin_service.list_users(admin_id)

    def machine_url(self, machine_id):
        return qr_service.machine_url(machine_id)

    def qr_png(self, machine_id):
        return qr_service.make_qr_png(qr_service.machine_url(machine_id))

    def qr_zip(self, machines):
        return qr_service.make_qr_zip(machines)
