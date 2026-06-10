# 図面チェック・自動見積積算システム

建築図面をアップロードするだけでAIがチェックと積算を自動実行するWebアプリ。

## セットアップ

```powershell
pip install -r requirements.txt
copy .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

## 使い方

```powershell
streamlit run src/app.py
```

ブラウザが開いたら図面ファイル（PDF/PNG/JPG）をアップロードして実行。

## ドキュメント

- `docs\PROJECT_SUMMARY.md` — プロジェクト全体概要
- `.claude\CLAUDE.md` — Claude Code 用のプロジェクト固有ルール
