import streamlit as st

@st.dialog("📖 宿舍洗衣管理系統 — 使用者說明書")
def _open_user_guide():
    st.markdown("### 🧺 核心功能介紹")
    st.markdown(
        """
        1. **即時洗衣機狀態監看**
           * 查看各台洗衣機目前的狀態（**空閒中**、**使用中＋剩餘時間**、**洗衣完成待取衣** 或 **暫停使用**）。
           * 選擇洗衣時間（分鐘）即可一鍵開始洗衣。
        2. **候補排隊制（先到先得）**
           * 當洗衣機正在使用或有人排隊時，可選擇機台並加入排隊佇列，也能即時查看排隊人數。
           * 排隊狀態包含「排隊中」、「已輪到您」、「已完成」與「已取消」，若有變動也可隨時取消排隊。
        3. **Email 自動通知（無干擾介面）**
           * **洗衣完成／取衣提醒**：衣物洗好時會寄送 Email 通知，若逾時未取衣也會定期提醒；領取後請務必點擊「確認已取衣」以釋放機台。
           * **排隊輪到通知**：前一位使用者取衣完成後，系統會自動寄送 Email 通知排隊第一順位的您前往使用。
        4. **歷史紀錄與帳號信箱**
           * 可隨時查閱過往洗衣紀錄；請確保帳號已填寫正確的 Email，才能順利收到通知信。
        """
    )
    st.caption("💡 提示：若未收到通知信，請檢查信箱的「垃圾郵件」或「促銷內容」資料夾。")

def render_help_button(key: str = "help_guide_btn"):
    """渲染右上角圓形問號 '?' 使用者說明書按鈕。"""
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] > button.circle-help-btn,
        button[key*="help_guide"] {
            border-radius: 50% !important;
            width: 42px !important;
            height: 42px !important;
            min-width: 42px !important;
            min-height: 42px !important;
            padding: 0 !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            line-height: 1 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button("?", key=key, help="開啟使用者說明書"):
        _open_user_guide()