# ウェブアプリとして公開する手順

「URLを開くだけで使えるアプリ」にする手順です。  
GitHub と Streamlit Community Cloud（どちらも無料）を使います。

---

## STEP 1 : GitHub にアカウントを作る

1. https://github.com を開く
2. 「Sign up」でアカウント作成（無料）
3. メール認証を完了する

---

## STEP 2 : リポジトリ（コード置き場）を作る

1. GitHub にログインして右上の「+」→「New repository」
2. Repository name: `drawing-check-app`（なんでもOK）
3. **Private** を選択（社外に見せたくない場合）
4. 「Create repository」をクリック

---

## STEP 3 : コードを GitHub にアップロード

GitHub Desktop（GUI ツール）を使うと簡単です。

### GitHub Desktop のインストール（初回のみ）
1. https://desktop.github.com からダウンロードしてインストール
2. GitHub アカウントでサインイン

### コードをアップロード
1. GitHub Desktop を開く
2. 「Add an Existing Repository from your Hard Drive」
3. フォルダを選択：  
   `G:\マイドライブ\AIクロード\claude_workspace\図面チェック_自動見積積算システム`
4. 「create a repository」リンクをクリック
5. 右上の「Publish repository」→ さきほど作ったリポジトリを選択
6. 「Publish Repository」をクリック

---

## STEP 4 : Streamlit Community Cloud でデプロイ

1. https://streamlit.io/cloud を開く
2. 「Sign in with GitHub」でログイン
3. 「New app」をクリック
4. Repository: `drawing-check-app` を選択
5. Main file path: `src/app.py` と入力
6. 「Advanced settings」→「Secrets」に以下を貼る：

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
APP_PASSWORD = "社内で決めたパスワード"
```

7. 「Deploy!」をクリック

数分後に `https://xxxx.streamlit.app` という URL が発行されます。  
**この URL を社内メンバーに共有するだけで使えます。**

---

## コードを更新したいとき

GitHub Desktop で「Commit to main」→「Push origin」するだけで  
自動的にウェブアプリも更新されます。

---

## 注意点

| 項目 | 内容 |
|---|---|
| 費用 | 無料（月1,000リクエスト制限、超えた場合は有料プランへ） |
| データ | アップロードした図面はStreamlitのサーバーを経由する |
| 速度 | 一定時間使われないとスリープする（次のアクセスで30秒程度待つ） |

機密性の高い図面を扱う場合は Google Cloud Run（`docs/DEPLOY_CLOUD_RUN.md`）を推奨。
