import streamlit as st

def show_login(controller):
    login_tab, register_tab = st.tabs(["登入", "註冊"])
    
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("帳號")
            password = st.text_input("密碼", type="password")
            submitted = st.form_submit_button("登入", width="stretch")
            if submitted:
                user = controller.login(username, password)
                if user:
                    st.session_state.user = user
                    st.success("登入成功！")
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤。")
                    
    with register_tab:
        with st.form("register_form"):
            username = st.text_input("設定帳號 (至少 3 個字元) ")
            
            # 🆕 新增：電子信箱輸入欄位（註冊必填，用於接收洗衣完成通知）
            email = st.text_input("電子信箱 (用於接收洗衣完成通知)")
            
            password = st.text_input("設定密碼 (至少 8 個字元) ", type="password")
            confirm = st.text_input("再次輸入密碼", type="password")
            submitted = st.form_submit_button("建立帳號", width="stretch")
            
        if submitted:
            if password != confirm:
                st.error("兩次輸入的密碼不一致。")
            else:
                # 🆕 傳入 email 給 controller 的 register 方法
                ok, message = controller.register(username, password, email)
                (st.success if ok else st.error)(message)
