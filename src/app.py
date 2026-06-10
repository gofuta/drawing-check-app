import streamlit as st
import sys
import os
from pathlib import Path
import fitz
from PIL import Image
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent))

import auth
auth.check_auth()

import checker
import estimator
import sheets_exporter
import history
import demo_data

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _get_secret(key: str, default: str = "") -> str:
    val = os.getenv(key, "")
    if val:
        return val
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


ENV_API_KEY = _get_secret("ANTHROPIC_API_KEY")
ENV_CREDS_FILE = _get_secret("GOOGLE_CREDENTIALS_FILE")
ENV_SHEET_URL = _get_secret("GOOGLE_SPREADSHEET_URL")

st.set_page_config(
    page_title="図面チェック・自動見積積算",
    page_icon="📐",
    layout="wide",
)

# ── カスタムCSS ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif;
}

/* ヘッダーエリア */
.app-header {
    background: linear-gradient(135deg, #0f2942 0%, #1a4a7a 100%);
    padding: 2rem 2.5rem 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
}
.app-header h1 {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0 0 0.3rem 0;
    color: white;
}
.app-header p {
    font-size: 0.9rem;
    margin: 0;
    opacity: 0.75;
}

/* メトリクスカード */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 4px solid #1a4a7a;
    margin-bottom: 0.8rem;
}
.metric-card.good { border-left-color: #22c55e; }
.metric-card.warn { border-left-color: #f59e0b; }
.metric-card.bad  { border-left-color: #ef4444; }
.metric-label { font-size: 0.75rem; color: #6b7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-value { font-size: 1.6rem; font-weight: 700; color: #111827; margin-top: 0.2rem; }

/* チェックアイテム */
.check-item {
    background: white;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    display: flex;
    align-items: center;
    gap: 0.8rem;
    border-left: 3px solid #e5e7eb;
}
.check-item.ok   { border-left-color: #22c55e; }
.check-item.ng   { border-left-color: #ef4444; background: #fff8f8; }
.check-item.warn { border-left-color: #f59e0b; background: #fffbf0; }
.check-badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    white-space: nowrap;
}
.badge-ok   { background: #dcfce7; color: #166534; }
.badge-ng   { background: #fee2e2; color: #991b1b; }
.badge-warn { background: #fef3c7; color: #92400e; }
.badge-high { background: #fee2e2; color: #991b1b; }
.badge-mid  { background: #fef3c7; color: #92400e; }
.badge-low  { background: #f3f4f6; color: #374151; }
.check-text { flex: 1; }
.check-category { font-size: 0.72rem; color: #9ca3af; }
.check-title { font-size: 0.92rem; font-weight: 500; color: #111827; }
.check-comment { font-size: 0.82rem; color: #6b7280; margin-top: 0.15rem; }

/* スコアリング */
.score-bar-bg {
    background: #e5e7eb;
    border-radius: 99px;
    height: 10px;
    margin-top: 0.4rem;
}
.score-bar-fill {
    height: 10px;
    border-radius: 99px;
    transition: width 0.5s ease;
}

/* 所見ボックス */
.summary-box {
    background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-size: 0.92rem;
    line-height: 1.7;
    color: #1e3a5f;
}

/* 合計金額 */
.total-box {
    background: linear-gradient(135deg, #0f2942 0%, #1a4a7a 100%);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    color: white;
    text-align: center;
    margin-top: 1rem;
}
.total-box .label { font-size: 0.85rem; opacity: 0.75; }
.total-box .amount { font-size: 2.2rem; font-weight: 700; letter-spacing: -0.02em; }
.total-box .sub { font-size: 0.9rem; opacity: 0.8; margin-top: 0.3rem; }

/* アップロードエリア */
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #cbd5e1 !important;
    border-radius: 14px !important;
    background: #f8fafc !important;
    padding: 2rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #1a4a7a !important;
    background: #f0f7ff !important;
}

/* ボタン */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0f2942, #1a4a7a) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    padding: 0.65rem 1.5rem !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* サイドバー */
[data-testid="stSidebar"] {
    background: #0f2942 !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.2) !important;
}

/* タブ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px;
    background: #f1f5f9;
    border-radius: 10px;
    padding: 4px;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 500 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: white !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}

/* テーブル */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}

/* divider */
hr { border-color: #e5e7eb !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── ヘッダー ──────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>📐 図面チェック・自動見積積算</h1>
    <p>建築図面をアップロードするとAIが自動でチェックと積算を行います</p>
</div>
""", unsafe_allow_html=True)

# ── サイドバー ────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ 設定")

    if ENV_API_KEY:
        api_key = ENV_API_KEY
        st.success("✅ APIキー設定済み")
    else:
        api_key = st.text_input("Anthropic API Key", type="password")

    project_name = st.text_input("📁 物件名", value="物件名未設定")

    st.markdown("---")
    st.markdown("### 📊 スプレッドシート")

    if ENV_SHEET_URL:
        sheet_url = ENV_SHEET_URL
        st.success("✅ URL設定済み")
    else:
        sheet_url = st.text_input("URL", placeholder="https://docs.google.com/...")

    sheet_name = st.text_input("シート名", value="積算")

    if ENV_CREDS_FILE and Path(ENV_CREDS_FILE).exists():
        credentials_path = ENV_CREDS_FILE
        st.success("✅ 認証設定済み")
    else:
        creds_file = st.file_uploader("サービスアカウントJSON", type=["json"])
        if creds_file:
            creds_save_path = OUTPUT_DIR / "service_account_tmp.json"
            creds_save_path.write_bytes(creds_file.read())
            credentials_path = str(creds_save_path)
        else:
            credentials_path = ""

    st.markdown("---")
    st.caption("対応形式: PDF / PNG / JPG")
    st.markdown("")
    if st.button("🎮 デモモードで試す", use_container_width=True):
        st.session_state["result"] = demo_data.get_demo_result()
        st.session_state["project_name"] = "デモ物件"
        st.rerun()

# ── メインエリア ──────────────────────────────────────
uploaded = st.file_uploader(
    "図面をドラッグ＆ドロップ、またはクリックして選択",
    type=["pdf", "png", "jpg", "jpeg"],
)

if uploaded is None:
    st.markdown("""
    <div style="text-align:center; padding:3rem; color:#94a3b8; font-size:0.95rem;">
        図面ファイルをアップロードするか、サイドバーの「デモモードで試す」をお使いください
    </div>
    """, unsafe_allow_html=True)
    st.stop()

file_bytes = uploaded.read()
media_type = "image/png"

if uploaded.type == "application/pdf":
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img_bytes = pix.tobytes("png")
    media_type = "image/png"
else:
    img_bytes = file_bytes
    media_type = uploaded.type

col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("**アップロード図面**")
    st.image(img_bytes, use_container_width=True)

with col2:
    if not api_key:
        st.error("APIキーを入力してください（サイドバー）")
        st.stop()
    st.markdown("")
    if st.button("🔍 チェック・積算を実行", type="primary", use_container_width=True):
        with st.spinner("AIが図面を解析中...（30秒〜1分程度）"):
            try:
                result = checker.check_drawing(img_bytes, media_type, api_key)
                st.session_state["result"] = result
                st.session_state["project_name"] = project_name
                history.save_history(project_name, result)
            except Exception as e:
                st.error(f"解析エラー: {e}")
                st.stop()

if "result" not in st.session_state:
    st.stop()

result = st.session_state["result"]
pname = st.session_state.get("project_name", "物件名未設定")

# ── タブ ────────────────────────────────────────────
tab_check, tab_estimate = st.tabs(["　📋 図面チェック結果　", "　💴 自動積算　"])

# ── チェック結果タブ ──────────────────────────────────
with tab_check:
    drawing_type = result.get("drawing_type", "不明")
    score = result.get("overall_score", 0)
    summary = result.get("summary", "")
    items = result.get("check_items", [])
    ng_count = sum(1 for i in items if i["status"] == "NG")
    warn_count = sum(1 for i in items if i["status"] == "要確認")
    ok_count = sum(1 for i in items if i["status"] == "OK")

    score_color = "#22c55e" if score >= 80 else ("#f59e0b" if score >= 60 else "#ef4444")
    score_class = "good" if score >= 80 else ("warn" if score >= 60 else "bad")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">図面種別</div>
            <div class="metric-value" style="font-size:1.2rem;">{drawing_type}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card {score_class}">
            <div class="metric-label">完成度スコア</div>
            <div class="metric-value" style="color:{score_color};">{score}<span style="font-size:1rem;color:#9ca3af;"> / 100</span></div>
            <div class="score-bar-bg"><div class="score-bar-fill" style="width:{score}%;background:{score_color};"></div></div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card bad">
            <div class="metric-label">NG件数</div>
            <div class="metric-value" style="color:#ef4444;">{ng_count}<span style="font-size:1rem;color:#9ca3af;"> 件</span></div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card warn">
            <div class="metric-label">要確認 / OK</div>
            <div class="metric-value" style="font-size:1.2rem;">
                <span style="color:#f59e0b;">{warn_count}</span>
                <span style="font-size:0.9rem;color:#9ca3af;"> / </span>
                <span style="color:#22c55e;">{ok_count}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="summary-box">💬 {summary}</div>', unsafe_allow_html=True)

    st.markdown("#### チェック明細")

    status_map = {"OK": ("ok", "OK", "badge-ok"), "NG": ("ng", "NG", "badge-ng"), "要確認": ("warn", "要確認", "badge-warn")}
    sev_map = {"高": "badge-high", "中": "badge-mid", "低": "badge-low"}

    for item in items:
        cls, label, badge_cls = status_map.get(item["status"], ("", item["status"], ""))
        sev = item.get("severity", "低")
        sev_cls = sev_map.get(sev, "badge-low")
        comment = item.get("comment", "")
        st.markdown(f"""
        <div class="check-item {cls}">
            <span class="check-badge {badge_cls}">{label}</span>
            <span class="check-badge {sev_cls}">{sev}</span>
            <div class="check-text">
                <div class="check-category">{item['category']}</div>
                <div class="check-title">{item['item']}</div>
                {"<div class='check-comment'>" + comment + "</div>" if comment else ""}
            </div>
        </div>""", unsafe_allow_html=True)

# ── 積算タブ ──────────────────────────────────────────
with tab_estimate:
    import pandas as pd
    quantities = result.get("quantities", {})

    st.markdown("#### 抽出数量")
    q_cols = st.columns(6)
    q_items = [
        ("延床面積", quantities.get("floor_area"), "m²"),
        ("建築面積", quantities.get("building_area"), "m²"),
        ("階数", quantities.get("stories"), "階"),
        ("窓数", quantities.get("window_count"), "箇所"),
        ("ドア数", quantities.get("door_count"), "箇所"),
        ("外壁周長", quantities.get("outer_wall_length"), "m"),
    ]
    for idx, (label, val, unit) in enumerate(q_items):
        with q_cols[idx]:
            display = f"{val}{unit}" if val is not None else "—"
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;border-left:none;border-top:3px solid #1a4a7a;">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="font-size:1.3rem;">{display}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    estimate_items = estimator.estimate_from_quantities(quantities)

    if not estimate_items:
        st.warning("数量情報が不足しているため積算できません。")
        st.stop()

    st.markdown("#### 積算明細")
    df = pd.DataFrame(estimate_items)
    df_display = df.copy()
    df_display["金額"] = df_display["金額"].map("¥{:,}".format)
    df_display["単価"] = df_display["単価"].map("¥{:,}".format)
    st.dataframe(df_display[["工種", "品目", "数量", "単位", "単価", "金額"]], use_container_width=True, hide_index=True)

    total = sum(i["金額"] for i in estimate_items)
    tax = int(total * 0.1)
    st.markdown(f"""
    <div class="total-box">
        <div class="label">税込合計（概算）</div>
        <div class="amount">¥{total + tax:,}</div>
        <div class="sub">税抜 ¥{total:,}　＋　消費税 ¥{tax:,}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    out_col1, out_col2 = st.columns(2)

    with out_col1:
        st.markdown("**📊 Googleスプレッドシートに転記**")
        if not sheet_url:
            st.caption("サイドバーでURLを設定してください")
        elif not credentials_path:
            st.caption("サイドバーで認証JSONを設定してください")
        else:
            if st.button("スプレッドシートに転記", type="primary", use_container_width=True):
                with st.spinner("転記中..."):
                    try:
                        res = sheets_exporter.write_estimate(
                            spreadsheet_url=sheet_url,
                            credentials_path=credentials_path,
                            items=estimate_items,
                            project_name=pname,
                            sheet_name=sheet_name,
                        )
                        st.success("転記完了！")
                        st.markdown(f"[スプレッドシートを開く]({res['url']})")
                    except Exception as e:
                        st.error(f"転記エラー: {e}")

    with out_col2:
        st.markdown("**📥 Excel出力**")
        if st.button("Excel見積書をダウンロード", use_container_width=True):
            output_path = OUTPUT_DIR / f"見積書_{pname}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            estimator.export_excel(estimate_items, output_path, pname)
            with open(output_path, "rb") as f:
                st.download_button(
                    label="⬇️ ダウンロード",
                    data=f.read(),
                    file_name=output_path.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
