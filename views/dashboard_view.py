import streamlit as st
from config import DEFAULT_WASH_TIME

def render_machine_card(machine, user_id, laundry_controller):
    machine_id = machine["id"]
    machine_name = machine["name"]
    is_active = machine.get("is_active", True)

    with st.container(border=True):
        st.subheader(f"🧺 {machine_name}")
        
        if not is_active:
            st.error("此機器目前維護中 / 停用")
            return

        # 取得該機器的目前狀態
        active_cycles = laundry_controller.get_user_active_cycles(user_id)
        # 這裡可以直接查詢該機台目前的全局狀態（看是否有人在洗）
        # 為了簡化，我們可以從 laundry_controller 或直接顯示卡片介面
        
        st.markdown(f"**狀態**：正常運作中")

        # 洗衣時間選擇
        durations = [10, 30, 45, 60]
        selected_duration = st.selectbox(
            "選擇洗衣時間 (分鐘)",
            options=durations,
            index=durations.index(DEFAULT_WASH_TIME) if DEFAULT_WASH_TIME in durations else 1,
            key=f"duration_{machine_id}"
        )

        if st.button("開始洗衣", key=f"start_{machine_id}", use_container_width=True):
            ok, msg = laundry_controller.start_cycle(user_id, machine_id, selected_duration)
            if ok:
                st.success(msg)
            else:
                st.warning(msg)
            st.rer()

def notify_finished_cycles(laundry_controller, user_id):
    """
    安全地檢查當前使用者的已完成洗衣行程，
    並透過 st.toast 彈出提示，且利用 st.session_state 避免重複跳出。
    """
    try:
        active_cycles = laundry_controller.get_user_active_cycles(user_id)
        for cycle in active_cycles:
            # 嚴格確認狀態為 finished 且確實屬於當前登入的使用者
            if cycle.get("status") == "finished":
                cycle_id = cycle.get("id")
                toast_key = f"toast_shown_{user_id}_{cycle_id}"
                
                # 如果這個行程還沒被提示過，才跳出 toast 並做記號
                if not st.session_state.get(toast_key, False):
                    machine_name = cycle.get("machine_name", "洗衣機")
                    st.toast(f"👕 您的洗衣機（{machine_name}）已經洗好囉！請盡快前往領取。", icon="🔔")
                    st.session_state[toast_key] = True
    except Exception as e:
        # 避免背景檢查失敗影響畫面渲染
        print(f"⚠️ 通知載入錯誤: {e}")
