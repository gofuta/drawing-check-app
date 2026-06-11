import sys
from pathlib import Path
import streamlit as st
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

import auth
auth.check_auth()

import style
style.apply()

CSV_PATH = Path(__file__).parent.parent.parent / "data" / "price_master.csv"

st.set_page_config(page_title="単価マスター", page_icon=None, layout="wide")

st.markdown("""
<div class="app-header">
    <h1>単価マスター編集</h1>
    <p>工種・品目ごとの単価を編集できます。変更後は「保存」を押してください。</p>
</div>
""", unsafe_allow_html=True)

try:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
except Exception as e:
    st.error(f"CSVの読み込みに失敗しました: {e}")
    st.stop()

edited = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "工種": st.column_config.TextColumn("工種"),
        "品目": st.column_config.TextColumn("品目"),
        "単位": st.column_config.TextColumn("単位"),
        "単価": st.column_config.NumberColumn("単価（円）", format="¥%d"),
    }
)

if st.button("💾 保存する", type="primary"):
    try:
        edited.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        st.success("保存しました")
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")
