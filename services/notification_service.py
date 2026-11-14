def notify_completion(message: str) -> None:
    """顯示頁面內提醒；關閉瀏覽器後的推播需另接 Web Push 服務。"""
    import streamlit as st
    st.toast(message, icon="🎉")
