import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

import auth
auth.check_auth()

import style
style.apply()

import history

st.set_page_config(page_title="解析履歴", page_icon="🗂️", layout="wide")

st.markdown("""
<div class="app-header">
    <h1>🗂️ 解析履歴</h1>
    <p>過去に実行した図面チェックの結果を確認できます。</p>
</div>
""", unsafe_allow_html=True)

records = history.load_history()

if not records:
    st.info("保存された解析履歴がありません。図面チェックを実行すると自動で保存されます。")
    st.stop()

options = {f"{r['timestamp'][:19].replace('T', ' ')}　{r['project_name']}": i for i, r in enumerate(records)}
selected_label = st.selectbox("履歴を選択", list(options.keys()), label_visibility="collapsed")
selected = records[options[selected_label]]

st.markdown("---")

result = selected.get("result", {})
drawing_type = result.get("drawing_type", "不明")
score = result.get("overall_score", 0)
items = result.get("check_items", [])
ng_count = sum(1 for i in items if i.get("status") == "NG")
warn_count = sum(1 for i in items if i.get("status") == "要確認")
score_color = "#22c55e" if score >= 80 else ("#f59e0b" if score >= 60 else "#ef4444")
score_class = "good" if score >= 80 else ("warn" if score >= 60 else "bad")

st.markdown(f"**物件名:** {selected['project_name']}　　**解析日時:** {selected['timestamp'][:19].replace('T', ' ')}")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">図面種別</div><div class="metric-value" style="font-size:1.2rem;">{drawing_type}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card {score_class}"><div class="metric-label">完成度スコア</div><div class="metric-value" style="color:{score_color};">{score}<span style="font-size:1rem;color:#9ca3af;"> / 100</span></div><div class="score-bar-bg"><div class="score-bar-fill" style="width:{score}%;background:{score_color};"></div></div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card bad"><div class="metric-label">NG件数</div><div class="metric-value" style="color:#ef4444;">{ng_count}<span style="font-size:1rem;color:#9ca3af;"> 件</span></div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card warn"><div class="metric-label">要確認件数</div><div class="metric-value" style="color:#f59e0b;">{warn_count}<span style="font-size:1rem;color:#9ca3af;"> 件</span></div></div>', unsafe_allow_html=True)

summary = result.get("summary", "")
if summary:
    st.markdown(f'<div class="summary-box">💬 {summary}</div>', unsafe_allow_html=True)

st.markdown("#### チェック明細")
status_map = {"OK": ("ok", "OK", "badge-ok"), "NG": ("ng", "NG", "badge-ng"), "要確認": ("warn", "要確認", "badge-warn")}
sev_map = {"高": "badge-high", "中": "badge-mid", "低": "badge-low"}

for item in items:
    cls, label, badge_cls = status_map.get(item.get("status", ""), ("", item.get("status", ""), ""))
    sev = item.get("severity", "低")
    sev_cls = sev_map.get(sev, "badge-low")
    comment = item.get("comment", "")
    st.markdown(f"""
    <div class="check-item {cls}">
        <span class="check-badge {badge_cls}">{label}</span>
        <span class="check-badge {sev_cls}">{sev}</span>
        <div class="check-text">
            <div class="check-category">{item.get('category', '')}</div>
            <div class="check-title">{item.get('item', '')}</div>
            {"<div class='check-comment'>" + comment + "</div>" if comment else ""}
        </div>
    </div>""", unsafe_allow_html=True)
