import os
import streamlit as st


def _get_secret(key: str, default: str = "") -> str:
    """環境変数 → Streamlit Secrets の順で取得する"""
    val = os.getenv(key, "")
    if val:
        return val
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def check_auth():
    password = _get_secret("APP_PASSWORD")
    if not password:
        return True

    if st.session_state.get("authenticated"):
        return True

    st.title("🔒 アクセス認証")
    entered = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if entered == password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()
