import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from datetime import date

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_client(credentials_path: str) -> gspread.Client:
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return gspread.authorize(creds)


def write_estimate(
    spreadsheet_url: str,
    credentials_path: str,
    items: list[dict],
    project_name: str,
    sheet_name: str = "積算",
) -> dict:
    """
    積算データをGoogleスプレッドシートに転記する。
    シート「積算」が存在しない場合は新規作成。
    既存データは上書き（A1から）。
    """
    gc = get_client(credentials_path)
    ss = gc.open_by_url(spreadsheet_url)

    try:
        ws = ss.worksheet(sheet_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=sheet_name, rows=300, cols=10)

    total = sum(i["金額"] for i in items)
    tax = int(total * 0.1)

    rows = []
    rows.append(["物件名", project_name, "", "", "作成日", date.today().isoformat()])
    rows.append([])
    rows.append(["工種", "品目", "数量", "単位", "単価（円）", "金額（円）"])

    for item in items:
        rows.append([
            item["工種"],
            item["品目"],
            item["数量"],
            item["単位"],
            item["単価"],
            item["金額"],
        ])

    rows.append([])
    rows.append(["", "", "", "", "合計（税抜）", total])
    rows.append(["", "", "", "", "消費税（10%）", tax])
    rows.append(["", "", "", "", "税込合計", total + tax])

    ws.update("A1", rows)

    # 数値列を右揃え・数値フォーマット（gspreadのformat_cellsで設定）
    last_data_row = 3 + len(items)
    ws.format(f"C3:C{last_data_row}", {"horizontalAlignment": "RIGHT"})
    ws.format(f"E3:F{last_data_row + 4}", {
        "numberFormat": {"type": "NUMBER", "pattern": "#,##0"},
        "horizontalAlignment": "RIGHT",
    })

    return {
        "url": ss.url,
        "sheet_name": sheet_name,
        "rows_written": len(rows),
    }


def validate_credentials(credentials_path: str) -> bool:
    try:
        Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        return True
    except Exception:
        return False
