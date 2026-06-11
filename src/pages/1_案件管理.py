import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

import auth
auth.check_auth()

import style
style.apply()

import gas_sheets

st.set_page_config(
    page_title="案件管理 | 設計課ポータル",
    page_icon=None,
    layout="wide",
)

st.markdown("""
<div class="app-header">
    <h1>案件管理</h1>
    <p>物件の進捗・打合せ日程・担当者を期ごとに管理します</p>
</div>
""", unsafe_allow_html=True)

if not gas_sheets.is_connected():
    st.error("スプレッドシートに接続できません。Secrets の BPM_SHEET_ID と gcp_service_account を確認してください。")
    st.stop()

# ── 定数 ─────────────────────────────────────────────────
PRODUCT_OPTIONS = ['ORDER', 'SELECT', 'COCOQUMI', 'COCOCHIE']
MEETING_COUNTS  = {'ORDER': 7, 'SELECT': 5, 'COCOQUMI': 5, 'COCOCHIE': 2}
STATUS_CHIP = {
    '完了': 'chip-ok', '実行中': 'chip-running',
    '要確認': 'chip-warn', 'エラー': 'chip-error',
}


def _pip_html(dates: list, n: int) -> str:
    pips = []
    for i in range(n):
        filled = bool(dates[i]) if i < len(dates) else False
        cls = 'pip-done' if filled else 'pip-empty'
        pips.append(f'<span class="progress-pip {cls}">{i+1}</span>')
    return ''.join(pips)


def _status_html(status: str) -> str:
    cls = STATUS_CHIP.get(status, 'chip-none')
    return f'<span class="status-chip {cls}">{status or "未実行"}</span>'


def _meet_dates(case: dict) -> list:
    return [case.get(f'meet{i}', '') for i in range(1, 8)]


def _n_meets(case: dict) -> int:
    return MEETING_COUNTS.get(case.get('product', ''), 5)


# ── サイドバー ────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 案件管理")
    st.markdown("---")

    terms = gas_sheets.get_all_terms()
    if not terms:
        terms = []

    term_options  = ['すべて'] + terms
    selected_term = st.selectbox("表示する期", term_options, index=0)

    st.markdown("---")
    st.markdown("**新しい期を追加**")
    new_term_input = st.text_input("期名", placeholder="例: 2026年度上期", label_visibility="collapsed")
    if st.button("追加", use_container_width=True) and new_term_input:
        st.session_state['_pending_term'] = new_term_input
        st.success(f"「{new_term_input}」を登録しました。新規物件追加時に選択できます。")

term_filter = None if selected_term == 'すべて' else selected_term

# ── タブ ─────────────────────────────────────────────────
tab_active, tab_done, tab_new = st.tabs(["  進行中  ", "  完了  ", "  新規追加  "])

# ====================================================
# 進行中タブ
# ====================================================
with tab_active:
    cases = gas_sheets.get_cases(term=term_filter, include_done=False)

    if not cases:
        msg = "進行中の物件がありません。"
        if term_filter:
            msg += " 別の期を選択するか「新規追加」タブから追加してください。"
        else:
            msg += " 「新規追加」タブから物件を追加してください。"
        st.info(msg)
    else:
        st.caption(f"{len(cases)} 件")

    for case in cases:
        dates  = _meet_dates(case)
        n      = _n_meets(case)
        pips   = _pip_html(dates, n)
        stat   = _status_html(case.get('status', ''))
        term_b = f'<span class="term-badge">{case["term"]}</span>' if case.get('term') else ''
        prod_b = (f'<span class="term-badge" style="margin-left:0.3rem;background:#0A0A0A;'
                  f'color:white;border-color:#0A0A0A;">{case["product"]}</span>'
                  if case.get('product') else '')

        with st.container():
            st.markdown(f"""
<div class="project-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
            <div class="pname">{case['project_name']}{term_b}{prod_b}</div>
            <div class="passign">担当: {case.get('assignee','—')}{f" &nbsp;|&nbsp; {case.get('customer_name','')}" if case.get('customer_name') else ''}</div>
        </div>
        <div style="text-align:right;">{stat}</div>
    </div>
    <div style="margin-top:0.7rem;">{pips}</div>
</div>
""", unsafe_allow_html=True)

            with st.expander("詳細・編集"):
                row = case['_row']
                c1, c2 = st.columns(2)

                with c1:
                    with st.form(key=f"edit_{row}"):
                        st.markdown("**基本情報**")
                        new_pname  = st.text_input("物件名",  value=case.get('project_name', ''))
                        new_assign = st.text_input("担当者",  value=case.get('assignee', ''))
                        new_cid    = st.text_input("顧客ID",  value=case.get('customer_id', ''))
                        new_cname  = st.text_input("顧客名",  value=case.get('customer_name', ''))
                        prod_idx   = PRODUCT_OPTIONS.index(case['product']) if case.get('product') in PRODUCT_OPTIONS else 0
                        new_prod   = st.selectbox("商品種別", PRODUCT_OPTIONS, index=prod_idx)
                        term_choices = terms if terms else ['期未設定']
                        t_idx = term_choices.index(case['term']) if case.get('term') in term_choices else 0
                        new_term_v = st.selectbox("期名", term_choices, index=t_idx)
                        if st.form_submit_button("保存", use_container_width=True):
                            updated = dict(case)
                            updated.update({
                                'project_name': new_pname, 'assignee': new_assign,
                                'customer_id': new_cid, 'customer_name': new_cname,
                                'product': new_prod, 'term': new_term_v,
                            })
                            gas_sheets.save_case(updated, row_number=row)
                            st.success("保存しました")
                            st.rerun()

                with c2:
                    with st.form(key=f"dates_{row}"):
                        st.markdown("**打合せ日程**")
                        d = _meet_dates(case)
                        n_edit = MEETING_COUNTS.get(case.get('product', ''), 5)
                        new_meets = {}
                        for i in range(1, n_edit + 1):
                            val = str(d[i-1]) if i <= len(d) and d[i-1] else ''
                            new_meets[i] = st.text_input(f"第{i}回", value=val)
                        if st.form_submit_button("日程保存", use_container_width=True):
                            updated = dict(case)
                            for i in range(1, 8):
                                updated[f'meet{i}'] = new_meets.get(i, '')
                            gas_sheets.save_case(updated, row_number=row)
                            st.success("保存しました")
                            st.rerun()

                st.markdown("")
                act_c1, act_c2 = st.columns(2)
                with act_c1:
                    if selected_term != 'すべて' and len(terms) > 1:
                        move_target = st.selectbox(
                            "別の期へ移動",
                            [t for t in terms if t != case.get('term')],
                            key=f"mv_{row}",
                        )
                        if st.button("期を移動", key=f"mvbtn_{row}", use_container_width=True):
                            gas_sheets.move_case_term(row, move_target)
                            st.success(f"「{move_target}」に移動しました")
                            st.rerun()
                with act_c2:
                    st.markdown("")
                    if st.button("完了にする", key=f"done_{row}", type="primary", use_container_width=True):
                        gas_sheets.mark_case_done(row, done=True)
                        st.success("完了にしました")
                        st.rerun()

