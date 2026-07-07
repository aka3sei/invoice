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
    secret_credentials = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(secret_credentials, scopes=scopes)
    return gspread.authorize(credentials)

try:
    gc = get_gspread_client()
    spreadsheet_key = "1fs2WPUVUugxZeobq_fsubPqu9XO1GTr8dWvcgGJPvcA" 
    sh = gc.open_by_key(spreadsheet_key)
    worksheet = sh.worksheet("Daily_Report")
    
except Exception as e:
    st.error("🚨 Google スプレッドシートへの接続に失敗しました。")
    st.code(f"{e}")
    st.stop()


# --- 2. アプリ画面（UI）の構築 ---
st.title("📝 データ入力フォーム")
st.write("スプレッドシートの各項目を入力してください。")

with st.form(key="data_input_form", clear_on_submit=True):
    
    # 📌 基本情報
    st.subheader("👤 基本情報")
    input_date = st.date_input("日付", datetime.date.today())
    staff_name = st.text_input("氏名", placeholder="例: 田中 太郎")
    
    st.markdown("---")
    
    # 📌 matsuri 民泊清掃管理業務委託料
    st.subheader("📁 matsuri 民泊清掃管理業務委託料")
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        fee_A = st.number_input("0.0～30.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_minpaku_A")
        fee_B = st.number_input("30.1～45.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_minpaku_B")
    with col1_2:
        fee_C = st.number_input("45.1～60.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_minpaku_C")
        fee_D = st.number_input("60.1～75.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_minpaku_D")
        
    st.markdown("---")
    
    # 📌 matsuri 管理清掃時業務委託料
    st.subheader("📁 matsuri 管理清掃時業務委託料")
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        fee_E = st.number_input("0.0～30.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_kanri_E")
        fee_F = st.number_input("30.1～45.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_kanri_F")
    with col2_2:
        fee_G = st.number_input("45.1～60.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_kanri_G")
        fee_H = st.number_input("60.1～75.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_kanri_H")
        
    st.markdown("---")
    
    # 📌 matsuri 研修時業務委託料
    st.subheader("📁 matsuri 研修時業務委託料")
    col3_1, col3_2 = st.columns(2)
    with col3_1:
        fee_I = st.number_input("0.0～30.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_kenshu_I")
        fee_J = st.number_input("30.1～45.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_kenshu_J")
    with col3_2:
        fee_K = st.number_input("45.1～60.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_kenshu_K")
        fee_L = st.number_input("60.1～75.0（単位：㎡）", min_value=0, value=0, step=1, key="matsuri_kenshu_L")
        
    submit_button = st.form_submit_button(label="データを送信する")

# --- 3. 送信・データ変換処理 ---
if submit_button:
    if not staff_name:
        st.error("氏名は必ず入力してください。")
    else:
        with st.spinner("データを送信中..."):
            try:
                # 日付フォーマット変換
                formatted_date = input_date.strftime("%Y-%m-%d")
                
                # 🛠️ スプレッドシートの「A列：日付、B列：氏名」から始まる順序に完全一致させたリスト（計14列）
                row_data = [
                    formatted_date, # A列: 日付
                    staff_name,     # B列: 氏名
                    int(fee_A),     # C列
                    int(fee_B),     # D列
                    int(fee_C),     # E列
                    int(fee_D),     # F列
                    int(fee_E),     # G列
                    int(fee_F),     # H列
                    int(fee_G),     # I列
                    int(fee_H),     # J列
                    int(fee_I),     # K列
                    int(fee_J),     # L列
                    int(fee_K),     # M列
                    int(fee_L)      # N列
                ]
                
                # スプレッドシートの最終行に追加
                worksheet.append_row(row_data)
                st.success("🎉 データが正常に登録されました！")
                
            except Exception as e:
                st.error(f"データの送信中にエラーが発生しました: {e}")
                st.code(traceback.format_exc())
