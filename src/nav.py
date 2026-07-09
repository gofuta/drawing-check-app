import streamlit as st

_ITEMS = [
    ("ホーム",       "app.py"),
    ("案件管理",     "pages/1_案件管理.py"),
    ("タスク管理",   "pages/6_タスク管理.py"),
    ("プロポイント", "pages/2_プロポイント.py"),
    ("図面チェック", "pages/3_図面チェック積算.py"),
]


def render():
    """全認証済みページの先頭で呼ぶ。トップナビゲーションバーを描画する。"""
    # ブランド + ナビリンク を1行に並べる
    cols = st.columns([1.3, 0.65, 0.72, 0.78, 0.88, 0.95, 6])

    with cols[0]:
        st.markdown(
            '<div class="nav-brand">K &mdash; 設計課</div>',
            unsafe_allow_html=True,
        )
    for i, (label, path) in enumerate(_ITEMS):
        with cols[i + 1]:
            st.page_link(path, label=label)

    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
