import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

import auth
auth.check_auth()
auth.check_owner_auth()  # 共有パスワードに加えて、本人専用の追加パスワードが必要

import style
style.apply()

import nav
nav.render()

import gas_sheets

st.set_page_config(
    page_title="タスク管理 | 設計課ポータル",
    page_icon=None,
    layout="wide",
)

st.markdown("""
<div class="app-header">
    <h1>タスク管理</h1>
    <p>自分・部下のタスクを担当者別に管理します。Claude Codeの秘書エージェントと同じデータを共有しています</p>
</div>
""", unsafe_allow_html=True)

if not gas_sheets.is_task_connected():
    st.error("タスク管理用スプレッドシートに接続できません。Secrets の TASK_SHEET_ID と、サービスアカウントへの共有設定を確認してください。")
    st.stop()


# ── 期限の切迫度判定 ─────────────────────────────────────
def _parse_due(due_str):
    s = str(due_str or '').strip()
    if not s:
        return None
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y/%m/%d %H:%M', '%m/%d', '%m-%d'):
        try:
            d = datetime.strptime(s, fmt)
            if fmt in ('%m/%d', '%m-%d'):
                d = d.replace(year=datetime.now().year)
            return d.date()
        except ValueError:
            continue
    return None


def _due_urgency(due_str):
    d = _parse_due(due_str)
    if d is None:
        return None
    delta = (d - date.today()).days
    if delta < 0:
        return 'due-overdue'
    if delta == 0:
        return 'due-today'
    if delta <= 7:
        return 'due-soon'
    return None


def _due_label(due_str):
    urgency = _due_urgency(due_str)
    text = due_str or '期限なし'
    if urgency == 'due-overdue':
        text += '（期限超過）'
    elif urgency == 'due-today':
        text += '（本日）'
    cls = urgency or ''
    return f'<span class="t-due-badge {cls}">{text}</span>'


def _sort_key(task):
    d = _parse_due(task.get('due'))
    return (d is None, d or date.max)


# ── データ取得 ───────────────────────────────────────────
open_tasks = gas_sheets.get_tasks(include_done=False)
existing_assignees = (
    gas_sheets.get_all_task_assignees() + gas_sheets.get_all_assignees()
)
existing_assignees = sorted(set(a for a in existing_assignees if a))
existing_projects = sorted(set(
    c.get('project_name', '') for c in gas_sheets.get_cases(include_done=False) if c.get('project_name')
))

n_overdue = sum(1 for t in open_tasks if _due_urgency(t.get('due')) == 'due-overdue')
n_today   = sum(1 for t in open_tasks if _due_urgency(t.get('due')) == 'due-today')
n_soon    = sum(1 for t in open_tasks if _due_urgency(t.get('due')) == 'due-soon')

# ── サマリー ─────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
<div class="metric-card {'bad' if n_overdue else ''}">
    <div class="metric-label">期限超過</div>
    <div class="metric-value">{n_overdue}</div>
</div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""
<div class="metric-card {'warn' if n_today else ''}">
    <div class="metric-label">本日期限</div>
    <div class="metric-value">{n_today}</div>
</div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">今週期限</div>
    <div class="metric-value">{n_soon}</div>
</div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">未完了タスク</div>
    <div class="metric-value">{len(open_tasks)}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="margin-bottom:0.5rem;"></div>', unsafe_allow_html=True)

tab_by_person, tab_new, tab_done = st.tabs(["  担当者別  ", "  新規追加  ", "  完了済み  "])

