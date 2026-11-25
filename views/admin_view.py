import streamlit as st

from config import APP_BASE_URL
from views.flash import set_flash

from views.labels import (
    CYCLE_STATUS_TEXT,
    RESERVATION_STATUS_TEXT
)

from views.text_utils import md_table


def _fmt(value):
    return (
        value.strftime("%Y-%m-%d %H:%M")
        if value else ""
    )


def _machine_state(machine):

    if not machine["is_active"]:
        return "已停用"

    return {
        "washing": "使用中",
        "finished": "待取衣"
    }.get(machine["cycle_status"], "空閒")


# ==============================
# 洗衣機管理
# ==============================

def _machine_tab(
    admin_controller,
    machine_controller,
    admin_id
):

    st.subheader("新增洗衣機")

    with st.form(
        "add_machine_form",
        clear_on_submit=True
    ):

        name = st.text_input(
            "洗衣機名稱",
            placeholder="例如：洗衣機 4"
        )

        submitted = st.form_submit_button(
            "新增洗衣機"
        )

    if submitted:

        ok, message = admin_controller.add_machine(
            admin_id,
            name
        )

        set_flash(ok, message)
        st.rerun()

    st.divider()
    st.subheader("洗衣機清單")

    machines = machine_controller.get_all_machines()

    if not machines:
        st.info("目前沒有洗衣機，請先新增。")

    for machine in machines:

        with st.container(border=True):

            st.caption(
                f"編號 {machine['id']}｜"
                f"目前狀態：{_machine_state(machine)}"
            )

            new_name = st.text_input(
                "名稱",
                value=machine["name"],
                key=f"name_{machine['id']}"
            )

            col1, col2, col3 = st.columns(3)

            if col1.button(
                "儲存名稱",
                key=f"rename_{machine['id']}",
                width="stretch"
            ):

                ok, message = admin_controller.rename_machine(
                    admin_id,
                    machine["id"],
                    new_name
                )

                set_flash(ok, message)
                st.rerun()

            toggle_label = (
                "停用"
                if machine["is_active"]
                else "啟用"
            )

            if col2.button(
                toggle_label,
                key=f"toggle_{machine['id']}",
                width="stretch"
            ):

                ok, message = admin_controller.set_machine_active(
                    admin_id,
                    machine["id"],
                    not machine["is_active"]
                )

                set_flash(ok, message)
                st.rerun()

            busy = machine["cycle_status"] in (
                "washing",
                "finished"
            )

            if col3.button(
                "強制釋放",
                key=f"release_{machine['id']}",
                disabled=not busy,
                width="stretch",
                help="使用者忘記取衣時，可結束目前洗衣紀錄。"
            ):

                ok, message = admin_controller.force_release(
                    admin_id,
                    machine["id"]
                )

                set_flash(ok, message)
                st.rerun()


# ==============================
# QR Code 管理
# ==============================

def _qr_tab(admin_controller, machine_controller):

    st.subheader("洗衣機 QR Code")

    if APP_BASE_URL.startswith(
        ("http://localhost", "http://127.0.0.1")
    ):

        st.warning(
            "目前網站網址是 localhost，"
            "手機掃描可能無法連線。"
            "請在 Secrets 設定 APP_BASE_URL。"
        )

    st.caption(
        f"目前網址基底：{APP_BASE_URL}｜"
        "可使用瀏覽器列印功能（Ctrl+P）。"
    )

    machines = machine_controller.get_all_machines()

    if not machines:
        st.info("目前沒有洗衣機。")
        return

    try:

        zip_data = admin_controller.qr_zip(machines)

        pngs = {
            m["id"]: admin_controller.qr_png(m["id"])
            for m in machines
        }

    except RuntimeError as exc:

        st.error(str(exc))
        return

    st.download_button(
        "下載全部 QR Code（zip）",
        data=zip_data,
        file_name="machine_qrcodes.zip",
        mime="application/zip"
    )

    columns = st.columns(3)

    for index, machine in enumerate(machines):

        with columns[index % 3]:

            with st.container(border=True):

                st.markdown(
                    f"**{machine['name']}**"
                    + (
                        "（已停用）"
                        if not machine["is_active"]
                        else ""
                    )
                )

                st.image(
                    pngs[machine["id"]],
                    width=220
                )

                st.caption(
                    admin_controller.machine_url(
                        machine["id"]
                    )
                )

                st.download_button(
                    "下載 PNG",
                    data=pngs[machine["id"]],
                    file_name=(
                        f"machine_{machine['id']}.png"
                    ),
                    mime="image/png",
                    key=f"dl_{machine['id']}"
                )


# ==============================
# 使用總覽
# ==============================

