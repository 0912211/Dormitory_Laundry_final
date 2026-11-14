import streamlit as st
from datetime import date, time, datetime, timedelta
from config import MIN_RESERVATION_TIME, MAX_RESERVATION_TIME
from services.clock import now_local
from views.flash import set_flash
from views.labels import RESERVATION_STATUS_TEXT

def show_reservation(controller, machine_controller, only_machine_id=None):
    user = st.session_state.user
    today = now_local().date()
    machines = [m for m in machine_controller.get_all_machines()
                if m["is_active"] and (only_machine_id is None or m["id"] == only_machine_id)]
    if not machines:
        st.info("目前沒有可預約的洗衣機。")
        return
    st.subheader("建立預約")
    machine_map = {m["name"]: m["id"] for m in machines}
    with st.form("reservation_form"):
        selected_name = st.selectbox("選擇洗衣機", list(machine_map))
        selected_date = st.date_input("預約日期", value=today + timedelta(days=1), min_value=today)
        selected_time = st.time_input("開始時間", value=time(18, 0), step=timedelta(minutes=15))
        durations = list(range(MIN_RESERVATION_TIME, MAX_RESERVATION_TIME + 1, 15))
        duration = st.selectbox("預約時間（分鐘）", durations, index=min(1, len(durations)-1))
        submitted = st.form_submit_button("確認預約", width="stretch")
    if submitted:
        start = datetime.combine(selected_date, selected_time)
        ok, message = controller.create_reservation(user["id"], machine_map[selected_name], start, duration)
        (st.success if ok else st.error)(message)
    st.divider()
    st.subheader("我的預約")
    reservations = controller.get_user_reservations(user["id"])
    if only_machine_id is not None:
        reservations = [r for r in reservations if r["machine_id"] == only_machine_id]
    if not reservations:
        st.info("目前沒有預約紀錄。")
    for item in reservations:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{item['machine_name']}｜{item['start_time']:%Y-%m-%d %H:%M} 至 {item['end_time']:%H:%M}｜{RESERVATION_STATUS_TEXT.get(item['status'], item['status'])}")
        with col2:
            if item["status"] == "booked" and st.button("取消", key=f"cancel_{item['id']}"):
                if controller.cancel_reservation(user["id"], item["id"]):
                    set_flash(True, "已取消預約。")
                    st.rerun()
                else:
                    st.error("無法取消這筆預約。")
