import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent))

import auth
auth.check_auth()

import style
style.apply()

import nav
nav.render()

import gas_sheets

st.set_page_config(
    page_title="設計課ポータル | 楓工務店",
    page_icon=None,
    layout="wide",
)

# ── ページヘッダー ─────────────────────────────────────────
st.markdown("""
<div class="home-header">
    <div class="home-label">楓工務店 設計課</div>
    <div class="home-title">設計課ポータル</div>
</div>
""", unsafe_allow_html=True)

# ── スタッツ（接続時のみ） ────────────────────────────────
connected = gas_sheets.is_connected()
if connected:
    try:
        active_cases = gas_sheets.get_cases(include_done=False)
        done_cases   = gas_sheets.get_cases(include_done=True)
        terms        = gas_sheets.get_all_terms()
        pp_data      = gas_sheets.get_propoints()

        s1, s2, s3, s4 = st.columns(4)
        for col, label, val, unit in [
            (s1, "進行中", len(active_cases), "件"),
            (s2, "完了",   len(done_cases),   "件"),
            (s3, "登録中の期", len(terms),     "期"),
            (s4, "プロポイント", len(pp_data), "件"),
        ]:
            with col:
                st.markdown(f"""
<div class="stat-card">
    <div class="stat-label">{label}</div>
    <div class="stat-value">{val}<span class="stat-unit">{unit}</span></div>
</div>""", unsafe_allow_html=True)
    except Exception:
        pass

# ── ツールカード ──────────────────────────────────────────
st.markdown('<div style="margin-bottom:0.8rem;"></div>', unsafe_allow_html=True)

_CARDS = [
    ("01", "案件管理",     "物件の進捗・打合せ日程・担当者を期ごとに管理します",                "pages/1_案件管理.py"),
    ("02", "プロポイント", "デザインプロポイントのスコア入力・ランキング表示",                  "pages/2_プロポイント.py"),
    ("03", "図面チェック", "AIが建築図面を解析して自動チェックと見積積算を行います",            "pages/3_図面チェック積算.py"),
    ("04", "BPM自動入力",  "Tampermonkeyスクリプトでタスク予定をBPMへ自動登録します",          None),
]

cols = st.columns(4)
for col, (num, title, desc, page_path) in zip(cols, _CARDS):
    with col:
        st.markdown(f"""
<div class="tool-card-v2">
    <div class="tc-num">{num}</div>
    <div class="tc-title">{title}</div>
    <div class="tc-desc">{desc}</div>
</div>""", unsafe_allow_html=True)
        if page_path:
            st.page_link(page_path, label="開く →")
        else:
            st.caption("Tampermonkeyで動作")

if not connected:
    st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)
    st.info("スプレッドシートに接続すると案件数・プロポイントのサマリーが表示されます。")

# ── BPM案内 ──────────────────────────────────────────────
st.markdown("---")
with st.expander("BPM自動入力について"):
    st.markdown("""
**BPM自動入力はTampermonkeyスクリプトで動作します。**

1. ChromeにTampermonkey拡張をインストール
2. `browser/userscript/bpm-auto.user.js` を登録
3. BPMの案件管理ページを開くと自動入力ボタンが表示されます

設定・テンプレートはGoogleスプレッドシート（BPM自動化シート）で管理します。
上の「案件管理」からも物件情報の参照ができます。
    """)
