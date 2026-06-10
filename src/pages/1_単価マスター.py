import sys
from pathlib import Path
import streamlit as st
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

import auth
auth.check_auth()

CSV_PATH = Path(__file__).parent.parent.parent / "data" / "price_master.csv"

st.set_page_config(page_title="単価マスター編集", page_icon="📋", layout="wide")
st.title("📋 単価マスター編集")

try:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
except Exception as e:
    st.error(f"CSVの読み込みに失敗しました: {e}")
    st.stop()

edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")

if st.button("💾 保存", type="primary"):
    try:
        edited.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        st.success("保存しました")
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")