# ====================================================
# 完了タブ
# ====================================================
with tab_done:
    done_cases = gas_sheets.get_cases(term=term_filter, include_done=True)

    if not done_cases:
        st.info("完了物件はありません。")
    else:
        st.caption(f"{len(done_cases)} 件")
        for case in done_cases:
            row    = case['_row']
            term_b = f'<span class="term-badge">{case["term"]}</span>' if case.get('term') else ''
            prod_b = (f'<span class="term-badge" style="margin-left:0.3rem;background:#0A0A0A;'
                      f'color:white;border-color:#0A0A0A;">{case["product"]}</span>'
                      if case.get('product') else '')
            st.markdown(f"""
<div class="project-card" style="opacity:0.7;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div class="pname">{case['project_name']}{term_b}{prod_b}</div>
            <div class="passign">担当: {case.get('assignee','—')}</div>
        </div>
        <span class="status-chip chip-ok">完了</span>
    </div>
</div>
""", unsafe_allow_html=True)
            with st.expander("進行中に戻す"):
                if st.button("進行中に戻す", key=f"undone_{row}", use_container_width=True):
                    gas_sheets.mark_case_done(row, done=False)
                    st.success("進行中に戻しました")
                    st.rerun()

# ====================================================
# 新規追加タブ
# ====================================================
with tab_new:
    st.markdown("#### 新しい物件を追加")
    st.caption("商品種別を選択すると、必要な打合せ回数が自動で設定されます。")

    c1, c2 = st.columns(2)
    with c1:
        a_pname   = st.text_input("物件名 *", key="na_pname")
        a_assign  = st.text_input("担当者 *", key="na_assign")
        a_cid     = st.text_input("顧客ID（BPM）", key="na_cid")
        a_cname   = st.text_input("顧客名", key="na_cname")
        a_term    = st.selectbox("期名", terms if terms else ['期未設定'], key="na_term")
    with c2:
        a_product = st.selectbox(
            "商品種別",
            PRODUCT_OPTIONS,
            key="na_product",
            help="ORDER:7回 / SELECT・COCOQUMI:5回 / COCOCHIE:2回",
        )
        n_new = MEETING_COUNTS.get(a_product, 5)
        st.caption(f"打合せ {n_new} 回分の日程を入力してください")
        a_meets = {}
        for i in range(1, n_new + 1):
            a_meets[i] = st.text_input(f"第{i}回打合せ日", placeholder="YYYY-MM-DD", key=f"na_meet{i}")

    st.markdown("")
    if st.button("追加", type="primary", key="na_submit"):
        if not a_pname or not a_assign:
            st.error("物件名と担当者は必須です")
        else:
            save_data = {
                'project_name': a_pname, 'assignee': a_assign,
                'customer_id': a_cid, 'customer_name': a_cname,
                'term': a_term, 'product': a_product,
                'status': '', 'run_at': '', 'done': '',
            }
            for i in range(1, 8):
                save_data[f'meet{i}'] = a_meets.get(i, '')
            gas_sheets.save_case(save_data)
            st.success(f"「{a_pname}」を追加しました")
            st.rerun()
