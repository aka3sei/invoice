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
    staff_name = st.text_input("氏名", placeholder="例: 田中　太郎")
    input_date = st.date_input("日付", datetime.date.today())
    
    st.markdown("---")
    
    # 📌 matsuri 民泊清掃管理業務委託料 (項目C〜F)
    st.subheader("📁 matsuri 民泊清掃管理業務委託料")
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        fee_A = st.number_input("0.0～30.0（単位：㎡）", min_value=0, value=0, step=1)
        fee_B = st.number_input("30.1～45.0（単位：㎡）", min_value=0, value=0, step=1)
    with col1_2:
        fee_C = st.number_input("45.1～60.0（単位：㎡）", min_value=0, value=0, step=1)
        fee_D = st.number_input("60.1～75.0（単位：㎡）", min_value=0, value=0, step=1)
        
    st.markdown("---")
    
    # 📌 matsuri 管理清掃時業務委託料 (項目G〜J)
    st.subheader("📁 matsuri 管理清掃時業務委託料")
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        fee_E = st.number_input("0.0～30.0（単位：㎡）", min_value=0, value=0, step=1)
        fee_F = st.number_input("30.1～45.0（単位：㎡）", min_value=0, value=0, step=1)
    with col2_2:
        fee_G = st.number_input("45.1～60.0（単位：㎡）", min_value=0, value=0, step=1)
        fee_H = st.number_input("60.1～75.0（単位：㎡）", min_value=0, value=0, step=1)
        
    st.markdown("---")
    
    # 📌 matsuri 研修時業務委託料 (項目K〜N) 
    st.subheader("📁 matsuri 研修時業務委託料")
    col3_1, col3_2 = st.columns(2)
    with col3_1:
        fee_I = st.number_input("0.0～30.0（単位：㎡）", min_value=0, value=0, step=1)
        fee_J = st.number_input("30.1～45.0（単位：㎡）", min_value=0, value=0, step=1)
    with col3_2:
        fee_K = st.number_input("45.1～60.0（単位：㎡）", min_value=0, value=0, step=1)
        fee_L = st.number_input("60.1～75.0（単位：㎡）", min_value=0, value=0, step=1)
        
    submit_button = st.form_submit_button(label="データを送信する")

# --- 3. 送信・データ変換処理 ---
if submit_button:
    if not staff_name:
        st.error("氏名は必ず入力してください。")
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
                
                # 🛠️ 日付フォーマット変換
                formatted_date = input_date.strftime("%Y-%m-%d")
                
                # 🛠️ 自動計算：12個の項目（A〜L）の金額をすべて合算して「委託料(合計)」を算出
                total_fee = (
                    fee_A + fee_B + fee_C + fee_D +
                    fee_E + fee_F + fee_G + fee_H +
                    fee_I + fee_J + fee_K + fee_L
                )
                
                # 🛠️ A列からN列までの14項目を完全に一致させたデータリスト
                # [No, 氏名, 日付, 項目A, 項目B, 項目C, 項目D, 項目E, 項目F, 項目G, 項目H, 項目I, 項目J, 委託料]
                row_data = [
                    next_no,
                    staff_name,
                    formatted_date,
                    int(fee_A), # D列
                    int(fee_B), # E列
                    int(fee_C), # F列
                    int(fee_D), # G列
                    int(fee_E), # H列
                    int(fee_F), # I列
                    int(fee_G), # J列
                    int(fee_H), # K列
                    int(fee_I), # L列
                    int(fee_J), # M列
                    int(total_fee) # N列: 委託料合計
                ]
                
                # スプレッドシートの最終行に追加
                worksheet.append_row(row_data)
                st.success(f"🎉 No.{next_no} のデータが正常に登録されました！（委託料合計: {total_fee:,}円）")
                
            except Exception as e:
                st.error(f"データの送信中にエラーが発生しました: {e}")
                st.code(traceback.format_exc())
