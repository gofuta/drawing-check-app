# Google スプレッドシート連携 セットアップ手順

## 必要なもの
- Googleアカウント（会社のGoogleアカウント推奨）
- Google Cloud Console へのアクセス

---

## 手順1：Google Cloud でサービスアカウントを作成

1. [Google Cloud Console](https://console.cloud.google.com/) を開く
2. 左上のプロジェクト選択 → 「新しいプロジェクト」で作成（例: `kaedekoumuten-estimate`）
3. 左メニュー → 「APIとサービス」→「ライブラリ」
4. 「Google Sheets API」を検索して **有効化**
5. 左メニュー → 「APIとサービス」→「認証情報」
6. 「認証情報を作成」→「サービスアカウント」をクリック
7. サービスアカウント名を入力（例: `estimate-writer`）→ 作成して続行
8. ロールは「編集者」を選択 → 完了

## 手順2：JSONキーをダウンロード

1. 「認証情報」ページでいま作ったサービスアカウントをクリック
2. 「キー」タブ →「鍵を追加」→「新しい鍵を作成」→ JSON形式
3. ダウンロードしたJSONファイルを保存：  
   `図面チェック_自動見積積算システム/credentials/service_account.json`

## 手順3：スプレッドシートを共有する

1. 転記先のGoogleスプレッドシートを開く
2. 右上「共有」ボタンをクリック
3. 手順1で作ったサービスアカウントのメールアドレスを追加  
   （JSONファイル内の `client_email` 欄に記載。例: `estimate-writer@kaedekoumuten-estimate.iam.gserviceaccount.com`）
4. 権限は「編集者」で共有

## 手順4：サーバーの .env に設定

```
GOOGLE_CREDENTIALS_FILE=credentials/service_account.json
GOOGLE_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/（スプレッドシートのID）/edit
```

---

## シート構成（転記される内容）

転記先に「積算」シートが自動作成されます（既存の場合は上書き）。

| 列 | 内容 |
|---|---|
| A | 工種 |
| B | 品目 |
| C | 数量 |
| D | 単位 |
| E | 単価（円） |
| F | 金額（円） |

物件ごとにシート名を変えたい場合は、サイドバーの「シート名」入力欄で変更してください。

---

## 既存フォーマットへの対応

既存スプレッドシートに独自のフォーマット（列順・行番号など）がある場合は、  
`src/sheets_exporter.py` の `write_estimate()` 関数内の列マッピングを調整します。  
フォーマットを教えていただければ対応します。
