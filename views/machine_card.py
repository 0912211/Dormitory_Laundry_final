import streamlit as st
from config import MIN_WASH_TIME, MAX_WASH_TIME, DEFAULT_WASH_TIME
from services.timer_service import remaining_seconds, format_remaining
from services.notification_service import notify_completion
from views.flash import set_flash

def render_machine_card(machine, user_id, laundry_controller):
    """顯示單台洗衣機狀態與操作按鈕（首頁與單機頁面共用）。"""
    with st.container(border=True):
        st.markdown(f"### {machine['name']}")
        if not machine["is_active"]:
            st.warning("暫停使用")
        elif machine["cycle_status"] == "washing":
            st.warning("使用中")
            st.metric("剩餘時間", format_remaining(remaining_seconds(machine["end_time"])))
            if machine["cycle_user_id"] == user_id:
                st.caption("這是你正在使用的洗衣機")
        elif machine["cycle_status"] == "finished":
            st.success("洗衣完成，等待取衣")
            if machine["cycle_user_id"] == user_id:
                st.info("請記得領取衣物")
                if st.button("確認已取衣", key=f"collect_{machine['cycle_id']}"):
                    ok, msg = laundry_controller.collect_cycle(user_id, machine["cycle_id"])
                    set_flash(ok, msg)
                    st.rerun()
        else:
            st.success("目前空閒")
            durations = list(range(MIN_WASH_TIME, MAX_WASH_TIME + 1, 5))
            duration = st.selectbox(
                "洗衣時間（分鐘）", durations,
                index=durations.index(DEFAULT_WASH_TIME) if DEFAULT_WASH_TIME in durations else 0,
                key=f"duration_{machine['id']}")
            if st.button("開始洗衣", key=f"start_{machine['id']}", width="stretch"):
                ok, msg = laundry_controller.start_cycle(user_id, machine["id"], duration)
                set_flash(ok, msg)
                st.rerun()

def notify_finished_cycles(laundry_controller, user_id):
    """使用者的洗衣完成時，跳出一次頁面內提醒。"""
    for cycle in laundry_controller.get_user_active_cycles(user_id):
        if cycle["status"] == "finished":
            key = f"notified_{cycle['id']}"
            if not st.session_state.get(key, False):
                notify_completion(f"{cycle['machine_name']} 已完成洗衣！")
                st.session_state[key] = True
