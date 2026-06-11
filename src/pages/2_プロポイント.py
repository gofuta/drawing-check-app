import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv(Path(__file__).parent.parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

import auth
auth.check_auth()

import style
style.apply()

import nav
nav.render()

import gas_sheets
import propoints as pp

st.set_page_config(
    page_title="プロポイント | 設計課ポータル",
    page_icon=None,
    layout="wide",
)

st.markdown("""
<div class="app-header">
    <h1>デザインプロポイント</h1>
    <p>スコア入力・ランキング表示</p>
</div>
""", unsafe_allow_html=True)

if not gas_sheets.is_connected():
    st.error("スプレッドシートに接続できません。Secrets の設定を確認してください。")
    st.stop()

# ── フィルター行 ─────────────────────────────────────────
terms = gas_sheets.get_all_terms() or []
_fc1, _fc2, _fc_sp = st.columns([1.8, 2, 6.2])
with _fc1:
    selected_term = st.selectbox("表示する期", ['すべて'] + terms)
with _fc2:
    view_mode = st.radio("表示モード", ['入力・編集', 'ランキング'], horizontal=True)

# ── データ取得 ───────────────────────────────────────────
term_filter  = None if selected_term == 'すべて' else selected_term
cases_active = gas_sheets.get_cases(term=term_filter, include_done=False)
cases_done   = gas_sheets.get_cases(term=term_filter, include_done=True)
all_cases    = cases_active + cases_done
pp_data      = gas_sheets.get_propoints(term=term_filter)
pp_index     = {d['project_name']: d for d in pp_data}

# ====================================================
# 入力・編集モード
# ====================================================
if view_mode == '入力・編集':

    if not all_cases:
        st.info("この期に物件がありません。案件管理から物件を追加してください。")
        st.stop()

    st.markdown(f"**{selected_term if term_filter else 'すべての期'}** — {len(all_cases)} 件")
    st.markdown("---")
    st.markdown("#### スコア入力")

    col_form, col_result = st.columns([3, 2])

    with col_form:
        case_names = [c['project_name'] for c in all_cases]
        sel_case   = st.selectbox("物件名 *", case_names, key="pp_case")
        sel_prod   = st.selectbox("商品種別 *", pp.PRODUCTS, key="pp_prod")
        col_a, col_b = st.columns(2)
        with col_a:
            sel_acc  = st.number_input("精度 (%)", min_value=0, max_value=100, value=95, step=1, key="pp_acc")
            sel_type = st.selectbox("建物種別", pp.BUILDING_TYPES, key="pp_type")
        with col_b:
            sel_hrs  = st.number_input("工数 (h)", min_value=0.0, max_value=200.0, value=60.0, step=0.5, key="pp_hrs")

        matched      = next((c for c in all_cases if c['project_name'] == sel_case), None)
        sel_assignee = matched['assignee']    if matched else ''
        sel_term_v   = matched.get('term', '') if matched else ''

        existing = pp_index.get(sel_case)
        if existing:
            st.caption(f"既存データあり（最終更新: {existing.get('registered_at', '—')}）。保存すると上書きします。")

        if st.button("保存", type="primary", use_container_width=True, key="pp_save"):
            score_save = pp.calculate(sel_prod, sel_acc, sel_hrs, sel_type)
            gas_sheets.save_propoint({
                'project_name' : sel_case,
                'assignee'     : sel_assignee,
                'term'         : sel_term_v,
                'product'      : sel_prod,
                'accuracy'     : sel_acc,
                'hours'        : sel_hrs,
                'building_type': sel_type,
                'product_pt'   : score_save['product_pt'],
                'accuracy_pt'  : score_save['accuracy_pt'],
                'workload_pt'  : score_save['workload_pt'],
                'total_score'  : score_save['total_score'],
                'status'       : score_save['status'],
            }, row_number=existing['_row'] if existing else None)
            st.success(f"「{sel_case}」を保存しました — {score_save['status']}  合計: {score_save['total_score']:.3f}")
            st.rerun()

    with col_result:
        score = pp.calculate(sel_prod, sel_acc, sel_hrs, sel_type)
        bg, fg = pp.status_color(score['status'])
        st.markdown(f"""
<div class="pp-score-card">
    <div class="score-lbl">合計スコア（リアルタイム）</div>
    <div class="score-val">{score['total_score']:.3f}</div>
    <div class="pp-status" style="background:{bg};color:{fg};">{score['status']}</div>
</div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
<div class="pp-breakdown" style="margin-top:0.75rem;">
    <div class="row"><span>商品Pt ({sel_prod})</span><span><b>{score['product_pt']:.1f}</b></span></div>
    <div class="row"><span>精度Pt ({sel_acc}%)</span><span><b>{score['accuracy_pt']:.1f}</b></span></div>
    <div class="row"><span>工数Pt ({sel_hrs}h / {sel_type})</span><span><b>{score['workload_pt']:.1f}</b></span></div>
    <div class="row" style="font-weight:700;"><span>合計スコア</span><span>{score['total_score']:.3f}</span></div>
    <div class="row"><span>判定スコア (精度×工数)</span><span>{score['perf_score']:.3f}</span></div>
</div>
        """, unsafe_allow_html=True)

    if pp_data:
        st.markdown("---")
        st.markdown("#### 登録済み")
        for d in sorted(pp_data, key=lambda x: float(x.get('total_score') or 0), reverse=True):
            bg2, fg2 = pp.status_color(d.get('status', ''))
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                term_b = f'<span class="term-badge">{d["term"]}</span>' if d.get('term') else ''
                st.markdown(f"""
<div style="padding:0.5rem 0;">
    <span style="font-weight:600;">{d['project_name']}</span>{term_b}
    <span style="font-size:0.8rem;color:#737373;"> — {d.get('assignee','')}</span><br>
    <span style="font-size:0.77rem;color:#ABABAB;">{d.get('product','')} | 精度{d.get('accuracy','')}% | {d.get('hours','')}h | {d.get('building_type','')}</span>
</div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
<div style="padding:0.5rem 0;text-align:center;">
    <div style="font-size:1.3rem;font-weight:700;color:#171717;">{d.get('total_score','—')}</div>
    <div style="font-size:0.72rem;color:#ABABAB;">合計スコア</div>
</div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
<div style="padding:0.5rem 0;text-align:center;">
    <span style="background:{bg2};color:{fg2};font-size:0.78rem;padding:0.25rem 0.6rem;border-radius:4px;font-weight:600;">
        {d.get('status','—')}
    </span>
</div>""", unsafe_allow_html=True)
            with st.expander(f"削除 — {d['project_name']}"):
                if st.button("このデータを削除", key=f"del_{d['_row']}", type="secondary"):
                    gas_sheets.delete_propoint(d['_row'])
                    st.success("削除しました")
                    st.rerun()

# ====================================================
# ランキングモード
# ====================================================
else:
    st.markdown(f"### スタッフランキング — {selected_term}")

    if not pp_data:
        st.info("まだプロポイントデータがありません。「入力・編集」モードでスコアを登録してください。")
        st.stop()

    staff_scores: dict = defaultdict(list)
    for d in pp_data:
        assignee = d.get('assignee') or '不明'
        try:
            score_val = float(d.get('total_score', 0))
        except (ValueError, TypeError):
            score_val = 0.0
        staff_scores[assignee].append(score_val)

    ranking = sorted(
        [{'name': k, 'count': len(v), 'total': round(sum(v), 3), 'avg': round(sum(v) / len(v), 3)}
         for k, v in staff_scores.items()],
        key=lambda x: x['total'],
        reverse=True,
    )

    st.markdown("")
    for i, r in enumerate(ranking):
        top_cls = 'top' if i < 3 else ''
        st.markdown(f"""
<div class="ranking-row">
    <div class="rank {top_cls}">{i+1}</div>
    <div class="name">{r['name']}</div>
    <div style="font-size:0.8rem;color:#737373;">{r['count']}件</div>
    <div style="text-align:right;">
        <div class="pts">{r['total']:.3f}</div>
        <div style="font-size:0.75rem;color:#ABABAB;">平均 {r['avg']:.3f}</div>
    </div>
</div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 全件スコア一覧")
    for d in sorted(pp_data, key=lambda x: float(x.get('total_score') or 0), reverse=True):
        bg2, fg2 = pp.status_color(d.get('status', ''))
        term_b = f'<span class="term-badge">{d["term"]}</span>' if d.get('term') else ''
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:1rem;padding:0.6rem 1rem;
            background:white;border:1px solid #E8E8E8;border-radius:10px;margin-bottom:0.4rem;">
    <div style="flex:1;">
        <span style="font-weight:600;">{d['project_name']}</span>{term_b}
        <span style="font-size:0.8rem;color:#737373;margin-left:0.5rem;">{d.get('assignee','')}</span>
    </div>
    <span style="font-size:1.2rem;font-weight:700;color:#171717;">{d.get('total_score','—')}</span>
    <span style="background:{bg2};color:{fg2};font-size:0.75rem;
                 padding:0.2rem 0.6rem;border-radius:4px;font-weight:600;">
        {d.get('status','—')}
    </span>
</div>
        """, unsafe_allow_html=True)
