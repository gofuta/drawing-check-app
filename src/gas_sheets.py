"""Google Sheets操作モジュール — BPM自動化スプレッドシート"""

import os
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
]

# ==================== 案件管理シート 列定義 ====================
# A(0):物件名 B(1):顧客ID C(2):顧客名 D(3):担当者
# E(4):第1回 F(5):第2回 G(6):第3回 H(7):第4回 I(8):第5回
# J(9):ステータス K(10):実行日時 L(11):期名 M(12):完了フラグ
# N(13):商品種別 O(14):第6回 P(15):第7回
CASE_COLS = {
    'project_name': 0, 'customer_id': 1, 'customer_name': 2, 'assignee': 3,
    'meet1': 4, 'meet2': 5, 'meet3': 6, 'meet4': 7, 'meet5': 8,
    'status': 9, 'run_at': 10, 'term': 11, 'done': 12,
    'product': 13, 'meet6': 14, 'meet7': 15,
}
CASE_HEADER = ['物件名', '顧客ID', '顧客名', '担当者',
               '第1回', '第2回', '第3回', '第4回', '第5回',
               'ステータス', '実行日時', '期名', '完了',
               '商品種別', '第6回', '第7回']

# ==================== プロポイントシート 列定義 ====================
# A:物件名 B:担当者 C:期名 D:商品種別 E:精度% F:工数h G:建物種別
# H:商品Pt I:精度Pt J:工数Pt K:合計スコア L:STATUS M:登録日時
PP_COLS = {
    'project_name': 0, 'assignee': 1, 'term': 2,
    'product': 3, 'accuracy': 4, 'hours': 5, 'building_type': 6,
    'product_pt': 7, 'accuracy_pt': 8, 'workload_pt': 9,
    'total_score': 10, 'status': 11, 'registered_at': 12,
}
PP_HEADER = ['物件名', '担当者', '期名', '商品種別', '精度%', '工数h', '建物種別',
             '商品Pt', '精度Pt', '工数Pt', '合計スコア', 'STATUS', '登録日時']

CASE_SHEET_NAME = '案件管理'
PP_SHEET_NAME   = 'プロポイント'


@st.cache_resource(show_spinner=False)
def _get_client() -> gspread.Client | None:
    # Streamlit Cloud: st.secrets["gcp_service_account"] を優先
    try:
        info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(info, scopes=_SCOPES)
        return gspread.authorize(creds)
    except Exception:
        pass
    # ローカル: 環境変数のファイルパス
    cred_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
    if cred_file and os.path.exists(cred_file):
        creds = Credentials.from_service_account_file(cred_file, scopes=_SCOPES)
        return gspread.authorize(creds)
    return None


@st.cache_resource(show_spinner=False)
def _get_spreadsheet() -> gspread.Spreadsheet | None:
    client = _get_client()
    if client is None:
        return None
    try:
        sheet_id = os.getenv('BPM_SHEET_ID') or st.secrets.get('BPM_SHEET_ID', '')
    except Exception:
        sheet_id = os.getenv('BPM_SHEET_ID', '')
    if not sheet_id:
        return None
    try:
        return client.open_by_key(sheet_id)
    except Exception:
        return None


def is_connected() -> bool:
    return _get_spreadsheet() is not None


def _ensure_sheet(name: str, header: list) -> gspread.Worksheet | None:
    ss = _get_spreadsheet()
    if ss is None:
        return None
    try:
        ws = ss.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=name, rows=500, cols=len(header))
        ws.append_row(header)
    return ws


def _rows_to_dicts(rows: list[list], col_map: dict) -> list[dict]:
    result = []
    for idx, row in enumerate(rows):
        # 短い行をパディング
        row = list(row) + [''] * (max(col_map.values()) + 1 - len(row))
        d = {k: row[v] for k, v in col_map.items()}
        d['_row'] = idx + 2  # スプレッドシートの行番号（1-indexed, ヘッダー込み）
        result.append(d)
    return result


# ==================== 案件管理 ====================

def get_cases(term: str | None = None, include_done: bool = False) -> list[dict]:
    ws = _ensure_sheet(CASE_SHEET_NAME, CASE_HEADER)
    if ws is None:
        return []
    all_rows = ws.get_all_values()
    if len(all_rows) <= 1:
        return []
    data = _rows_to_dicts(all_rows[1:], CASE_COLS)
    if not include_done:
        data = [d for d in data if str(d.get('done', '')).strip() not in ('完了', '1', 'TRUE', 'true')]
    else:
        data = [d for d in data if str(d.get('done', '')).strip() in ('完了', '1', 'TRUE', 'true')]
    if term:
        data = [d for d in data if d.get('term', '') == term]
    return data


def get_all_terms() -> list[str]:
    ws = _ensure_sheet(CASE_SHEET_NAME, CASE_HEADER)
    if ws is None:
        return []
    all_rows = ws.get_all_values()
    if len(all_rows) <= 1:
        return []
    terms = []
    for row in all_rows[1:]:
        row = list(row) + [''] * (16 - len(row))
        t = str(row[CASE_COLS['term']]).strip()
        if t and t not in terms:
            terms.append(t)
    return terms


def save_case(data: dict, row_number: int | None = None):
    ws = _ensure_sheet(CASE_SHEET_NAME, CASE_HEADER)
    if ws is None:
        return
    row = [''] * len(CASE_HEADER)
    for k, idx in CASE_COLS.items():
        row[idx] = data.get(k, '')
    if row_number:
        ws.update(f'A{row_number}', [row])
    else:
        ws.append_row(row)


def update_case_field(row_number: int, field: str, value):
    ws = _ensure_sheet(CASE_SHEET_NAME, CASE_HEADER)
    if ws is None:
        return
    col_idx = CASE_COLS.get(field)
    if col_idx is None:
        return
    col_letter = chr(ord('A') + col_idx)
    ws.update(f'{col_letter}{row_number}', [[value]])


def mark_case_done(row_number: int, done: bool = True):
    update_case_field(row_number, 'done', '完了' if done else '')


def move_case_term(row_number: int, new_term: str):
    update_case_field(row_number, 'term', new_term)


# ==================== プロポイント ====================

def get_propoints(term: str | None = None) -> list[dict]:
    ws = _ensure_sheet(PP_SHEET_NAME, PP_HEADER)
    if ws is None:
        return []
    all_rows = ws.get_all_values()
    if len(all_rows) <= 1:
        return []
    data = _rows_to_dicts(all_rows[1:], PP_COLS)
    if term:
        data = [d for d in data if d.get('term', '') == term]
    return data


def save_propoint(data: dict, row_number: int | None = None):
    ws = _ensure_sheet(PP_SHEET_NAME, PP_HEADER)
    if ws is None:
        return
    if not data.get('registered_at'):
        data['registered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    row = [''] * len(PP_HEADER)
    for k, idx in PP_COLS.items():
        row[idx] = data.get(k, '')
    if row_number:
        ws.update(f'A{row_number}', [row])
    else:
        ws.append_row(row)


def delete_propoint(row_number: int):
    ws = _ensure_sheet(PP_SHEET_NAME, PP_HEADER)
    if ws is None:
        return
    ws.delete_rows(row_number)
