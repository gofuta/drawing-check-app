import hashlib
import os
import streamlit as st
from datetime import datetime


def _get_secret(key: str, default: str = "") -> str:
    val = os.getenv(key, "")
    if val:
        return val
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def _daily_token(password: str) -> str:
    day = datetime.now().strftime('%Y-%m-%d')
    return hashlib.sha256(f"{password}:{day}".encode()).hexdigest()[:20]


def check_auth():
    password = _get_secret("APP_PASSWORD")
    if not password:
        return True

    if st.session_state.get("authenticated"):
        return True

    token = _daily_token(password)

    # URLトークンチェック（ブラウザ更新後も有効・当日中有効）
    try:
        if st.query_params.get("auth") == token:
            st.session_state["authenticated"] = True
            return True
    except Exception:
        pass

    _render_login(password, token)
    st.stop()


def _render_login(password: str, token: str):
    try:
        st.set_page_config(page_title="設計課ポータル", layout="centered")
    except Exception:
        pass

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+JP:wght@300;400;500;700&display=swap');
* { font-family: 'Inter', 'Noto Sans JP', sans-serif !important; -webkit-font-smoothing: antialiased; }
[data-testid="stSidebar"]    { display: none !important; }
[data-testid="stToolbar"]    { display: none !important; }
[data-testid="stHeader"]     { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
#MainMenu                    { display: none !important; }
[data-testid="stMainMenu"]   { display: none !important; }
footer                       { display: none !important; }
.main .block-container       { padding-top: 20vh !important; max-width: 360px !important; }
[data-testid="stTextInput"] input {
    border: 1.5px solid #E5E5E5 !important;
    border-radius: 8px !important;
    font-size: 0.92rem !important;
    padding: 0.75rem 1rem !important;
    background: #FAFAFA !important;
    transition: border-color 0.15s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #0A0A0A !important;
    background: white !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-testid="stButton"] > button {
    background: #0A0A0A !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.03em !important;
    height: 2.8rem !important;
    transition: opacity 0.15s !important;
}
[data-testid="stButton"] > button:hover { opacity: 0.78 !important; }
</style>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="text-align:center;margin-bottom:2.8rem;">
    <div style="
        display:inline-flex;align-items:center;justify-content:center;
        width:54px;height:54px;background:#0A0A0A;border-radius:12px;
        margin-bottom:1.3rem;">
        <span style="color:white;font-size:1.4rem;font-weight:700;letter-spacing:-0.03em;">楓</span>
    </div>
    <h1 style="font-size:1.5rem;font-weight:700;letter-spacing:-0.04em;margin:0 0 0.35rem;color:#0A0A0A;">
        設計課ポータル
    </h1>
    <p style="font-size:0.72rem;color:#A3A3A3;margin:0;letter-spacing:0.12em;text-transform:uppercase;">
        楓工務店 設計課
    </p>
</div>
""", unsafe_allow_html=True)

    pw_input = st.text_input(
        "パスワード",
        type="password",
        placeholder="パスワードを入力",
        label_visibility="collapsed",
        key="login_pw",
    )
    login_btn = st.button("ログイン", use_container_width=True)

    if login_btn:
        if pw_input == password:
            st.session_state["authenticated"] = True
            try:
                st.query_params["auth"] = token
            except Exception:
                pass
            st.rerun()
        else:
            st.markdown("""
<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:7px;
     padding:0.65rem 1rem;font-size:0.83rem;color:#B91C1C;margin-top:0.6rem;text-align:center;">
    パスワードが正しくありません
</div>
""", unsafe_allow_html=True)
