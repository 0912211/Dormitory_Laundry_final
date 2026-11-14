import io
import zipfile
from config import APP_BASE_URL

def machine_url(machine_id: int) -> str:
    """每台洗衣機專屬的網址（QR Code 內容）。"""
    return f"{APP_BASE_URL}/?machine={machine_id}"

def make_qr_png(url: str, scale: int = 8) -> bytes:
    """產生 QR Code 的 PNG 圖片位元組。優先使用 segno，其次 qrcode。"""
    try:
        import segno
        buffer = io.BytesIO()
        segno.make(url, error="m").save(buffer, kind="png", scale=scale, border=2)
        return buffer.getvalue()
    except ImportError:
        pass
    try:
        import qrcode
    except ImportError as exc:
        raise RuntimeError("缺少 QR Code 套件，請執行 pip install segno") from exc
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=scale, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    buffer = io.BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buffer, format="PNG")
    return buffer.getvalue()

def make_qr_zip(machines) -> bytes:
    """machines: [{'id':..,'name':..}]，回傳包含全部 QR Code 的 zip。"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for machine in machines:
            archive.writestr(f"machine_{machine['id']}.png", make_qr_png(machine_url(machine["id"])))
    return buffer.getvalue()