# ====================================================
# 担当者別タブ
# ====================================================
with tab_by_person:
    if not open_tasks:
        st.info("未完了のタスクはありません。「新規追加」タブから追加してください。")
    else:
        by_assignee = {}
        for t in open_tasks:
            by_assignee.setdefault(t.get('assignee') or '未割当', []).append(t)

        # 期限超過を含む担当者を先頭に
        def _assignee_sort_key(name):
            tasks = by_assignee[name]
            has_overdue = any(_due_urgency(t.get('due')) == 'due-overdue' for t in tasks)
            return (not has_overdue, name)

        for assignee in sorted(by_assignee.keys(), key=_assignee_sort_key):
            tasks = sorted(by_assignee[assignee], key=_sort_key)
            st.markdown(f"#### 👤 {assignee}　<span style='font-size:0.75rem;color:#ABABAB;'>{len(tasks)}件</span>", unsafe_allow_html=True)

            for t in tasks:
                row = t['_row']
                urgency = _due_urgency(t.get('due')) or ''
                proj_badge = f'<span class="term-badge">{t["project_name"]}</span>' if t.get('project_name') else ''
                st.markdown(f"""
<div class="task-card {urgency}">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
            <div class="t-content">{t.get('content','')}{proj_badge}</div>
            <div class="t-meta">{t.get('memo','') or ''}</div>
        </div>
        <div>{_due_label(t.get('due'))}</div>
    </div>
</div>""", unsafe_allow_html=True)

                c1, c2, c3 = st.columns([1, 1, 5])
                with c1:
                    if st.button("完了", key=f"done_{row}", use_container_width=True):
                        gas_sheets.complete_task(row)
                        st.rerun()
                with c2:
                    with st.popover("編集"):
                        e_assignee = st.text_input("担当者", value=t.get('assignee', ''), key=f"ea_{row}")
                        e_project  = st.text_input("案件名（物件外は空欄）", value=t.get('project_name', ''), key=f"ep_{row}")
                        e_content  = st.text_area("内容", value=t.get('content', ''), key=f"ec_{row}")
                        e_due      = st.text_input("期限（YYYY-MM-DD）", value=t.get('due', ''), key=f"ed_{row}")
                        e_memo     = st.text_input("メモ", value=t.get('memo', ''), key=f"em_{row}")
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("保存", key=f"save_{row}", type="primary", use_container_width=True):
                                gas_sheets.update_task_field(row, 'assignee', e_assignee)
                                gas_sheets.update_task_field(row, 'project_name', e_project)
                                gas_sheets.update_task_field(row, 'content', e_content)
                                gas_sheets.update_task_field(row, 'due', e_due)
                                gas_sheets.update_task_field(row, 'memo', e_memo)
                                st.rerun()
                        with b2:
                            if st.button("削除", key=f"del_{row}", use_container_width=True):
                                gas_sheets.delete_task(row)
                                st.rerun()
            st.markdown('<div style="margin-bottom:1rem;"></div>', unsafe_allow_html=True)

# ====================================================
# 新規追加タブ
# ====================================================
with tab_new:
    st.markdown("#### 新しいタスクを追加")

    c1, c2 = st.columns(2)
    with c1:
        assignee_options = existing_assignees + ['--- 新規入力 ---']
        sel_assignee = st.selectbox("担当者", assignee_options or ['--- 新規入力 ---'], key="ta_assignee_sel")
        if sel_assignee == '--- 新規入力 ---' or not assignee_options:
            n_assignee = st.text_input("担当者名を入力", value="呉", key="ta_assignee_new")
        else:
            n_assignee = sel_assignee

        project_options = ['なし（物件外の業務）'] + existing_projects + ['--- 新規入力 ---']
        sel_project = st.selectbox("案件名", project_options, key="ta_project_sel")
        if sel_project == '--- 新規入力 ---':
            n_project = st.text_input("案件名を入力", key="ta_project_new")
        elif sel_project == 'なし（物件外の業務）':
            n_project = ''
        else:
            n_project = sel_project

        n_content = st.text_area("タスク内容 *", key="ta_content")
    with c2:
        set_due = st.checkbox("期限を設定する", key="ta_set_due")
        n_due = ''
        if set_due:
            n_due = str(st.date_input("期限", key="ta_due"))
        n_memo = st.text_input("メモ", key="ta_memo")

    if st.button("追加", type="primary", key="ta_submit"):
        if not n_content:
            st.error("タスク内容は必須です")
        else:
            gas_sheets.add_task(n_assignee, n_content, due=n_due, memo=n_memo, project_name=n_project)
            st.success("タスクを追加しました")
            st.rerun()

# ====================================================
# 完了済みタブ
# ====================================================
with tab_done:
    done_tasks = gas_sheets.get_tasks(include_done=True, status='完了')
    if not done_tasks:
        st.info("完了済みのタスクはありません。")
    else:
        st.caption(f"{len(done_tasks)} 件")
        for t in sorted(done_tasks, key=lambda x: x.get('completed_at', ''), reverse=True):
            row = t['_row']
            proj_badge = f'<span class="term-badge">{t["project_name"]}</span>' if t.get('project_name') else ''
            st.markdown(f"""
<div class="task-card" style="opacity:0.65;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div class="t-content">{t.get('content','')}{proj_badge}</div>
            <div class="t-meta">担当: {t.get('assignee','—')} ｜ 完了: {t.get('completed_at','')}</div>
        </div>
        <span class="status-chip chip-ok">完了</span>
    </div>
</div>""", unsafe_allow_html=True)
            oc1, oc2 = st.columns([1, 5])
            with oc1:
                if st.button("戻す", key=f"reopen_{row}", use_container_width=True):
                    gas_sheets.reopen_task(row)
                    st.rerun()
