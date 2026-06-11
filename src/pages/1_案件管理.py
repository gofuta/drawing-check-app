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

import nav
nav.render()

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


# ── 期フィルター（ページ上部） ────────────────────────────
terms = gas_sheets.get_all_terms() or []
_fc1, _fc2, _fc3, _fc_sp = st.columns([1.8, 2.2, 1.1, 4.9])
with _fc1:
    selected_term = st.selectbox("表示する期", ['すべて'] + terms)
with _fc2:
    _new_term_input = st.text_input("新しい期名を追加", placeholder="例: 2026年度上期")
with _fc3:
    st.markdown('<div style="margin-top:1.72rem;"></div>', unsafe_allow_html=True)
    if st.button("追加", use_container_width=True) and _new_term_input:
        st.session_state['_pending_term'] = _new_term_input
        st.success(f"「{_new_term_input}」を登録しました。")

term_filter = None if selected_term == 'すべて' else selected_term

# 担当者一覧はループ外で1回だけ取得
existing_assignees = gas_sheets.get_all_assignees()

# ── タブ ─────────────────────────────────────────────────
tab_active, tab_done, tab_new, tab_schedule = st.tabs([
    "  進行中  ", "  完了  ", "  新規追加  ", "  スケジュール  "
])

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
        prod_b = (f'<span class="term-badge" style="margin-left:0.3rem;background:#171717;'
                  f'color:white;border-color:#171717;">{case["product"]}</span>'
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
                        new_pname  = st.text_input("物件名",  value=case.get('project_name', ''), key=f"ep_{row}")
                        assignee_opts = existing_assignees + ['--- 新規入力 ---']
                        cur_idx = assignee_opts.index(case.get('assignee', '')) if case.get('assignee') in existing_assignees else 0
                        sel_a = st.selectbox("担当者", assignee_opts, index=cur_idx, key=f"eas_{row}")
                        if sel_a == '--- 新規入力 ---':
                            new_assign = st.text_input("担当者名を入力", key=f"ea_{row}")
                        else:
                            new_assign = sel_a
                        new_cid    = st.text_input("顧客ID",  value=case.get('customer_id', ''), key=f"ec_{row}")
                        new_cname  = st.text_input("顧客名",  value=case.get('customer_name', ''), key=f"en_{row}")
                        prod_idx   = PRODUCT_OPTIONS.index(case['product']) if case.get('product') in PRODUCT_OPTIONS else 0
                        new_prod   = st.selectbox("商品種別", PRODUCT_OPTIONS, index=prod_idx, key=f"epr_{row}")
                        term_choices = terms if terms else ['期未設定']
                        t_idx = term_choices.index(case['term']) if case.get('term') in term_choices else 0
                        new_term_v = st.selectbox("期名", term_choices, index=t_idx, key=f"et_{row}")
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
                            new_meets[i] = st.text_input(f"第{i}回", value=val, key=f"dm{i}_{row}")
                        if st.form_submit_button("日程保存", use_container_width=True):
                            updated = dict(case)
                            for i in range(1, 8):
                                updated[f'meet{i}'] = new_meets.get(i, '')
                            gas_sheets.save_case(updated, row_number=row)
                            st.success("保存しました")
                            st.rerun()

                st.markdown("")
                act_c1, act_c2, act_c3 = st.columns(3)
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
                with act_c3:
                    st.markdown("")
                    if st.button("削除", key=f"delact_{row}", use_container_width=True):
                        if st.session_state.get(f"confirm_del_{row}"):
                            gas_sheets.delete_case(row)
                            st.success("削除しました")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_del_{row}"] = True
                            st.warning("もう一度「削除」を押すと削除されます")

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
            prod_b = (f'<span class="term-badge" style="margin-left:0.3rem;background:#171717;'
                      f'color:white;border-color:#171717;">{case["product"]}</span>'
                      if case.get('product') else '')
            st.markdown(f"""
<div class="project-card" style="opacity:0.65;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div class="pname">{case['project_name']}{term_b}{prod_b}</div>
            <div class="passign">担当: {case.get('assignee','—')}</div>
        </div>
        <span class="status-chip chip-ok">完了</span>
    </div>
</div>
""", unsafe_allow_html=True)
            with st.expander("操作"):
                op_c1, op_c2 = st.columns(2)
                with op_c1:
                    if st.button("進行中に戻す", key=f"undone_{row}", use_container_width=True):
                        gas_sheets.mark_case_done(row, done=False)
                        st.success("進行中に戻しました")
                        st.rerun()
                with op_c2:
                    if st.button("削除", key=f"deldone_{row}", use_container_width=True):
                        if st.session_state.get(f"confirm_del_done_{row}"):
                            gas_sheets.delete_case(row)
                            st.success("削除しました")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_del_done_{row}"] = True
                            st.warning("もう一度「削除」を押すと完全に削除されます")

# ====================================================
# 新規追加タブ
# ====================================================
with tab_new:
    st.markdown("#### 新しい物件を追加")
    st.caption("商品種別を選択すると、必要な打合せ回数が自動で設定されます。")

    c1, c2 = st.columns(2)
    with c1:
        a_pname = st.text_input("物件名 *", key="na_pname")

        assignee_options = existing_assignees + ['--- 新規入力 ---']
        sel_assignee = st.selectbox("担当者 *", assignee_options, key="na_assignee_sel")
        if sel_assignee == '--- 新規入力 ---':
            a_assign = st.text_input("担当者名を入力", key="na_assign_new", placeholder="氏名を入力")
        else:
            a_assign = sel_assignee

        a_cid   = st.text_input("顧客ID（BPM）", key="na_cid")
        a_cname = st.text_input("顧客名", key="na_cname")
        a_term  = st.selectbox("期名", terms if terms else ['期未設定'], key="na_term")

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

# ====================================================
# スケジュールタブ
# ====================================================
with tab_schedule:
    try:
        import plotly.express as px
        import pandas as pd

        st.markdown("#### 打合せスケジュール")
        st.caption("各担当者の打合せ日程を月別に表示します。日程が入力されている物件のみ表示されます。")

        all_cases_sch = (
            gas_sheets.get_cases(term=term_filter, include_done=False)
            + gas_sheets.get_cases(term=term_filter, include_done=True)
        )

        events = []
        for case in all_cases_sch:
            n = _n_meets(case)
            for i in range(1, n + 1):
                date_str = case.get(f'meet{i}', '')
                if date_str and str(date_str).strip():
                    try:
                        d = pd.to_datetime(str(date_str).strip())
                        events.append({
                            '担当者': case.get('assignee') or '未割当',
                            '物件名': case.get('project_name', '—'),
                            '打合せ': f'第{i}回',
                            '開始日': d,
                            '終了日': d + pd.Timedelta(days=3),
                        })
                    except Exception:
                        pass

        if not events:
            st.info("打合せ日程が登録されていません。案件に日程を入力するとここに表示されます。")
        else:
            df_g = pd.DataFrame(events)
            n_staff = df_g['担当者'].nunique()

            fig = px.timeline(
                df_g,
                x_start='開始日',
                x_end='終了日',
                y='担当者',
                color='物件名',
                text='打合せ',
                hover_data={'物件名': True, '打合せ': True},
            )
            fig.update_traces(
                textposition='inside',
                textfont=dict(size=10, family='Inter, Noto Sans JP, sans-serif'),
                marker_line_width=0,
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Inter, Noto Sans JP, sans-serif', size=12, color='#171717'),
                height=max(280, n_staff * 60 + 120),
                xaxis_title='',
                yaxis_title='',
                margin=dict(l=10, r=20, t=50, b=40),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='left',
                    x=0,
                    font=dict(size=11),
                ),
                xaxis=dict(
                    tickformat='%Y/%m',
                    dtick='M1',
                    showgrid=True,
                    gridcolor='#F0F0F0',
                    tickfont=dict(size=11),
                ),
                yaxis=dict(showgrid=False, tickfont=dict(size=12)),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.markdown("**月別 打合せ件数**")
            df_g['月'] = df_g['開始日'].dt.strftime('%Y/%m')
            summary = (
                df_g.groupby(['月', '担当者'])
                .size()
                .reset_index(name='件数')
                .pivot(index='担当者', columns='月', values='件数')
                .fillna(0)
                .astype(int)
            )
            st.dataframe(summary, use_container_width=True)

    except ImportError:
        st.warning("グラフ表示には plotly が必要です。requirements.txt に plotly>=5.18.0 を追加してください。")
    except Exception as e:
        st.error(f"スケジュール表示でエラーが発生しました: {e}")
