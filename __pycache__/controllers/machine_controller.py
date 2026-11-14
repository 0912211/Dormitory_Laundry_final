from services.machine_service import get_machines, get_machine

class MachineController:
    def get_all_machines(self):
        return get_machines()

    def get_machine(self, machine_id):
        return get_machine(machine_id)
