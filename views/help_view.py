import streamlit as st

from config import (
    MIN_WASH_TIME,
    MAX_WASH_TIME,
    DEFAULT_WASH_TIME,
    MIN_PASSWORD_LENGTH
)


# ==============================
# 使用者說明書
# ==============================

@st.dialog("📖 使用者說明書", width="large")
def user_manual():

    st.markdown(f"""
    # 🧺 宿舍洗衣機管理系統

    歡迎使用宿舍洗衣機管理系統！
    本系統提供即時洗衣機查詢、候補排隊、
    倒數計時及 Email 通知等功能。

    ---

    ### 1️⃣ 註冊與登入

    首次使用請先建立個人帳號。

    - 帳號至少需要 3 個字元。
    - 密碼至少需要 {MIN_PASSWORD_LENGTH} 個字元。
    - 請填寫正確的電子信箱。
    - 註冊完成後即可登入。

    電子信箱將用於接收洗衣完成、
    取衣提醒及候補排隊通知。

    ---

    ### 2️⃣ 查看洗衣機狀態

    進入首頁或「洗衣機狀態」，
    即可查看各台洗衣機的即時資訊。

    - 🟢 目前空閒：洗衣機目前沒有使用者。
    - 🟡 使用中：洗衣機正在使用。
    - 🔵 洗衣完成：等待使用者取衣。
    - 🔴 暫停使用：設備目前無法使用。

    也可以查看剩餘洗衣時間與候補排隊人數。

    ---

    ### 3️⃣ 開始洗衣

    1. 選擇空閒且無人候補的洗衣機。
    2. 將衣物放入實體洗衣機。
    3. 設定預計洗衣時間。
    4. 啟動實體洗衣機。
    5. 點擊網站上的「開始洗衣」。

    洗衣時間設定：

    - 最短：{MIN_WASH_TIME} 分鐘。
    - 最長：{MAX_WASH_TIME} 分鐘。
    - 預設：{DEFAULT_WASH_TIME} 分鐘。

    注意：本網站提供計時與管理功能，
    不會直接啟動實體洗衣機。

    ---

    ### 4️⃣ 預約洗衣（候補排隊）

    本系統採用候補排隊制度，
    不需要選擇預約日期或預約時段。

    **加入排隊方式：**

    1. 進入側邊欄的「預約洗衣」。
    2. 選擇欲使用的洗衣機。
    3. 點擊「加入排隊」。
    4. 等待前一位使用者完成洗衣及取衣。
    5. 輪到您時，系統會嘗試寄送 Email 通知。
    6. 前往洗衣機並開始洗衣。

    也可以直接透過洗衣機卡片上的
    「加入排隊」按鈕進行候補。

    **排隊狀態說明：**

    - 排隊中：正在等待使用。
    - 已通知可洗衣：已輪到您使用。
    - 已完成排隊：已完成候補流程。
    - 已取消：已取消候補資格。

    如不需要繼續等待，
    可以在「我的排隊紀錄」取消排隊。

    完全空閒且無人排隊的洗衣機，
    不需要預約，可直接使用。

    ---

    ### 5️⃣ 洗衣完成與取衣

    洗衣倒數結束後，
    系統會更新洗衣機狀態，
    並嘗試寄送洗衣完成通知。

    若尚未取衣，在系統持續執行狀態更新
    且郵件設定正常的情況下，
    每隔至少 10 分鐘會再次提醒。

    取走衣物後，
    請務必點擊「確認已取衣」。

    系統將釋放洗衣機，
    並通知下一位候補使用者。

    ---

    ### 6️⃣ 洗衣紀錄

    點擊側邊欄的「洗衣紀錄」，
    即可查看個人歷史紀錄。

    包含：

    - 使用的洗衣機。
    - 洗衣開始時間。
    - 預計完成時間。
    - 洗衣狀態。
    - 實際取衣時間。

    ---

    ### 7️⃣ QR Code 快速使用

    1. 掃描洗衣機上的 QR Code。
    2. 登入個人帳號。
    3. 進入指定洗衣機的專屬頁面。
    4. 查看目前狀態。
    5. 開始洗衣或加入候補排隊。

    ---

    ### 8️⃣ Email 通知功能

    系統會依照使用情況寄送：

    - 洗衣完成通知。
    - 尚未取衣提醒。
    - 候補排隊輪候通知。

    如果沒有收到通知，
    請確認註冊信箱是否正確，
    並查看垃圾郵件及網站目前狀態。
    """)

    st.warning("""
    ⚠️ 使用注意事項

    ・請勿擅自移動他人的衣物。

    ・洗衣完成後請盡快取衣。

    ・取衣後請務必點擊「確認已取衣」。

    ・請遵守候補排隊順序。

    ・如遇設備故障，請聯絡宿舍管理員。
    """)

    if st.button(
        "我知道了",
        key="close_user_manual",
        width="stretch"
    ):

        st.rerun()


# ==============================
# 圓形問號按鈕
# ==============================

def show_help_button():

    st.markdown("""
    <style>

    .st-key-user_manual_button {
        position: fixed;
        top: 75px;
        right: 25px;
        width: 48px !important;
        z-index: 999;
    }

    .st-key-user_manual_button button {
        width: 48px !important;
        height: 48px !important;
        min-height: 48px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        background-color: #2563EB !important;
        color: white !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }

    .st-key-user_manual_button button p {
        font-size: 28px !important;
        font-weight: bold !important;
        color: white !important;
    }

    .st-key-user_manual_button button:hover {
        background-color: #1D4ED8 !important;
        transform: scale(1.1);
        cursor: pointer;
    }

    .st-key-user_manual_button button:active {
        transform: scale(0.95);
    }

    @media (max-width: 600px) {

        .st-key-user_manual_button {
            top: 65px;
            right: 12px;
            width: 42px !important;
        }

        .st-key-user_manual_button button {
            width: 42px !important;
            height: 42px !important;
            min-height: 42px !important;
        }

    }

    </style>
    """, unsafe_allow_html=True)

    with st.container(key="user_manual_button"):

        if st.button(
            "?",
            key="open_user_manual",
            help="點擊查看使用者說明書"
        ):

            user_manual()
