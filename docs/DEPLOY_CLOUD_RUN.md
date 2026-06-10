# Google Cloud Run デプロイ手順

ウェブ上のアプリとして公開する方法です。  
URLを知っている人なら社外からもアクセスできます。

## 前提条件
- Google Cloud アカウント（Googleスプレッドシート用に既に作成済みであれば同じプロジェクトを使用可）
- Google Cloud CLI のインストール → https://cloud.google.com/sdk/docs/install

---

## 手順

### 1. gcloud にログイン
```
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. 必要なAPIを有効化
```
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 3. Secret Manager にAPIキーを登録（推奨）
```
echo -n "sk-ant-..." | gcloud secrets create ANTHROPIC_API_KEY --data-file=-
echo -n "your-password" | gcloud secrets create APP_PASSWORD --data-file=-
```

### 4. Artifact Registry にDockerイメージをプッシュ
```
gcloud artifacts repositories create drawing-app --repository-format=docker --location=asia-northeast1
gcloud builds submit --tag asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/drawing-app/app
```

### 5. Cloud Run にデプロイ
```
gcloud run deploy drawing-check-app \
  --image asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/drawing-app/app \
  --region asia-northeast1 \
  --platform managed \
  --set-secrets "ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,APP_PASSWORD=APP_PASSWORD:latest" \
  --memory 1Gi \
  --timeout 300
```

### 6. アクセス制限（社内のみに絞る場合）
デプロイ時に `--no-allow-unauthenticated` を付けると、Google アカウント認証が必要になります。  
または `APP_PASSWORD` を設定することで簡易パスワード保護が使えます。

---

## 費用の目安

| 使用量 | 月額目安 |
|---|---|
| 月50リクエスト以下 | **ほぼ無料**（無料枠内） |
| 月200リクエスト | 約200〜500円 |

Cloud Run は使った分だけの課金（リクエストがないときは課金なし）。

---

## 社内LAN共有（Cloud なし）

Cloud Run を使わず社内のPCで起動してLAN共有する方法：

1. `start.bat` をダブルクリック
2. 起動後に表示される `http://[PC名]:8501` を社内のメンバーに共有
3. 同じWi-Fi・LAN内ならスマホ・タブレットからもアクセス可能

この方法はGoogle Cloudの設定不要、費用も無料です。  
PCがスリープ/シャットダウンするとアクセスできなくなります。
