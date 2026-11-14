# 宿舍洗衣機管理系統

## 專案架構
採用 Python + Streamlit + SQLAlchemy，依 MVC 概念分為 models、views、controllers、services、database。

## 安裝
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 執行
```bash
streamlit run main.py
```
瀏覽器開啟 Streamlit 顯示的本機網址（通常為 http://localhost:8501）。

## 功能
- 使用者註冊、登入，密碼以 PBKDF2 雜湊保存
- 三台示範洗衣機狀態
- 開始洗衣、倒數、完成與確認取衣
- 洗衣機預約、時段衝突檢查與取消
- 個人洗衣紀錄
- 頁面開啟時的完成提醒
- 每台洗衣機專屬 QR Code，掃描後直接進入該機器的單機頁面
- 後台管理（僅管理員）：新增／改名／停用洗衣機、強制釋放、QR Code 下載、使用總覽與統計

## 管理員與網址設定
在 Streamlit Secrets（本機為 `.streamlit/secrets.toml`）設定：
```toml
ADMIN_USERNAMES = ["你的管理員帳號"]
APP_BASE_URL = "https://你的app.streamlit.app"
```
- 帳號名稱出現在 `ADMIN_USERNAMES` 的使用者，登入後會看到「後台管理」。
- 部署後請**先自己註冊管理員帳號**，避免別人搶先註冊同名帳號。
- `APP_BASE_URL` 是 QR Code 指向的網址，本機測試預設為 `http://localhost:8501`。

## 注意
- `database/laundry.db` 是 SQLite 資料庫檔案，第一次啟動會自動建立資料表與三台示範洗衣機。
- 此系統為軟體模擬，不會實際控制實體洗衣機。
- 完成提醒目前只在網頁開啟時顯示；瀏覽器關閉後的推播通知尚未實作。
- 若部署至雲端多使用者環境，建議設定 PostgreSQL `DATABASE_URL`，不要依賴雲端暫存檔案系統中的 SQLite。
