import streamlit as st

_KEY = "_flash"


def set_flash(ok: bool, message: str) -> None:
    """儲存操作結果。"""

    st.session_state[_KEY] = (ok, message)


def show_flash() -> None:
    """顯示並清除上一輪留下的訊息。"""

    flash = st.session_state.pop(_KEY, None)

    if flash:

        ok, message = flash

        (st.success if ok else st.error)(message)
