import streamlit as st


def apply():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans JP', -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ══ Streamlit chrome 非表示 ══ */
[data-testid="stToolbar"]     { display: none !important; }
[data-testid="stDecoration"]  { display: none !important; }
[data-testid="stHeader"]      { display: none !important; }
[data-testid="stMainMenu"]    { display: none !important; }
#MainMenu                     { display: none !important; }
footer                        { display: none !important; }
.viewerBadge_container__r5tak { display: none !important; }

/* ══ サイドバー完全非表示 ══ */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarNav"]     { display: none !important; }

/* ══ 全体レイアウト ══ */
body { background: #F7F8FA !important; }
.stApp { background: #F7F8FA !important; }
.main .block-container {
    padding: 0 2.5rem 3rem !important;
    max-width: 1320px !important;
}

/* ══ トップナビゲーション ══ */
.nav-brand {
    font-size: 0.87rem;
    font-weight: 700;
    color: #171717;
    letter-spacing: -0.01em;
    padding: 0.6rem 0;
    white-space: nowrap;
}
.nav-divider {
    border-bottom: 1px solid #E8E8E8;
    margin: 0.15rem 0 1.8rem;
}

/* ── st.page_link ナビスタイル ── */
[data-testid="stPageLink"] {
    padding: 0 !important;
    margin: 0 !important;
}
[data-testid="stPageLink"] a {
    display: inline-flex !important;
    align-items: center !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #737373 !important;
    padding: 0.45rem 0.6rem !important;
    border-radius: 6px !important;
    text-decoration: none !important;
    transition: background 0.1s, color 0.1s !important;
    white-space: nowrap !important;
    border: none !important;
    background: transparent !important;
    line-height: 1 !important;
}
[data-testid="stPageLink"] a:hover {
    background: #EFEFEF !important;
    color: #171717 !important;
    text-decoration: none !important;
}
[data-testid="stPageLink"] a[aria-current="page"] {
    background: #E8E8E8 !important;
    color: #171717 !important;
    font-weight: 600 !important;
}
/* SVGアイコン非表示 */
[data-testid="stPageLink"] svg { display: none !important; }

/* ══ ホームページ ══ */
.home-header {
    padding: 2.2rem 0 1.8rem;
}
.home-label {
    font-size: 0.67rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #A8A8A8;
    margin-bottom: 0.55rem;
}
.home-title {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.045em;
    color: #171717;
    line-height: 1.1;
    margin: 0;
}

/* ── スタッツカード ── */
.stat-card {
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.5rem;
}
.stat-label {
    font-size: 0.66rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #ABABAB;
    margin-bottom: 0.4rem;
}
.stat-value {
    font-size: 2.1rem;
    font-weight: 700;
    color: #171717;
    letter-spacing: -0.04em;
    line-height: 1;
}
.stat-unit {
    font-size: 0.82rem;
    font-weight: 400;
    color: #ABABAB;
    margin-left: 0.2rem;
    letter-spacing: 0;
}

/* ── ツールカード（ホーム新デザイン） ── */
.tool-card-v2 {
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-radius: 12px;
    padding: 1.8rem 1.8rem 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.15s, box-shadow 0.15s, transform 0.12s;
    min-height: 155px;
}
.tool-card-v2::after {
    content: '';
    position: absolute;
    left: 0; top: 0;
    width: 3px; height: 100%;
    background: #171717;
    transform: scaleY(0);
    transform-origin: top;
    transition: transform 0.2s;
    border-radius: 12px 0 0 12px;
}
.tool-card-v2:hover {
    border-color: #D0D0D0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    transform: translateY(-2px);
}
.tool-card-v2:hover::after { transform: scaleY(1); }
.tc-num {
    font-size: 0.64rem;
    font-weight: 600;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #D0D0D0;
    margin-bottom: 0.85rem;
}
.tc-title {
    font-size: 1rem;
    font-weight: 700;
    color: #171717;
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
}
.tc-desc {
    font-size: 0.79rem;
    color: #737373;
    line-height: 1.62;
    margin-bottom: 0.2rem;
}

/* ══ ページヘッダー（サブページ共通） ══ */
.app-header {
    padding: 1.2rem 0 1.5rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #E8E8E8;
}
.app-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #171717;
    margin: 0 0 0.2rem;
}
.app-header p { font-size: 0.82rem; margin: 0; color: #737373; }

/* ══ メトリクスカード ══ */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.8rem;
    border-left: 3px solid #171717;
}
.metric-card.good { border-left-color: #16A34A; }
.metric-card.warn { border-left-color: #D97706; }
.metric-card.bad  { border-left-color: #DC2626; }
.metric-label {
    font-size: 0.66rem;
    color: #ABABAB;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.metric-value { font-size: 1.6rem; font-weight: 700; color: #171717; margin-top: 0.2rem; }
.score-bar-bg   { background: #F0F0F0; border-radius: 99px; height: 5px; margin-top: 0.5rem; }
.score-bar-fill { height: 5px; border-radius: 99px; }

/* ══ 案件カード ══ */
.project-card {
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.12s;
}
.project-card:hover { border-color: #B0B0B0; }
.project-card .pname   { font-size: 0.92rem; font-weight: 600; color: #171717; }
.project-card .passign { font-size: 0.78rem; color: #737373; margin-top: 0.15rem; }

/* ══ 打合せ進捗ドット ══ */
.progress-pip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 23px; height: 23px;
    border-radius: 50%;
    font-size: 0.63rem;
    font-weight: 600;
    margin-right: 3px;
}
.pip-done  { background: #171717; color: #FFFFFF; }
.pip-empty { background: #F5F5F5; color: #D4D4D4; border: 1px solid #E8E8E8; }

/* ══ ステータスチップ ══ */
.status-chip {
    display: inline-block;
    font-size: 0.67rem;
    font-weight: 600;
    padding: 0.15rem 0.55rem;
    border-radius: 4px;
    letter-spacing: 0.03em;
}
.chip-ok      { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.chip-running { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.chip-warn    { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
.chip-error   { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
.chip-none    { background: #F5F5F5; color: #525252; border: 1px solid #E8E8E8; }

/* ══ 期バッジ ══ */
.term-badge {
    display: inline-block;
    font-size: 0.64rem;
    font-weight: 600;
    padding: 0.1rem 0.45rem;
    border-radius: 3px;
    background: #F5F5F5;
    color: #525252;
    border: 1px solid #E8E8E8;
    margin-left: 0.5rem;
    letter-spacing: 0.03em;
}

/* ══ 所見ボックス ══ */
.summary-box {
    background: #FAFAFA;
    border-left: 3px solid #171717;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    font-size: 0.88rem;
    line-height: 1.72;
    color: #262626;
}

/* ══ チェックアイテム ══ */
.check-item {
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.65rem;
    border-left: 3px solid #E8E8E8;
}
.check-item.ok   { border-left-color: #16A34A; }
.check-item.ng   { border-left-color: #DC2626; background: #FFFCFC; }
.check-item.warn { border-left-color: #D97706; background: #FFFDF5; }
.check-badge { font-size: 0.65rem; font-weight: 600; padding: 0.12rem 0.45rem; border-radius: 3px; white-space: nowrap; }
.badge-ok   { background: #F0FDF4; color: #15803D; }
.badge-ng   { background: #FEF2F2; color: #B91C1C; }
.badge-warn { background: #FFFBEB; color: #B45309; }
.badge-high { background: #FEF2F2; color: #B91C1C; }
.badge-mid  { background: #FFFBEB; color: #B45309; }
.badge-low  { background: #F5F5F5; color: #525252; }
.check-text { flex: 1; }
.check-category { font-size: 0.65rem; color: #ABABAB; letter-spacing: 0.06em; text-transform: uppercase; }
.check-title    { font-size: 0.88rem; font-weight: 500; color: #171717; }
.check-comment  { font-size: 0.78rem; color: #737373; margin-top: 0.1rem; }

/* ══ 合計金額 ══ */
.total-box {
    background: #171717;
    border-radius: 10px;
    padding: 1.5rem 2rem;
    color: #FFFFFF;
    text-align: center;
    margin-top: 1rem;
}
.total-box .label  { font-size: 0.71rem; opacity: 0.5; letter-spacing: 0.09em; text-transform: uppercase; }
.total-box .amount { font-size: 2.1rem; font-weight: 700; letter-spacing: -0.04em; }
.total-box .sub    { font-size: 0.82rem; opacity: 0.5; margin-top: 0.3rem; }

/* ══ ボタン ══ */
[data-testid="stButton"] > button[kind="primary"] {
    background: #171717 !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.01em !important;
    transition: opacity 0.15s !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover { opacity: 0.75 !important; }
[data-testid="stButton"] > button[kind="secondary"] {
    border-radius: 7px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    border-color: #E0E0E0 !important;
    color: #525252 !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: #171717 !important;
    color: #171717 !important;
}

/* ══ タブ ══ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid #E8E8E8;
    padding: 0;
    border-radius: 0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 0 !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    padding: 0.65rem 1.1rem !important;
    border-bottom: 2px solid transparent !important;
    color: #ABABAB !important;
    background: transparent !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: transparent !important;
    box-shadow: none !important;
    border-bottom: 2px solid #171717 !important;
    color: #171717 !important;
}

/* ══ ファイルアップロード ══ */
[data-testid="stFileUploadDropzone"] {
    border: 1.5px dashed #D0D0D0 !important;
    border-radius: 10px !important;
    background: #FAFAFA !important;
    transition: border-color 0.12s !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #171717 !important;
    background: #F5F5F5 !important;
}

/* ══ テーブル ══ */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #E8E8E8 !important;
    box-shadow: none !important;
}

/* ══ エクスパンダー ══ */
[data-testid="stExpander"] {
    border: 1px solid #E8E8E8 !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1rem !important;
    color: #525252 !important;
}
[data-testid="stExpander"] summary:hover { color: #171717 !important; }

/* ══ プロポイント ══ */
.pp-score-card {
    background: #171717;
    border-radius: 10px;
    padding: 1.5rem;
    color: #FFFFFF;
    text-align: center;
}
.pp-score-card .score-val { font-size: 2.7rem; font-weight: 700; letter-spacing: -0.05em; }
.pp-score-card .score-lbl { font-size: 0.67rem; opacity: 0.5; letter-spacing: 0.1em; text-transform: uppercase; }
.pp-breakdown {
    background: #FAFAFA;
    border: 1px solid #E8E8E8;
    border-radius: 10px;
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
    border-radius: 5px;
    margin-top: 0.75rem;
    letter-spacing: 0.05em;
}
.ranking-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1.1rem;
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-radius: 10px;
    margin-bottom: 0.45rem;
}
.ranking-row .rank { font-size: 0.88rem; font-weight: 700; width: 26px; text-align: center; color: #ABABAB; }
.ranking-row .rank.top { color: #171717; }
.ranking-row .name { flex: 1; font-size: 0.92rem; font-weight: 600; color: #171717; }
.ranking-row .pts  { font-size: 1.05rem; font-weight: 700; color: #171717; }

/* ══ セレクトボックス・インプット ══ */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border-color: #E0E0E0 !important;
    border-radius: 7px !important;
    font-size: 0.85rem !important;
}
[data-testid="stTextInput"] input {
    border-color: #E0E0E0 !important;
    border-radius: 7px !important;
    font-size: 0.85rem !important;
}
[data-testid="stTextInput"] input:focus { border-color: #171717 !important; box-shadow: none !important; }

/* ══ 区切り線 ══ */
hr { border-color: #E8E8E8 !important; margin: 1.5rem 0 !important; }

/* ══ info / success / warning / error ══ */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)
