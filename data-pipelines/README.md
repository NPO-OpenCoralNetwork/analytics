# 予算データ処理パイプライン

## 概要
富山市の予算文書からデータを抽出し、構造化されたデータとしてPostgreSQLに保存し、Notionで可視化するパイプライン。

## 機能
- PDF文書からのテキスト抽出
- OpenAI APIを使用した予算データの構造化
- PostgreSQLへのデータ保存
- Notionとの自動同期

## 必要条件
- Python 3.8以上
- PostgreSQL 14以上
- OpenAI APIキー
- Notion APIキー

## セットアップ手順

1. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

2. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集して以下の値を設定:
# - DATABASE_URL
# - OPENAI_API_KEY
# - NOTION_API_KEY
# - NOTION_DATABASE_ID
```

3. データベースの初期化
```bash
cd database
psql -U your_user -d your_database -f schema.sql
```

## 使用方法

### PDFの処理と予算データの抽出
```bash
python process_budget.py --pdf-dir /path/to/pdfs --log-level INFO
```

オプション:
- `--pdf-dir`: 処理対象のPDFが格納されているディレクトリ（必須）
- `--log-level`: ログレベル（DEBUG/INFO/WARNING/ERROR、デフォルト：INFO）

### 処理結果
- 抽出されたデータはPostgreSQLに保存されます
- 処理結果のJSONは`output/[timestamp]/analysis_results.json`に保存されます
- Notionデータベースが自動的に更新されます

## ディレクトリ構造
```
data-pipelines/
├── pdf-processors/      # PDF処理モジュール
├── langchain-processors/ # テキスト解析モジュール
├── data-transformers/   # データ変換モジュール
├── process_budget.py    # メイン処理スクリプト
└── README.md
```

## エラーハンドリング

主なエラーケースと対処方法:

1. PDF読み取りエラー
   - PDFファイルが破損していないか確認
   - ファイルのアクセス権限を確認

2. OpenAI API エラー
   - APIキーの有効性を確認
   - クレジットの残高を確認
   - レートリミットに注意

3. データベース接続エラー
   - PostgreSQLサービスが起動していることを確認
   - 接続情報が正しいか確認
   - ファイアウォール設定を確認

4. Notion同期エラー
   - APIキーの有効性を確認
   - データベースIDが正しいか確認
   - Notionの統合設定を確認

## ログ
- ログファイル: `logs/budget_processing.log`
- ログレベルの変更: `--log-level`オプションで指定

## トラブルシューティング

### よくある問題

1. テキスト抽出の精度が低い
   - OCRエンジンの設定を調整
   - PDFの品質を確認

2. データ構造化の精度が低い
   - プロンプトテンプレートの調整
   - モデルパラメータの調整

3. Notion同期が失敗する
   - レートリミットの確認
   - ページプロパティの設定確認

## 開発メモ

### 今後の改善点
1. 並列処理の導入
2. エラーリトライの実装
3. バッチ処理の最適化
4. テストカバレッジの向上

### パフォーマンス
- 1PDFあたりの処理時間: 約30秒
- OpenAI APIコスト: 約$0.2/文書
- メモリ使用量: 約500MB
