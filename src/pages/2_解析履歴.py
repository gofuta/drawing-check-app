import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

import auth
auth.check_auth()

import history

st.set_page_config(page_title="解析履歴", page_icon="🗂️", layout="wide")
st.title("🗂️ 解析履歴")

records = history.load_history()

if not records:
    st.info("保存された解析履歴がありません")
    st.stop()

options = {f"{r['timestamp'][:19]}　{r['project_name']}": i for i, r in enumerate(records)}
selected_label = st.selectbox("履歴を選択", list(options.keys()))
selected = records[options[selected_label]]

st.divider()

result = selected.get("result", {})
st.subheader(f"物件名: {selected['project_name']}")
st.caption(f"解析日時: {selected['timestamp'][:19]}")

drawing_type = result.get("drawing_type", "不明")
score = result.get("overall_score", 0)
items = result.get("check_items", [])
ng_count = sum(1 for i in items if i.get("status") == "NG")

c1, c2, c3 = st.columns(3)
c1.metric("図面種別", drawing_type)
c2.metric("完成度スコア", f"{score} / 100")
c3.metric("NG件数", f"{ng_count} 件")

summary = result.get("summary", "")
if summary:
    st.info(summary)

status_icon = {"OK": "✅", "NG": "❌", "要確認": "⚠️"}
severity_color = {"高": "🔴", "中": "🟡", "低": "🟢"}

for item in items:
    icon = status_icon.get(item.get("status"), "❓")
    sev = severity_color.get(item.get("severity", "低"), "")
    label = f"{icon} {sev} [{item.get('category', '')}] {item.get('item', '')}"
    with st.expander(label, expanded=(item.get("status") == "NG")):
        st.write(f"**ステータス**: {item.get('status', '-')}")
        st.write(f"**重大度**: {item.get('severity', '-')}")
        st.write(f"**コメント**: {item.get('comment', '-')}")
