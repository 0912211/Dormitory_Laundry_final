import streamlit as st
from config import (
    MIN_WASH_TIME,
    MAX_WASH_TIME,
    DEFAULT_WASH_TIME,
    MIN_RESERVATION_TIME,
    MAX_RESERVATION_TIME,
    MIN_PASSWORD_LENGTH,
)


@st.dialog("📖 使用者說明書", width="large")
def user_manual():

    st.markdown("""
    # 🧺 宿舍洗衣機管理系統

    歡迎使用本系統！您可以透過本網站查詢洗衣機狀態、
    預約洗衣時段、查看剩餘時間及個人洗衣紀錄。
    """)

    st.divider()

    st.markdown(f"""
    ### 1️⃣ 註冊與登入

    - 首次使用請先建立帳號。
    - 帳號至少需要 3 個字元。
    - 密碼至少需要 {MIN_PASSWORD_LENGTH} 個字元。
    - 註冊完成後即可登入系統。

    ### 2️⃣ 查看洗衣機狀態

    透過首頁或側邊欄的「洗衣機狀態」查看設備。

    - 🟢 **目前空閒**：可以開始使用。
    - 🟡 **使用中**：正在洗衣，可查看剩餘時間。
    - 🔵 **洗衣完成**：等待使用者取衣。
    - 🔴 **暫停使用**：設備目前無法使用。

    ### 3️⃣ 開始洗衣

    1. 選擇目前空閒的洗衣機。
    2. 將衣物放入實體洗衣機。
    3. 選擇洗衣時間。
    4. 操作實體洗衣機並點擊「開始洗衣」。
    5. 系統將開始倒數計時。

    - 最短時間：{MIN_WASH_TIME} 分鐘。
    - 最長時間：{MAX_WASH_TIME} 分鐘。
    - 預設時間：{DEFAULT_WASH_TIME} 分鐘。

    ### 4️⃣ 預約洗衣

    1. 點選側邊欄的「預約洗衣」。
    2. 選擇欲使用的洗衣機。
    3. 選擇預約日期及開始時間。
    4. 設定預約使用時間。
    5. 點擊「確認預約」。

    預約時間為 {MIN_RESERVATION_TIME} 至
    {MAX_RESERVATION_TIME} 分鐘。

    若時段已被預約，請選擇其他時間。
    如需取消，可在「我的預約」中點擊取消。

    ### 5️⃣ 洗衣完成與取衣

    - 倒數結束後，系統會更新洗衣機狀態。
    - 收到完成提醒後，請前往洗衣區取衣。
    - 取走衣物後，請點擊「確認已取衣」。
    - 洗衣機即可恢復空閒狀態。

    ### 6️⃣ 查詢洗衣紀錄

    點選側邊欄的「洗衣紀錄」，即可查看：

    - 使用的洗衣機。
    - 洗衣開始時間。
    - 預計完成時間。
    - 目前洗衣狀態。
    - 實際取衣時間。

    ### 7️⃣ QR Code 快速使用

    掃描洗衣機上的 QR Code，
    登入後即可進入該台洗衣機的專屬頁面，
    查看狀態、開始洗衣或進行預約。
    """)

    st.divider()

    st.warning("""
    使用注意事項

    ・請勿擅自移動他人的衣物。

    ・請於洗衣完成後盡快取衣。

    ・請遵守預約時間，避免影響其他使用者。

    ・設備發生異常時，請聯絡宿舍管理員。
    """)

    st.info("本系統主要提供洗衣管理、預約及計時功能。")

    if st.button(
        "我知道了",
        key="close_user_manual",
        width="stretch"
    ):
        st.rerun()


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
