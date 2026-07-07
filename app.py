import streamlit as st
import datetime
import gspread
import traceback
from google.oauth2.service_account import Credentials

# ページの設定
st.set_page_config(page_title="データ入力フォーム", page_icon="📝", layout="centered")

# --- 1. Google スプレッドシート接続設定 ---
@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Secretsから認証情報を取得
    secret_credentials = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(secret_credentials, scopes=scopes)
    return gspread.authorize(credentials)

try:
    gc = get_gspread_client()
    # ご指定のスプレッドシートID
    spreadsheet_key = "1fs2WPUVUugxZeobq_fsubPqu9XO1GTr8dWvcgGJPvcA" 
    sh = gc.open_by_key(spreadsheet_key)
    
    # 💡実際のシート名（タブ名）が「Daily_Report」以外の場合は、ここを書き換えてください（例: "シート1" など）
    worksheet = sh.worksheet("Daily_Report")
    
except Exception as e:
    # 🔍 エラーの原因を画面に詳しく特定して表示する機能
    st.error("🚨 Google スプレッドシートへの接続に失敗しました。")
    st.warning("【エラー特定のための詳細メッセージ（ここを教えてください）】")
    st.code(f"{e}")
    st.code(traceback.format_exc())
    st.stop()


# --- 2. アプリ画面（UI）の構築 ---
st.title("📝 データ入力フォーム")
st.write("スプレッドシートの項目を入力してください。")

with st.form(key="data_input_form", clear_on_submit=True):
    
    # 1. 氏名
    staff_name = st.text_input("氏名", placeholder="例: 景 曉風")
    
    # 2. 日付（デフォルトは今日）
    input_date = st.date_input("日付", datetime.date.today())
    
    # 3. 委託料
    fee = st.number_input("委託料（円）", min_value=0, value=0, step=1000)
    
    submit_button = st.form_submit_button(label="データを送信する")

# --- 3. 送信・データ変換処理 ---
if submit_button:
    # バリデーション（必須入力のチェック）
    if not staff_name:
        st.error("氏名は必ず入力してください。")
    elif fee == 0:
        st.error("委託料は0より大きい数値を入力してください。")
    else:
        with st.spinner("データを送信中..."):
            try:
                # 🛠️ 自動採番：現在の最大Noを取得して＋1する
                all_rows = worksheet.get_all_values()
                if len(all_rows) <= 1:
                    next_no = 1
                else:
                    try:
                        next_no = int(all_rows[-1][0]) + 1
                    except:
                        next_no = len(all_rows)
                
                # 🛠️ 日付フォーマット変換：「YYYY-MM-DD」形式
                formatted_date = input_date.strftime("%Y-%m-%d")
                
                # 🛠️ スプレッドシートの項目（列）に完全一致させたデータ構造
                # [No, 氏名, 日付, 委託料]
                row_data = [
                    next_no,
                    staff_name,
                    formatted_date,
                    int(fee)
                ]
                
                # スプレッドシートの最終行に追加
                worksheet.append_row(row_data)
                st.success(f"🎉 No.{next_no} のデータが正常に登録されました！")
                
            except Exception as e:
                st.error(f"データの送信中にエラーが発生しました: {e}")
                st.code(traceback.format_exc())
