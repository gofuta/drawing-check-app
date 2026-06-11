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

import gas_sheets

st.set_page_config(
    page_title="設計課ポータル | 楓工務店",
    page_icon=None,
    layout="wide",
)

# ── ヘッダー ──────────────────────────────────────────
st.markdown("""
<div class="portal-header">
    <div class="company-label">楓工務店 設計課</div>
    <h1>設計課ポータル</h1>
</div>
""", unsafe_allow_html=True)

# ── サイドバー ────────────────────────────────────────
with st.sidebar:
    st.markdown("### 設計課ポータル")
    st.caption("楓工務店 設計課")
    st.markdown("---")

    connected = gas_sheets.is_connected()
    if connected:
        st.success("スプレッドシート 接続中")
    else:
        st.warning("スプレッドシート 未接続")
        st.caption("Secrets に BPM_SHEET_ID と gcp_service_account を設定してください")

    st.markdown("---")
    st.caption("左のメニューから各ツールを選択")

# ── ツールカード ──────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="tool-card">
        <h3>案件管理</h3>
        <p>物件の進捗・打合せ日程・担当者を期ごとに管理します</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="tool-card">
        <h3>プロポイント</h3>
        <p>デザインプロポイントのスコア入力・ランキング表示</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="tool-card">
        <h3>図面チェック・積算</h3>
        <p>AIが建築図面を解析して自動チェックと見積積算を行います</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="tool-card">
        <h3>BPM自動入力</h3>
        <p>BPMへのタスク予定を自動登録します（Tampermonkeyスクリプト）</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ── クイックスタッツ（接続時のみ） ──────────────────
if connected:
    st.markdown("### 現在の状況")
    try:
        active_cases = gas_sheets.get_cases(include_done=False)
        done_cases   = gas_sheets.get_cases(include_done=True)
        terms        = gas_sheets.get_all_terms()
        pp_data      = gas_sheets.get_propoints()

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">進行中 物件</div>
                <div class="metric-value">{len(active_cases)}<span style="font-size:1rem;color:#9ca3af;"> 件</span></div>
            </div>""", unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
            <div class="metric-card good">
                <div class="metric-label">完了 物件</div>
                <div class="metric-value" style="color:#22c55e;">{len(done_cases)}<span style="font-size:1rem;color:#9ca3af;"> 件</span></div>
            </div>""", unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">登録中 期</div>
                <div class="metric-value">{len(terms)}<span style="font-size:1rem;color:#9ca3af;"> 期</span></div>
            </div>""", unsafe_allow_html=True)
        with s4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">プロポイント記録</div>
                <div class="metric-value">{len(pp_data)}<span style="font-size:1rem;color:#9ca3af;"> 件</span></div>
            </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"データ取得エラー: {e}")

else:
    st.info("スプレッドシートに接続すると、案件数・プロポイントなどのサマリーが表示されます。")

# ── BPM自動入力案内 ────────────────────────────────────
st.markdown("---")
with st.expander("BPM自動入力について"):
    st.markdown("""
**BPM自動入力はTampermonkeyスクリプトで動作します。**

1. ChromeにTampermonkey拡張をインストール
2. `browser/userscript/bpm-auto.user.js` を登録
3. BPMの案件管理ページを開くと自動入力ボタンが表示されます

設定・テンプレートはGoogleスプレッドシート（BPM自動化シート）で管理します。
左メニューの「案件管理」からも物件情報の参照ができます。
    """)
