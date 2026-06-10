# CLAUDE.md

## プロジェクト概要
- **目的**: 建築図面のAIチェックと自動見積積算
- **GitHub**: ローカルのみ
- **詳細**: `docs/PROJECT_SUMMARY.md` を参照

## 技術スタック
- **言語**: Python 3.11+
- **主なライブラリ**: streamlit, anthropic, pymupdf, openpyxl, pandas, gspread, google-auth
- **DB**: なし（CSVファイルで単価マスター管理）
- **デプロイ先**: 社内サーバー共有運用（全員がブラウザからアクセス）

## ディレクトリ構成
- `src/` — ソースコード（app.py / checker.py / estimator.py / sheets_exporter.py / price_master.py）
- `data/` — 単価マスターCSV
- `credentials/` — Googleサービスアカウント JSON（Git管理外）
- `output/` — 生成された見積書Excel（Git管理外）
- `docs/` — プロジェクトドキュメント（GOOGLE_SHEETS_SETUP.md含む）
- `logs/` — 作業ログ（Git管理外）

## 開発コマンド
- セットアップ: `pip install -r requirements.txt`
- 起動: `streamlit run src/app.py`

## Claude API利用方針
- モデル: `claude-opus-4-8`（図面解析の精度優先）
- APIキー: 環境変数 `ANTHROPIC_API_KEY` で管理
- 画像はbase64エンコードして送信

## セキュリティ
- 認証情報は環境変数で管理
- `.env` はGit管理外、Claude からの読み取り禁止
- `output/` もGit管理外（顧客データ保護）
