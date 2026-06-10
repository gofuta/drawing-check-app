import streamlit as st
import sys
import os
from pathlib import Path
import io
import fitz  # pymupdf
from PIL import Image
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent))

import auth
auth.check_auth()

import checker
import estimator
import sheets_exporter
import history
import demo_data

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _get_secret(key: str, default: str = "") -> str:
    val = os.getenv(key, "")
    if val:
        return val
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


# サーバー側で設定された値（.env または Streamlit Secrets から）
ENV_API_KEY = _get_secret("ANTHROPIC_API_KEY")
ENV_CREDS_FILE = _get_secret("GOOGLE_CREDENTIALS_FILE")
ENV_SHEET_URL = _get_secret("GOOGLE_SPREADSHEET_URL")

st.set_page_config(
    page_title="図面チェック・自動見積積算",
    page_icon="📐",
    layout="wide",
)

st.title("📐 図面チェック・自動見積積算システム")
st.caption("建築図面をアップロードするとAIが自動でチェックと積算を行います")

# ── サイドバー ────────────────────────────────────────
with st.sidebar:
    st.header("設定")

    # APIキーはサーバー設定済みの場合は非表示
    if ENV_API_KEY:
        api_key = ENV_API_KEY
        st.success("✅ APIキー設定済み（サーバー）")
    else:
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="環境変数 ANTHROPIC_API_KEY でも設定可能",
        )

    project_name = st.text_input("物件名", value="物件名未設定")

    st.divider()
    st.subheader("📊 Googleスプレッドシート")

    # スプレッドシートURL
    if ENV_SHEET_URL:
        sheet_url = ENV_SHEET_URL
        st.success("✅ スプレッドシートURL設定済み")
    else:
        sheet_url = st.text_input(
            "スプレッドシートURL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="転記先のGoogleスプレッドシートURL",
        )

    sheet_name = st.text_input("シート名", value="積算", help="データを書き込むシート名")

    # サービスアカウント認証ファイル
    if ENV_CREDS_FILE and Path(ENV_CREDS_FILE).exists():
        credentials_path = ENV_CREDS_FILE
        st.success("✅ Google認証設定済み")
    else:
        creds_file = st.file_uploader(
            "サービスアカウントJSON",
            type=["json"],
            help="Google Cloud サービスアカウントのJSONキーファイル",
        )
        if creds_file:
            creds_save_path = OUTPUT_DIR / "service_account_tmp.json"
            creds_save_path.write_bytes(creds_file.read())
            credentials_path = str(creds_save_path)
        else:
            credentials_path = ""

    st.divider()
    st.info("対応形式: PDF / PNG / JPG")

    st.divider()
    if st.button("🎮 デモモードで試す", use_container_width=True):
        st.session_state["result"] = demo_data.get_demo_result()
        st.session_state["project_name"] = "デモ物件"
        st.rerun()

# ── メインエリア ──────────────────────────────────────
uploaded = st.file_uploader(
    "図面ファイルをアップロード",
    type=["pdf", "png", "jpg", "jpeg"],
    label_visibility="collapsed",
)

if uploaded is None:
    st.info("図面ファイルをアップロードしてください")
    st.stop()

# ファイル読み込みと画像化
file_bytes = uploaded.read()
media_type = "image/png"

if uploaded.type == "application/pdf":
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page = doc[0]
    mat = fitz.Matrix(2, 2)  # 2倍解像度
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    media_type = "image/png"
else:
    img_bytes = file_bytes
    media_type = uploaded.type

# プレビュー
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("アップロード図面")
    st.image(img_bytes, use_container_width=True)

with col2:
    if not api_key:
        st.error("APIキーを入力してください（サイドバー）")
        st.stop()

    if st.button("チェック・積算を実行", type="primary", use_container_width=True):
        with st.spinner("AIが図面を解析中...（30秒〜1分程度）"):
            try:
                result = checker.check_drawing(img_bytes, media_type, api_key)
                st.session_state["result"] = result
                st.session_state["project_name"] = project_name
                history.save_history(project_name, result)
            except Exception as e:
                st.error(f"解析エラー: {e}")
                st.stop()

if "result" not in st.session_state:
    st.stop()

result = st.session_state["result"]
pname = st.session_state.get("project_name", "物件名未設定")

# ── タブ表示 ──────────────────────────────────────────
tab_check, tab_estimate = st.tabs(["📋 図面チェック結果", "💴 自動積算"])

