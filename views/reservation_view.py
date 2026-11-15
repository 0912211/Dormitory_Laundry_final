import streamlit as st
from views.flash import set_flash

# 排隊狀態文字對應
QUEUE_STATUS_TEXT = {
    "waiting": "排隊中",
    "notified": "已輪到您 (請前往使用)",
    "completed": "已完成",
    "cancelled": "已取消"
}

def notify_queue_notifications(controller, user_id):
    """
    安全地檢查當前使用者的排隊狀態：
    若有任何一台機器的排隊狀態變成 'notified'（輪到您），
    透過 st.toast 彈出個人化提示，並用 st.session_state 避免重複跳出。
    """
    try:
        reservations = controller.get_user_reservations(user_id)
        for item in reservations:
            if item.get("status") == "notified":
                res_id = item.get("id")
                # 結合 user_id 與 res_id 產生專屬的 session 鑰匙，絕不跨帳號外洩
                toast_key = f"queue_toast_user_{user_id}_res_{res_id}"
                
                if not st.session_state.get(toast_key, False):
                    machine_name = item.get("machine_name", "洗衣機")
                    st.toast(f"🎉 好消息！您排隊的【{machine_name}】已經輪到您囉！請盡快前往使用。", icon="🔔")
                    st.session_state[toast_key] = True
    except Exception as e:
        print(f"⚠️ 排隊通知載入錯誤: {e}")

def show_reservation(controller, machine_controller, only_machine_id=None):
    user = st.session_state.user
    
    # 執行個人化排隊到號通知檢查
    notify_queue_notifications(controller, user["id"])
    
    machines = [m for m in machine_controller.get_all_machines()
                if m["is_active"] and (only_machine_id is None or m["id"] == only_machine_id)]
    
    if not machines:
        st.info("目前沒有可排隊的洗衣機。")
        return

    st.subheader("加入洗衣機排隊")
    
    # 建立下拉選單選項，並即時抓取各洗衣機目前的排隊人數
    machine_options = []
    machine_map = {}
    for m in machines:
        queue_count = controller.get_queue_count(m["id"])
        label = f"{m['name']} (目前排隊人數: {queue_count} 人)"
        machine_options.append(label)
        machine_map[label] = m["id"]

    with st.form("queue_form"):
        selected_label = st.selectbox("選擇洗衣機", machine_options)
        submitted = st.form_submit_button("加入排隊", use_container_width=True)

    if submitted:
        machine_id = machine_map[selected_label]
        ok, message = controller.join_queue(user["id"], machine_id)
        (st.success if ok else st.error)(message)
        if ok:
            st.rerun()

    st.divider()
    st.subheader("我的排隊紀錄")
    
    reservations = controller.get_user_reservations(user["id"])
    if only_machine_id is not None:
        reservations = [r for r in reservations if r["machine_id"] == only_machine_id]
        
    if not reservations:
        st.info("目前沒有排隊紀錄。")
        return

    for item in reservations:
        col1, col2 = st.columns([4, 1])
        with col1:
            created_str = item['created_at'].strftime('%Y-%m-%d %H:%M') if item.get('created_at') else ''
            status_text = QUEUE_STATUS_TEXT.get(item['status'], item['status'])
            st.write(f"🧺 **{item['machine_name']}**｜加入排隊時間：{created_str}｜狀態：**{status_text}**")
        with col2:
            # 只有在排隊中或已通知狀態下可以取消
            if item["status"] in ("waiting", "notified") and st.button("取消排隊", key=f"cancel_{item['id']}"):
                if controller.cancel_reservation(user["id"], item["id"]):
                    set_flash(True, "已取消排隊。")
                    st.rerun()
                else:
                    st.error("無法取消此排隊紀錄。")
