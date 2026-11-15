import streamlit as st
from config import REFRESH_INTERVAL
from views.machine_card import render_machine_card

@st.fragment(run_every=REFRESH_INTERVAL)
def show_dashboard(machine_controller, laundry_controller):
    user_id = st.session_state.user["id"]
    
    # 全域檢查逾期與狀態同步（同時會觸發背景 Gmail 寄信）
    laundry_controller.update_expired_cycles()
    
    machines = machine_controller.get_all_machines()
    
    st.subheader("洗衣機即時狀態")
    if not machines:
        st.info("目前沒有洗衣機資料。")
        return
        
    columns = st.columns(min(3, len(machines)))
    for index, machine in enumerate(machines):
        with columns[index % len(columns)]:
            render_machine_card(machine, user_id, laundry_controller)
