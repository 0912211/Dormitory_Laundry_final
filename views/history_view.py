import streamlit as st
from views.labels import CYCLE_STATUS_TEXT

def show_history(controller):
    user_id = st.session_state.user["id"]
    rows = controller.get_user_history(user_id)
    if not rows:
        st.info("目前沒有洗衣紀錄。")
        return
    for row in rows:
        with st.container(border=True):
            st.write(f"**洗衣機：** {row['machine_name']}")
            st.write(f"開始時間：{row['start_time']:%Y-%m-%d %H:%M}")
            st.write(f"預計結束：{row['end_time']:%Y-%m-%d %H:%M}")
            st.write(f"狀態：{CYCLE_STATUS_TEXT.get(row['status'], row['status'])}")
            if row["collected_at"]:
                st.write(f"取衣時間：{row['collected_at']:%Y-%m-%d %H:%M}")
