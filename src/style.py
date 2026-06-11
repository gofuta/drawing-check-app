import streamlit as st


def apply():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ── Streamlit標準UI非表示 ── */
[data-testid="stToolbar"]    { display: none !important; }
[data-testid="stHeader"]     { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
#MainMenu                    { display: none !important; }
footer                       { display: none !important; }
.viewerBadge_container__r5tak { display: none !important; }
[data-testid="stMainMenu"]   { display: none !important; }

/* ── ポータルヘッダー ── */
.portal-header {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid #E5E5E5;
    margin-bottom: 2rem;
}
.portal-header .company-label {
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #A3A3A3;
    margin-bottom: 0.5rem;
}
.portal-header h1 {
    font-size: 1.9rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #0A0A0A;
    margin: 0;
}

/* ── ページヘッダー（サブページ） ── */
.app-header {
    padding: 1.5rem 0 1.2rem;
    border-bottom: 2px solid #0A0A0A;
    margin-bottom: 1.5rem;
    background: none;
    border-radius: 0;
    color: #0A0A0A;
}
.app-header h1 {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #0A0A0A;
    margin: 0 0 0.25rem;
}
.app-header p  { font-size: 0.82rem; margin: 0; color: #737373; }

/* ── メトリクスカード ── */
.metric-card {
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.8rem;
    border-left: 3px solid #0A0A0A;
}
.metric-card.good { border-left-color: #16A34A; }
.metric-card.warn { border-left-color: #D97706; }
.metric-card.bad  { border-left-color: #DC2626; }
.metric-label {
    font-size: 0.68rem;
    color: #A3A3A3;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.metric-value { font-size: 1.6rem; font-weight: 700; color: #0A0A0A; margin-top: 0.2rem; }
.score-bar-bg   { background: #F5F5F5; border-radius: 99px; height: 5px; margin-top: 0.5rem; }
.score-bar-fill { height: 5px; border-radius: 99px; }

/* ── ツールカード（ホーム） ── */
.tool-card {
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 1.5rem;
    height: 100%;
    transition: border-color 0.15s, transform 0.1s;
}
.tool-card:hover { border-color: #0A0A0A; transform: translateY(-1px); }
.tool-card h3 { font-size: 0.92rem; font-weight: 600; color: #0A0A0A; margin: 0 0 0.4rem; }
.tool-card p  { font-size: 0.8rem; color: #737373; margin: 0; line-height: 1.55; }

/* ── 案件カード ── */
.project-card {
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.55rem;
    transition: border-color 0.15s;
}
.project-card:hover { border-color: #A3A3A3; }
.project-card .pname   { font-size: 0.92rem; font-weight: 600; color: #0A0A0A; }
.project-card .passign { font-size: 0.78rem; color: #737373; margin-top: 0.15rem; }

/* ── 打合せ進捗ドット ── */
.progress-pip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px; height: 24px;
    border-radius: 50%;
    font-size: 0.64rem;
    font-weight: 600;
    margin-right: 3px;
}
.pip-done  { background: #0A0A0A; color: white; }
.pip-empty { background: #F5F5F5; color: #D4D4D4; border: 1px solid #E5E5E5; }

/* ── ステータスチップ ── */
.status-chip {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 0.15rem 0.55rem;
    border-radius: 4px;
    letter-spacing: 0.03em;
}
.chip-ok      { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.chip-running { background: #F0F9FF; color: #0369A1; border: 1px solid #BAE6FD; }
.chip-warn    { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
.chip-error   { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
.chip-none    { background: #F5F5F5; color: #525252; border: 1px solid #E5E5E5; }

/* ── 期バッジ ── */
.term-badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 0.1rem 0.45rem;
    border-radius: 3px;
    background: #F5F5F5;
    color: #525252;
    border: 1px solid #E5E5E5;
    margin-left: 0.5rem;
    letter-spacing: 0.03em;
}

/* ── 所見ボックス ── */
.summary-box {
    background: #FAFAFA;
    border-left: 3px solid #0A0A0A;
    border-radius: 0 6px 6px 0;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #262626;
}

/* ── チェックアイテム ── */
.check-item {
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.65rem;
    border-left: 3px solid #E5E5E5;
}
.check-item.ok   { border-left-color: #16A34A; }
.check-item.ng   { border-left-color: #DC2626; background: #FFFCFC; }
.check-item.warn { border-left-color: #D97706; background: #FFFDF5; }
.check-badge { font-size: 0.66rem; font-weight: 600; padding: 0.12rem 0.45rem; border-radius: 3px; white-space: nowrap; }
.badge-ok   { background: #F0FDF4; color: #15803D; }
.badge-ng   { background: #FEF2F2; color: #B91C1C; }
.badge-warn { background: #FFFBEB; color: #B45309; }
.badge-high { background: #FEF2F2; color: #B91C1C; }
.badge-mid  { background: #FFFBEB; color: #B45309; }
.badge-low  { background: #F5F5F5; color: #525252; }
.check-text { flex: 1; }
.check-category { font-size: 0.66rem; color: #A3A3A3; letter-spacing: 0.06em; text-transform: uppercase; }
.check-title    { font-size: 0.88rem; font-weight: 500; color: #0A0A0A; }
.check-comment  { font-size: 0.78rem; color: #737373; margin-top: 0.1rem; }

/* ── 合計金額 ── */
.total-box {
    background: #0A0A0A;
    border-radius: 8px;
    padding: 1.5rem 2rem;
    color: white;
    text-align: center;
    margin-top: 1rem;
}
.total-box .label  { font-size: 0.72rem; opacity: 0.55; letter-spacing: 0.08em; text-transform: uppercase; }
.total-box .amount { font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; }
.total-box .sub    { font-size: 0.82rem; opacity: 0.55; margin-top: 0.3rem; }

/* ── プライマリボタン ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: #0A0A0A !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.15s !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover { opacity: 0.78 !important; }
[data-testid="stButton"] > button[kind="secondary"] {
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.86rem !important;
}

/* ── サイドバー ── */
[data-testid="stSidebar"] {
    background: #0A0A0A !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #D4D4D4 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: white !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: rgba(255,255,255,0.09) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: white !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.16) !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── タブ ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid #E5E5E5;
    padding: 0;
    border-radius: 0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 0 !important;
    font-weight: 500 !important;
    font-size: 0.86rem !important;
    padding: 0.65rem 1.1rem !important;
    border-bottom: 2px solid transparent !important;
    color: #A3A3A3 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: transparent !important;
    box-shadow: none !important;
    border-bottom: 2px solid #0A0A0A !important;
    color: #0A0A0A !important;
}

/* ── アップロード ── */
[data-testid="stFileUploadDropzone"] {
    border: 1px dashed #D4D4D4 !important;
    border-radius: 8px !important;
    background: #FAFAFA !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #0A0A0A !important;
    background: #F5F5F5 !important;
}

/* ── テーブル ── */
[data-testid="stDataFrame"] {
    border-radius: 8px !important;
    overflow: hidden !important;
    border: 1px solid #E5E5E5 !important;
    box-shadow: none !important;
}

/* ── プロポイント ── */
.pp-score-card {
    background: #0A0A0A;
    border-radius: 8px;
    padding: 1.5rem;
    color: white;
    text-align: center;
}
.pp-score-card .score-val { font-size: 2.6rem; font-weight: 700; letter-spacing: -0.04em; }
.pp-score-card .score-lbl { font-size: 0.68rem; opacity: 0.55; letter-spacing: 0.1em; text-transform: uppercase; }
.pp-breakdown {
    background: #FAFAFA;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 1rem;
    font-size: 0.84rem;
}
.pp-breakdown .row { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #F0F0F0; }
.pp-breakdown .row:last-child { border-bottom: none; }
.pp-status {
    display: inline-block;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 0.3rem 0.9rem;
    border-radius: 4px;
    margin-top: 0.75rem;
    letter-spacing: 0.05em;
}
.ranking-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1rem;
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    margin-bottom: 0.45rem;
}
.ranking-row .rank { font-size: 0.9rem; font-weight: 700; width: 28px; text-align: center; color: #0A0A0A; }
.ranking-row .name { flex: 1; font-size: 0.92rem; font-weight: 600; color: #0A0A0A; }
.ranking-row .pts  { font-size: 1.05rem; font-weight: 700; color: #0A0A0A; }

hr { border-color: #E5E5E5 !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)
