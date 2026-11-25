import re


_MD_SPECIAL = re.compile(
    r"([\\`*_{}\[\]()#+!|<>~])"
)


def md_escape(value) -> str:
    """避免使用者輸入的內容破壞 Markdown 表格。"""

    text = " ".join(
        str(
            value if value is not None else ""
        ).split()
    )

    return _MD_SPECIAL.sub(r"\\\1", text)


def md_table(rows, columns, escape_columns=()):
    """建立 Markdown 表格。"""

    header = "| " + " | ".join(columns) + " |"

    divider = (
        "| "
        + " | ".join("---" for _ in columns)
        + " |"
    )

    lines = [header, divider]

    for row in rows:

        cells = []

        for col in columns:

            value = row.get(col, "")

            cells.append(
                md_escape(value)
                if col in escape_columns
                else str(
                    value if value is not None else ""
                )
            )

        lines.append(
            "| " + " | ".join(cells) + " |"
        )

    return "\n".join(lines)
