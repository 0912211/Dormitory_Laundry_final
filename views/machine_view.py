import streamlit as st
from config import REFRESH_INTERVAL
from views.machine_card import render_machine_card
from views.reservation_view import show_reservation

def _leave():
    st.session_state.pop("selected_machine_id", None)
    st.rerun()

@st.fragment(run_every=REFRESH_INTERVAL)
def show_machine_page(machine_controller, laundry_controller, reservation_controller):
    machine_id = st.session_state.get("selected_machine_id")
    if not machine_id:
        st.warning("未選擇洗衣機。")
        if st.button("返回列表"):
            _leave()
        return

    machine = machine_controller.get_machine_by_id(machine_id)
    if not machine:
        st.error("找不到該洗衣機。")
        if st.button("返回列表"):
            _leave()
        return

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅ 返回"):
            _leave()

    st.subheader(f"洗衣機詳細資訊：{machine['name']}")
    
    user_id = st.session_state.user["id"]
    laundry_controller.update_expired_cycles()
    
    # 渲染單機卡片
    render_machine_card(machine, user_id, laundry_controller)

    st.divider()
    
    # 顯示該機台專屬的預約/排隊功能
    show_reservation(reservation_controller, machine_controller, only_machine_id=machine_id)
