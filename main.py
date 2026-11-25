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
from views.help_view import show_help_button


# ==============================
# 網站基本設定
# ==============================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧺",
    layout="wide"
)

# 顯示使用者說明書
show_help_button()


# ==============================
# 初始化資料庫
# ==============================

@st.cache_resource
def initialize_database():

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:

        if db.query(Machine).count() == 0:

            db.add_all([
                Machine(name=f"洗衣機 {i}")
                for i in range(1, DEFAULT_MACHINE_COUNT + 1)
            ])

            db.commit()


initialize_database()


# ==============================
# 登入狀態
# ==============================

if "user" not in st.session_state:
    st.session_state.user = None


# ==============================
# 網站標題
# ==============================

st.title(f"🧺 {APP_NAME}")

st.caption(
    "洗衣機即時狀態查詢｜候補排隊｜"
    "倒數計時｜Email 通知｜洗衣紀錄"
)

st.divider()


# ==============================
# 登入與註冊
# ==============================

if st.session_state.user is None:

    show_login(AuthController())

    st.stop()


# ==============================
# 初始化 Controllers
# ==============================

auth_controller = AuthController()
machine_controller = MachineController()
reservation_controller = ReservationController()
laundry_controller = LaundryController()
admin_controller = AdminController()


# ==============================
# QR Code 頁面切換
# ==============================

def _leave_machine_page():

    st.query_params.clear()


# ==============================
# 功能選單
# ==============================

is_admin = bool(
    st.session_state.user.get("is_admin")
)

pages = [
    "首頁",
    "洗衣機狀態",
    "候補排隊",
    "洗衣紀錄"
]

if is_admin:
    pages.append("後台管理")

# 避免舊版選單狀態造成錯誤
if st.session_state.get("page") not in pages:
    st.session_state.page = "首頁"


# ==============================
# 側邊欄
# ==============================

with st.sidebar:

    st.subheader("功能選單")

    st.write(
        f"👤 目前登入："
        f"{st.session_state.user['username']}"
    )

    if is_admin:
        st.caption("管理員帳號")

    page = st.radio(
        "請選擇功能",
        pages,
        key="page",
        on_change=_leave_machine_page
    )

    st.divider()

    if st.button(
        "🔄 重新整理頁面",
        width="stretch"
    ):

        laundry_controller.update_expired_cycles()

        st.rerun()

    if st.button(
        "登出",
        width="stretch"
    ):

        auth_controller.logout()

        st.session_state.user = None
        st.session_state.pop("page", None)

        st.rerun()


# ==============================
# 更新洗衣與排隊狀態
# ==============================

laundry_controller.update_expired_cycles()

show_flash()


# ==============================
# QR Code 單機頁面
# ==============================

machine_param = st.query_params.get("machine")

if machine_param is not None:

    try:
        machine_id = int(machine_param)

    except (ValueError, TypeError):
        machine_id = None

    show_machine_page(
        machine_controller,
        laundry_controller,
        reservation_controller,
        machine_id
    )


# ==============================
# 首頁與洗衣機狀態
# ==============================

elif page in ("首頁", "洗衣機狀態"):

    st.header(
        "系統首頁"
        if page == "首頁"
        else "洗衣機狀態"
    )

    if page == "首頁":

        st.write(
            "歡迎使用宿舍洗衣機管理系統！"
            "您可以即時查看洗衣機狀態、"
            "加入候補排隊及接收 Email 通知。"
        )

        st.info(
            "💡 洗衣機空閒且無人排隊時，"
            "可直接開始洗衣；"
            "若洗衣機使用中或已有其他人排隊，"
            "請使用候補排隊功能。"
        )

    show_dashboard(
        machine_controller,
        laundry_controller
    )


# ==============================
# 候補排隊
# ==============================

elif page == "候補排隊":

    st.header("候補排隊")

    show_reservation(
        reservation_controller,
        machine_controller
    )


# ==============================
# 洗衣紀錄
# ==============================

elif page == "洗衣紀錄":

    st.header("洗衣紀錄")

    show_history(laundry_controller)


# ==============================
# 管理員後台
# ==============================

elif page == "後台管理":

    st.header("後台管理")

    if is_admin:

        show_admin(
            admin_controller,
            machine_controller
        )

    else:
        st.error("您沒有管理員權限。")


# ==============================
# 網站頁尾
# ==============================

st.divider()

st.caption(
    f"Python 程式語言期末專題｜"
    f"{APP_NAME} v{APP_VERSION}"
)
