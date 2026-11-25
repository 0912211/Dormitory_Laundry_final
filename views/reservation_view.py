import streamlit as st
from views.flash import set_flash
from views.labels import RESERVATION_STATUS_TEXT


def show_reservation(
    controller,
    machine_controller,
    only_machine_id=None
):
    user_id = st.session_state.user["id"]

    scope = (
        f"machine_{only_machine_id}"
        if only_machine_id is not None
        else "all"
    )

    machines = [
        m for m in machine_controller.get_all_machines()
        if m["is_active"] and (
            only_machine_id is None
            or m["id"] == only_machine_id
        )
    ]

    st.subheader("候補排隊")

    st.caption(
        "不需選擇日期或時段。"
        "洗衣機完全空閒時請直接使用；"
        "有人使用或排隊時可加入候補。"
    )

    if machines:
        names = {
            m["id"]: m["name"]
            for m in machines
        }

        with st.form(f"queue_form_{scope}"):

            machine_id = st.selectbox(
                "選擇洗衣機",
                list(names),
                format_func=names.get
            )

            submitted = st.form_submit_button(
                "加入排隊",
                width="stretch"
            )

        if submitted:
            ok, msg = controller.join_queue(
                user_id,
                machine_id
            )

            set_flash(ok, msg)
            st.rerun()

        for m in machines:
            count = controller.get_queue_count(m["id"])

            st.caption(
                f"{m['name']}｜目前候補 "
                f"{count} 人（含已通知者）"
            )

    else:
        st.info("目前沒有可加入排隊的洗衣機。")

    st.divider()
    st.subheader("我的排隊紀錄")

    rows = controller.get_user_reservations(user_id)

    if only_machine_id is not None:
        rows = [
            r for r in rows
            if r["machine_id"] == only_machine_id
        ]

    if not rows:
        st.info("目前沒有排隊紀錄。")

    for r in rows:

        with st.container(border=True):

            st.write(f"**{r['machine_name']}**")

            st.write(
                f"加入時間："
                f"{r['created_at']:%Y-%m-%d %H:%M}"
            )

            status = RESERVATION_STATUS_TEXT.get(
                r["status"],
                r["status"]
            )

            st.write(f"狀態：{status}")

            if r["status"] == "notified":
                st.success(
                    "已輪到您，請前往洗衣機並開始洗衣。"
                )

            if r["status"] in ("waiting", "notified"):

                if st.button(
                    "取消排隊",
                    key=f"cancel_{scope}_{r['id']}"
                ):

                    ok, msg = controller.cancel_reservation(
                        user_id,
                        r["id"]
                    )

                    set_flash(ok, msg)
                    st.rerun()
