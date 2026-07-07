import streamlit as st
import datetime
import uuid
import gspread
from google.oauth2.service_account import Credentials

# ページの設定
st.set_page_config(page_title="清掃業務 報告フォーム", page_icon="📝", layout="centered")

# --- 1. Google スプレッドシート接続設定 ---
# Streamlit Community Cloudの「Secrets」に設定した認証情報を使用します
@st.cache_resource
def get_gspread_client():
    # 必要な権限スコープの定義
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Streamlit Secretsから認証情報を取得
    secret_credentials = dict(st.secrets["gcp_service_account"])
    
    # 認証オブジェクトの作成
    credentials = Credentials.from_service_account_info(secret_credentials, scopes=scopes)
    return gspread.authorize(credentials)

try:
    gc = get_gspread_client()
    # スプレッドシート名（ご自身のシート名に合わせて変更してください）
    # ※裏側でサービスアカウントのメールアドレスに対して、このシートの「編集者」権限を共有しておく必要があります
    spreadsheet_name = "就業管理・請求明細DB" 
    sh = gc.open(spreadsheet_name)
    worksheet = sh.worksheet("Daily_Report")
except Exception as e:
    st.error("Google スプレッドシートへの接続に失敗しました。Secretsの設定やシートの共有設定を確認してください。")
    st.stop()


# --- 2. アプリ画面（UI）の構築 ---
st.title("清掃業務 報告フォーム")
st.write("毎日の業務終了後に、以下の項目を入力して送信してください。")

# フォームの開始
with st.form(key="report_form", clear_on_submit=True):
    
    st.subheader("👤 基本情報")
    # スタッフ氏名（よく稼働するスタッフ名をリストに入れておくと便利です）
    staff_name = st.selectbox(
        "氏名を選択してください",
        ["選択してください", "景 曉風", "スタッフA", "スタッフB"],
        index=0
    )
    
    # 業務日付（デフォルトは今日）
    work_date = st.date_input("業務日付", datetime.date.today())
    
    # 清掃区分
    job_type = st.radio(
        "清掃区分",
        ["民泊清掃", "管理清掃"],
        horizontal=True
    )
    
    st.markdown("---")
    st.subheader("📊 完了件数（平米別）")
    st.caption("該当する平米数の件数を入力してください（＋/ー ボタンで増減できます）")
    
    # 各平米ごとの件数入力（初期値0、最小値0、ステップ1）
    size_30 = st.number_input("0.0 〜 30.0㎡ （件）", min_value=0, value=0, step=1)
    size_45 = st.number_input("30.1 〜 45.0㎡ （件）", min_value=0, value=0, step=1)
    size_60 = st.number_input("45.1 〜 60.0㎡ （件）", min_value=0, value=0, step=1)
    size_75 = st.number_input("60.1 〜 75.0㎡ （件）", min_value=0, value=0, step=1)
    
    st.markdown("---")
    st.subheader("💬 その他")
    # 備考欄
    remarks = st.text_area("備考・連絡事項（任意）", placeholder="現場での特記事項や報告があれば記入してください。")
    
    # 送信ボタン
    submit_button = st.form_submit_button(label="報告を送信する")

# --- 3. 送信処理 ---
if submit_button:
    # バリデーション（氏名が未選択の場合はエラー）
    if staff_name == "選択してください":
        st.error("氏名を選択してください。")
    # 件数がすべて0の場合も警告
    elif size_30 == 0 and size_45 == 0 and size_60 == 0 and size_75 == 0:
        st.error("少なくとも1つの平米区分に1件以上の件数を入力してください。")
    else:
        # 送信データの組み立て
        with st.spinner("データを送信中..."):
            # 一意のIDとタイムスタンプの生成
            report_id = str(uuid.uuid4())
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # スプレッドシートの列順に並べ替えたリスト
            # [ID, タイムスタンプ, 氏名, 日付, 区分, 0-30, 30-45, 45-60, 60-75, 備考]
            row_data = [
                report_id,
                timestamp,
                staff_name,
                str(work_date),
                job_type,
                size_30,
                size_45,
                size_60,
                size_75,
                remarks
            ]
            
            try:
                # スプレッドシートの最終行に追加
                worksheet.append_row(row_data)
                st.success(f"🎉 報告が正常に送信されました！お疲れ様でした。 ({timestamp})")
            except Exception as e:
                st.error(f"データの送信中にエラーが発生しました: {e}")