def _overview_tab(admin_controller, admin_id):

    st.subheader("最近洗衣紀錄（最多 200 筆）")

    cycles = admin_controller.list_all_cycles(admin_id)

    if cycles:

        st.markdown(
            md_table(
                [
                    {
                        "洗衣機": c["machine_name"],
                        "使用者": c["username"],
                        "開始": _fmt(c["start_time"]),
                        "預計結束": _fmt(c["end_time"]),
                        "狀態": CYCLE_STATUS_TEXT.get(
                            c["status"],
                            c["status"]
                        ),
                        "取衣/結束時間": _fmt(
                            c["collected_at"]
                        ),
                    }
                    for c in cycles
                ],
                [
                    "洗衣機",
                    "使用者",
                    "開始",
                    "預計結束",
                    "狀態",
                    "取衣/結束時間"
                ],
                escape_columns=("洗衣機", "使用者")
            )
        )

    else:
        st.info("目前沒有洗衣紀錄。")

    st.subheader("最近排隊紀錄（最多 200 筆）")

    reservations = (
        admin_controller.list_all_reservations(
            admin_id
        )
    )

    if reservations:

        st.markdown(
            md_table(
                [
                    {
                        "洗衣機": r["machine_name"],
                        "使用者": r["username"],
                        "加入時間": _fmt(r["created_at"]),
                        "狀態": RESERVATION_STATUS_TEXT.get(
                            r["status"],
                            r["status"]
                        ),
                    }
                    for r in reservations
                ],
                [
                    "洗衣機",
                    "使用者",
                    "加入時間",
                    "狀態"
                ],
                escape_columns=("洗衣機", "使用者")
            )
        )

    else:
        st.info("目前沒有排隊紀錄。")


# ==============================
# 使用統計
# ==============================

def _bars(items):

    items = list(items)

    peak = max(
        (count for _, count in items),
        default=0
    )

    for label, count in items:

        st.progress(
            count / peak if peak else 0.0,
            text=f"{label}：{count} 次"
        )


def _stats_tab(admin_controller, admin_id):

    stats = admin_controller.usage_stats(admin_id)

    if not stats:
        st.info("沒有統計資料。")
        return

    st.metric(
        "累計洗衣次數",
        stats["total"]
    )

    if stats["total"] == 0:

        st.info(
            "還沒有洗衣紀錄，"
            "使用後這裡會顯示統計圖。"
        )

        return

    st.subheader("各洗衣機使用次數")

    _bars(stats["per_machine"].items())

    st.subheader("各時段開始洗衣次數")

    _bars(
        (f"{hour:02d} 時", count)
        for hour, count
        in stats["per_hour"].items()
        if count > 0
    )


# ==============================
# 使用者管理
# ==============================

def _users_tab(admin_controller, admin_id):

    users = admin_controller.list_users(admin_id)

    st.subheader(
        f"使用者（共 {len(users)} 人）"
    )

    if users:

        st.markdown(
            md_table(
                [
                    {
                        "編號": u["id"],
                        "帳號": u["username"],
                        "電子信箱": u.get("email") or "",
                        "建立時間": _fmt(u["created_at"]),
                        "管理員": "是" if u["is_admin"] else "",
                    }
                    for u in users
                ],
                [
                    "編號",
                    "帳號",
                    "電子信箱",
                    "建立時間",
                    "管理員"
                ],
                escape_columns=("帳號", "電子信箱")
            )
        )


# ==============================
# 候補排隊管理
# ==============================

def _queue_tab(admin_controller, admin_id):

    st.subheader("各洗衣機即時排隊名單")

    machines = (
        admin_controller.get_machines_queue_status(
            admin_id
        )
    )

    for machine in machines:

        with st.container(border=True):

            st.write(
                f"**{machine['machine_name']}**｜"
                f"候補 {machine['queue_count']} 人"
            )

            if not machine["is_active"]:
                st.warning("已停用")

            if not machine["queue_list"]:

                st.caption("目前無人排隊")

            else:

                st.markdown(
                    md_table(
                        [
                            {
                                "順位": i,
                                "帳號": r["username"],
                                "加入時間": _fmt(
                                    r["created_at"]
                                ),
                                "狀態": (
                                    RESERVATION_STATUS_TEXT.get(
                                        r["status"],
                                        r["status"]
                                    )
                                ),
                            }
                            for i, r in enumerate(
                                machine["queue_list"],
                                1
                            )
                        ],
                        [
                            "順位",
                            "帳號",
                            "加入時間",
                            "狀態"
                        ],
                        escape_columns=("帳號",)
                    )
                )


# ==============================
# 管理員主頁面
# ==============================

def show_admin(
    admin_controller,
    machine_controller
):

    admin_id = st.session_state.user["id"]

    if not admin_controller.is_admin(admin_id):

        st.error("沒有管理員權限。")
        return

    tabs = st.tabs([
        "洗衣機管理",
        "QR Code",
        "使用總覽",
        "使用統計",
        "使用者",
        "排隊管理"
    ])

    with tabs[0]:
        _machine_tab(
            admin_controller,
            machine_controller,
            admin_id
        )

    with tabs[1]:
        _qr_tab(
            admin_controller,
            machine_controller
        )

    with tabs[2]:
        _overview_tab(
            admin_controller,
            admin_id
        )

    with tabs[3]:
        _stats_tab(
            admin_controller,
            admin_id
        )

    with tabs[4]:
        _users_tab(
            admin_controller,
            admin_id
        )

    with tabs[5]:
        _queue_tab(
            admin_controller,
            admin_id
        )
