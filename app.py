import streamlit as st
import datetime
import gspread
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
    # ご指定のスプレッドシートID
    spreadsheet_key = "1fs2WPUVUugxZeobq_fsubPqu9XO1GTr8dWvcgGJPvcA" 
    sh = gc.open_by_key(spreadsheet_key)
    worksheet = sh.worksheet("Daily_Report")
except Exception as e:
    st.error(f"Google スプレッドシートへの接続に失敗しました。詳細エラー: {e}")
    st.stop()


# --- 2. アプリ画面（UI）の構築 ---
st.title("📝 データ入力フォーム")
st.write("スプレッドシートの項目を入力してください。")

with st.form(key="data_input_form", clear_on_submit=True):
    
    # 1. 所在地
    location = st.text_input("所在地")
    
    # 2. マンション名
    mansion_name = st.text_input("マンション名")
    
    st.markdown("---")
    
    # 3. 合計賃料（円）※賃料と管理費（共益費）を合算した金額
    total_rent = st.number_input("合計賃料（円）", min_value=0, value=0, step=1000)
    
    # 4. 専有面積（㎡）
    area = st.number_input("専有面積（㎡）", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    
    st.markdown("---")
    
    # 5. 築年
    age = st.number_input("築年", min_value=0, value=0, step=1)
    
    # 6. 駅徒歩（分）
    walk_time = st.number_input("駅徒歩（分）", min_value=0, value=0, step=1)
    
    st.markdown("---")
    
    # 7. 成約日（デフォルトは今日）
    contract_date = st.date_input("成約日", datetime.date.today())
    
    submit_button = st.form_submit_button(label="データを送信する")

# --- 3. 送信・データ変換処理 ---
if submit_button:
    # バリデーション（必須項目のチェック）
    if not location or not mansion_name:
        st.error("所在地とマンション名は必ず入力してください。")
    elif total_rent == 0 or area == 0.0:
        st.error("合計賃料と専有面積は0より大きい数値を入力してください。")
    else:
        with st.spinner("データを送信中..."):
            try:
                # 🛠️ 自動計算：平米単価（合計賃料 ÷ 専有面積、小数点以下切り捨て）
                price_per_m2 = int(total_rent // area)
                
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
                formatted_date = contract_date.strftime("%Y-%m-%d")
                
                # 🛠️ スプレッドシートの項目（列）に完全一致させたデータ構造
                # [No, 所在地, マンション名, 合計賃料(円), 専有面積(㎡), 平米単価(円/㎡), 築年, 駅徒歩(分), 成約日]
                row_data = [
                    next_no,
                    location,
                    mansion_name,
                    int(total_rent),
                    float(area),
                    price_per_m2,
                    int(age),
                    int(walk_time),
                    formatted_date
                ]
                
                # スプレッドシートの最終行に追加
                worksheet.append_row(row_data)
                st.success(f"🎉 No.{next_no} のデータが正常に登録されました！")
                
            except Exception as e:
                st.error(f"データの送信中にエラーが発生しました: {e}")
