import streamlit as st
from config import REFRESH_INTERVAL
from views.machine_card import render_machine_card, notify_finished_cycles
from views.reservation_view import show_reservation

def _leave():
    st.query_params.clear()

@st.fragment(run_every=REFRESH_INTERVAL)
def _machine_status(machine_controller, laundry_controller, machine_id):
    user_id = st.session_state.user["id"]
    laundry_controller.update_expired_cycles()
    machine = machine_controller.get_machine(machine_id)
    if machine is None:
        st.error("找不到這台洗衣機。")
        return
    render_machine_card(machine, user_id, laundry_controller)
    notify_finished_cycles(laundry_controller, user_id)

def show_machine_page(machine_controller, laundry_controller, reservation_controller, machine_id):
    """掃描洗衣機 QR Code 後進入的單機頁面。"""
    if machine_id is None or machine_controller.get_machine(machine_id) is None:
        st.error("找不到這台洗衣機，QR Code 可能已失效。")
    else:
        st.header("單機頁面")
        _machine_status(machine_controller, laundry_controller, machine_id)
        with st.expander("預約這台洗衣機"):
            show_reservation(reservation_controller, machine_controller, only_machine_id=machine_id)
    st.button("返回首頁", on_click=_leave)
