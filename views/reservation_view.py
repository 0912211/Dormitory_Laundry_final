import streamlit as st

# 排隊狀態文字對應
QUEUE_STATUS_TEXT = {
    "waiting": "排隊中",
    "notified": "已輪到您 (請前往使用)",
    "completed": "已完成",
    "cancelled": "已取消"
}

def show_reservation(controller, machine_controller, only_machine_id=None):
    user = st.session_state.user
    
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
                    st.rerun()
