# プロジェクトセットアップガイド

## 前提条件

- Python 3.8以上
- PostgreSQL 14以上
- MeCab（日本語形態素解析用）
- Node.js 16以上（Notionインテグレーション用）
- Docker（オプション：MinIOコンテナ用）

## 初期セットアップ手順

### 1. リポジトリのクローンと環境設定

```bash
# リポジトリのクローン
git clone https://github.com/your-organization/toyama-analytics.git
cd toyama-analytics

# Python仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して必要な情報を設定
```

### 2. データベースのセットアップ

```bash
# PostgreSQLデータベースの作成
psql -U postgres -f database/schema.sql

# データベース接続確認
psql -U your_user -d toyama_analytics -c "\dt"
```

### 3. MinIOのセットアップ（ローカルS3代替）

```bash
# MinIOコンテナの起動
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=admin" \
  -e "MINIO_ROOT_PASSWORD=password" \
  -v ${PWD}/minio_data:/data \
  minio/minio server /data --console-address ":9001"
```

### 4. Airflowの初期設定

```bash
# Airflow用のディレクトリ作成
mkdir -p data-pipelines/airflow/dags
mkdir -p data-pipelines/airflow/logs
mkdir -p data-pipelines/airflow/plugins

# Airflow設定の初期化
export AIRFLOW_HOME=./data-pipelines/airflow
airflow db init

# 管理者ユーザーの作成
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### 5. Grafanaのセットアップ

```bash
# Grafanaコンテナの起動
docker run -d \
  -p 3000:3000 \
  --name grafana \
  -v ${PWD}/dashboards/grafana-dashboards:/var/lib/grafana/dashboards \
  grafana/grafana
```

## 開発用コマンド

### データパイプラインの開発

```bash
# Airflowの開発用サーバー起動
airflow webserver -p 8080
airflow scheduler

# ETLジョブのテスト実行
python -m pytest tests/etl/
```

### データベース操作

```bash
# データベースバックアップ
pg_dump -U your_user toyama_analytics > backup.sql

# バックアップからの復元
psql -U your_user toyama_analytics < backup.sql
```

### コード品質管理

```bash
# コードフォーマット
black .

# リンター実行
flake8 .

# 型チェック
mypy .

# テスト実行
pytest
```

## トラブルシューティング

### よくある問題と解決方法

1. データベース接続エラー
   - PostgreSQLサービスが起動していることを確認
   - .envファイルの接続情報が正しいことを確認

2. MeCabのインストールエラー
   - Windowsの場合：公式サイトからインストーラーを使用
   - Mac/Linuxの場合：パッケージマネージャーを使用

3. Airflowの起動エラー
   - AIRFLOW_HOME環境変数が正しく設定されているか確認
   - データベース初期化が完了しているか確認

### ログの確認方法

- アプリケーションログ: `logs/app.log`
- Airflowログ: `data-pipelines/airflow/logs/`
- データベースログ: PostgreSQLのログ設定を確認

## 開発環境のカスタマイズ

### VS Code設定

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### Git hooks

開発環境では以下のGit hooksを使用することを推奨します：

- pre-commit: コードフォーマットとリンターチェック
- pre-push: テストの実行

これらのhooksは`.git/hooks/`ディレクトリに配置してください。

## 注意事項

- 本番環境の認証情報は.envファイルで管理し、Gitにコミットしないでください
- APIキーやパスワードなどの機密情報は必ず環境変数として管理してください
- データベースのバックアップは定期的に実行することを推奨します
