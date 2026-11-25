import streamlit as st
from config import APP_NAME, APP_VERSION, DEFAULT_MACHINE_COUNT
from database.db import Base, engine, SessionLocal
from models import User, Machine, Reservation, LaundryCycle
from controllers.auth_controller import AuthController
from controllers.machine_controller import MachineController
from controllers.reservation_controller import ReservationController
from controllers.laundry_controller import LaundryController
from controllers.admin_controller import AdminController
from views.login_view import show_login
from views.dashboard_view import show_dashboard
from views.reservation_view import show_reservation
from views.history_view import show_history
from views.machine_view import show_machine_page
from views.admin_view import show_admin
from views.flash import show_flash

# 🆕 匯入使用者說明書功能
from views.help_view import show_help_button

st.set_page_config(page_title=APP_NAME, page_icon="🧺", layout="wide")

# 🆕 顯示右上角圓形問號按鈕
show_help_button()


@st.cache_resource
def initialize_database():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(Machine).count() == 0:
            db.add_all([Machine(name=f"洗衣機 {i}") for i in range(1, DEFAULT_MACHINE_COUNT + 1)])
            db.commit()


initialize_database()

if "user" not in st.session_state:
    st.session_state.user = None

st.title(f"🧺 {APP_NAME}")
st.caption("洗衣機狀態查詢、洗衣預約、倒數計時與洗衣紀錄")
st.divider()

if st.session_state.user is None:
    show_login(AuthController())
    st.stop()

auth_controller = AuthController()
machine_controller = MachineController()
reservation_controller = ReservationController()
laundry_controller = LaundryController()
admin_controller = AdminController()


def _leave_machine_page():
    # 從單機頁面（QR Code 網址）切換到側邊欄功能時，清除網址參數
    st.query_params.clear()


is_admin = bool(st.session_state.user.get("is_admin"))
pages = ["首頁", "洗衣機狀態", "預約洗衣", "洗衣紀錄"] + (["後台管理"] if is_admin else [])

with st.sidebar:
    st.subheader("功能選單")
    st.write(f"目前登入：{st.session_state.user['username']}")
    page = st.radio("請選擇功能", pages, key="page", on_change=_leave_machine_page)

    # 僅刷新當前頁面，保留登入狀態與目前分頁/網址參數
    if st.button("🔄 重新整理頁面", use_container_width=True):
        laundry_controller.update_expired_cycles()
        st.rerun()

    if st.button("登出", use_container_width=True):
        auth_controller.logout()
        st.session_state.user = None
        st.rerun()

laundry_controller.update_expired_cycles()
show_flash()

machine_param = st.query_params.get("machine")

if machine_param is not None:
    try:
        machine_id = int(machine_param)
    except ValueError:
        machine_id = None

    show_machine_page(
        machine_controller,
        laundry_controller,
        reservation_controller,
        machine_id
    )

elif page in ("首頁", "洗衣機狀態"):
    st.header("系統首頁" if page == "首頁" else "洗衣機狀態")

    if page == "首頁":
        st.write("歡迎使用宿舍洗衣機管理系統。請查看洗衣機狀態，或使用預約功能安排洗衣時間。")

    show_dashboard(machine_controller, laundry_controller)

elif page == "預約洗衣":
    st.header("預約洗衣")
    show_reservation(reservation_controller, machine_controller)

elif page == "洗衣紀錄":
    st.header("洗衣紀錄")
    show_history(laundry_controller)

elif page == "後台管理":
    st.header("後台管理")
    show_admin(admin_controller, machine_controller)

st.divider()
st.caption(f"Python 程式語言期末專題｜{APP_NAME} v{APP_VERSION}")
