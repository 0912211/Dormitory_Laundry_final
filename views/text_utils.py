"""不依賴 pandas / pyarrow 的簡單表格輔助函式。"""
import re

_MD_SPECIAL = re.compile(r"([\\`*_{}\[\]()#+!|<>~])")

def md_escape(value) -> str:
    """跳脫使用者輸入的文字，避免破壞表格或被當成 Markdown 語法。"""
    text = " ".join(str(value if value is not None else "").split())
    return _MD_SPECIAL.sub(r"\\\1", text)

def md_table(rows, columns, escape_columns=()) -> str:
    """rows: list[dict]；columns: 欄位順序；escape_columns: 需要跳脫的欄位（使用者可輸入的文字）。"""
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, divider]
    for row in rows:
        cells = []
        for col in columns:
            value = row.get(col, "")
            cells.append(md_escape(value) if col in escape_columns else str(value if value is not None else ""))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)
