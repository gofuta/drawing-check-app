import streamlit as st


def apply():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans JP', sans-serif; }

/* ── Streamlit標準UIを非表示 ── */
[data-testid="stToolbar"]    { display: none !important; }
[data-testid="stHeader"]     { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
#MainMenu                    { display: none !important; }
footer                       { display: none !important; }
.viewerBadge_container__r5tak { display: none !important; }

/* ── ヘッダーエリア ── */
.app-header {
    background: linear-gradient(135deg, #0f2942 0%, #1a4a7a 100%);
    padding: 2rem 2.5rem 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
}
.app-header h1 { font-size: 1.8rem; font-weight: 700; margin: 0 0 0.3rem; color: white; }
.app-header p  { font-size: 0.9rem; margin: 0; opacity: 0.75; }

/* ── メトリクスカード ── */
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
.score-bar-bg   { background: #e5e7eb; border-radius: 99px; height: 10px; margin-top: 0.4rem; }
.score-bar-fill { height: 10px; border-radius: 99px; }

/* ── チェックアイテム ── */
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
.check-badge { font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.6rem; border-radius: 20px; white-space: nowrap; }
.badge-ok   { background: #dcfce7; color: #166534; }
.badge-ng   { background: #fee2e2; color: #991b1b; }
.badge-warn { background: #fef3c7; color: #92400e; }
.badge-high { background: #fee2e2; color: #991b1b; }
.badge-mid  { background: #fef3c7; color: #92400e; }
.badge-low  { background: #f3f4f6; color: #374151; }
.check-text { flex: 1; }
.check-category { font-size: 0.72rem; color: #9ca3af; }
.check-title    { font-size: 0.92rem; font-weight: 500; color: #111827; }
.check-comment  { font-size: 0.82rem; color: #6b7280; margin-top: 0.15rem; }

/* ── 所見ボックス ── */
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

/* ── 合計金額 ── */
.total-box {
    background: linear-gradient(135deg, #0f2942 0%, #1a4a7a 100%);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    color: white;
    text-align: center;
    margin-top: 1rem;
}
.total-box .label  { font-size: 0.85rem; opacity: 0.75; }
.total-box .amount { font-size: 2.2rem; font-weight: 700; letter-spacing: -0.02em; }
.total-box .sub    { font-size: 0.9rem; opacity: 0.8; margin-top: 0.3rem; }

/* ── アップロードエリア ── */
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #cbd5e1 !important;
    border-radius: 14px !important;
    background: #f8fafc !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #1a4a7a !important;
    background: #f0f7ff !important;
}

/* ── ボタン ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0f2942, #1a4a7a) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── サイドバー ── */
[data-testid="stSidebar"] { background: #0f2942 !important; }
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

/* ── タブ ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px;
    background: #f1f5f9;
    border-radius: 10px;
    padding: 4px;
}
[data-testid="stTabs"] [data-baseweb="tab"] { border-radius: 8px !important; font-weight: 500 !important; }
[data-testid="stTabs"] [aria-selected="true"] {
    background: white !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}

/* ── テーブル ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}

hr { border-color: #e5e7eb !important; margin: 1.5rem 0 !important; }
</style>

<script>
// ファイルアップローダーの英語テキストを日本語に置換
function japanizeUploader() {
    const replacements = {
        'Drag and drop file here': 'ここにファイルをドラッグ＆ドロップ',
        'Drag and drop files here': 'ここにファイルをドラッグ＆ドロップ',
        'Browse files': 'ファイルを選択',
        'Limit': '上限',
        'per file': '/ファイル',
    };
    document.querySelectorAll('span, button, p, div').forEach(el => {
        if (el.children.length === 0) {
            let text = el.textContent;
            let changed = false;
            for (const [en, ja] of Object.entries(replacements)) {
                if (text.includes(en)) { text = text.replace(en, ja); changed = true; }
            }
            if (changed) el.textContent = text;
        }
    });
}
const observer = new MutationObserver(japanizeUploader);
observer.observe(document.body, { childList: true, subtree: true });
japanizeUploader();
</script>
""", unsafe_allow_html=True)