# ── チェック結果タブ ──────────────────────────────────
with tab_check:
    drawing_type = result.get("drawing_type", "不明")
    score = result.get("overall_score", 0)
    summary = result.get("summary", "")

    c1, c2, c3 = st.columns(3)
    c1.metric("図面種別", drawing_type)
    c2.metric("完成度スコア", f"{score} / 100")
    items = result.get("check_items", [])
    ng_count = sum(1 for i in items if i["status"] == "NG")
    c3.metric("NG件数", f"{ng_count} 件")

    st.subheader("総合所見")
    st.info(summary)

    st.subheader("チェック明細")

    status_icon = {"OK": "✅", "NG": "❌", "要確認": "⚠️"}
    severity_color = {"高": "🔴", "中": "🟡", "低": "🟢"}

    for item in items:
        icon = status_icon.get(item["status"], "❓")
        sev = severity_color.get(item.get("severity", "低"), "")
        label = f"{icon} {sev} [{item['category']}] {item['item']}"
        with st.expander(label, expanded=(item["status"] == "NG")):
            st.write(f"**ステータス**: {item['status']}")
            st.write(f"**重大度**: {item.get('severity', '-')}")
            st.write(f"**コメント**: {item.get('comment', '-')}")

# ── 積算タブ ──────────────────────────────────────────
with tab_estimate:
    quantities = result.get("quantities", {})

    st.subheader("抽出数量")
    q_cols = st.columns(3)
    q_items = [
        ("延床面積", quantities.get("floor_area"), "m²"),
        ("建築面積", quantities.get("building_area"), "m²"),
        ("階数", quantities.get("stories"), "階"),
        ("窓数", quantities.get("window_count"), "箇所"),
        ("ドア数", quantities.get("door_count"), "箇所"),
        ("外壁周長", quantities.get("outer_wall_length"), "m"),
    ]
    for idx, (label, val, unit) in enumerate(q_items):
        with q_cols[idx % 3]:
            display = f"{val} {unit}" if val is not None else "読取不可"
            st.metric(label, display)

    st.divider()

    estimate_items = estimator.estimate_from_quantities(quantities)

    if not estimate_items:
        st.warning("数量情報が不足しているため積算できません。面積・開口数が読み取れる図面をアップロードしてください。")
        st.stop()

    st.subheader("積算明細")
    import pandas as pd
    df = pd.DataFrame(estimate_items)
    df_display = df.copy()
    df_display["金額"] = df_display["金額"].map("{:,}".format)
    df_display["単価"] = df_display["単価"].map("{:,}".format)
    st.dataframe(df_display[["工種", "品目", "数量", "単位", "単価", "金額"]], use_container_width=True)

    total = sum(i["金額"] for i in estimate_items)
    st.metric("合計（税抜）", f"¥{total:,}", help="単価マスターに基づく概算金額です")
    st.metric("消費税（10%）", f"¥{int(total * 0.1):,}")
    st.metric("税込合計", f"¥{int(total * 1.1):,}")

    st.divider()

    # ── 出力ボタン ────────────────────────────────────
    out_col1, out_col2 = st.columns(2)

    with out_col1:
        st.markdown("**📊 Googleスプレッドシートに転記**")
        if not sheet_url:
            st.warning("サイドバーでスプレッドシートURLを設定してください")
        elif not credentials_path:
            st.warning("サイドバーでサービスアカウントJSONを設定してください")
        else:
            if st.button("スプレッドシートに転記", type="primary", use_container_width=True):
                with st.spinner("Googleスプレッドシートに転記中..."):
                    try:
                        res = sheets_exporter.write_estimate(
                            spreadsheet_url=sheet_url,
                            credentials_path=credentials_path,
                            items=estimate_items,
                            project_name=pname,
                            sheet_name=sheet_name,
                        )
                        st.success(f"転記完了！")
                        st.markdown(f"[スプレッドシートを開く]({res['url']})")
                    except Exception as e:
                        st.error(f"転記エラー: {e}")

    with out_col2:
        st.markdown("**📥 Excelバックアップ**")
        if st.button("Excel見積書を出力", use_container_width=True):
            output_path = OUTPUT_DIR / f"見積書_{pname}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            estimator.export_excel(estimate_items, output_path, pname)
            with open(output_path, "rb") as f:
                st.download_button(
                    label="ダウンロード",
                    data=f.read(),
                    file_name=output_path.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
