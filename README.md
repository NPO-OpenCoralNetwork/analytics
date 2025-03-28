# 富山県自治体データ分析システム

富山県の自治体データを分析し、NPOプロジェクト提案を効率的に行うためのデータ分析プラットフォーム

## 概要

本プロジェクトは、富山県内の自治体が公開する政策文書、予算データ、統計情報などを効率的に収集・分析し、地域ニーズを把握した上で効果的なプロジェクト提案を行うためのシステムです。Notion、GitHub、SQL、Grafanaを組み合わせたハイブリッド環境により、多様なスキルレベルのチームメンバーが協働してデータドリブンな意思決定を行うことができます。

## 主な機能

- 自治体文書のデジタル化と構造化
- 政策傾向と予算配分の分析
- 地域課題の可視化
- AI支援による洞察生成
- チーム協働でのプロジェクト提案作成

## システムアーキテクチャ

```
[データソース] → [ETLパイプライン] → [SQLデータベース] ↔ [分析レイヤー] → [表示レイヤー]
                      ↑                     ↑               ↓
                   [GitHub]              [AI連携]     [Notion/Grafana]
```

- **データ層**: PostgreSQL, AWS S3/MinIO
- **処理層**: Python, pandas, Apache Airflow, MeCab, dbt
- **分析層**: Python, scikit-learn, LangChain, OpenAI API
- **表示層**: Grafana, Notion, GitHub

## 導入手順

### 前提条件

- PostgreSQL 14以上
- Python 3.8以上
- Notion アカウント (チームプラン推奨)
- GitHub アカウント
- Grafana (OSS版またはCloud版)

### インストール手順

1. リポジトリのクローン
   ```bash
   git clone https://github.com/your-organization/toyama-analytics.git
   cd toyama-analytics
   ```

2. 必要なパッケージのインストール
   ```bash
   pip install -r requirements.txt
   ```

3. 環境設定
   ```bash
   cp .env.example .env
   # .envファイルを編集して必要な環境変数を設定
   ```

4. データベースのセットアップ
   ```bash
   psql -U your_user -d your_database -f database/schema.sql
   ```

5. Notion統合の設定
   - Notion API統合を設定し、トークンを取得
   - .envファイルにトークンを追加

6. Grafanaのセットアップ
   - Grafanaをインストールまたはクラウドアカウントを設定
   - PostgreSQLデータソースを追加
   - ダッシュボードをインポート

## 開発ロードマップ

システムは4つのフェーズに分けて開発を進める予定です：

1. **フェーズ1**: 基盤構築（1-2ヶ月）
   - Notion/GitHub環境構築
   - 基本データ収集と分析

2. **フェーズ2**: データベース実装（2-3ヶ月）
   - PostgreSQL構築
   - ETLパイプライン開発

3. **フェーズ3**: 可視化基盤（1-2ヶ月）
   - Grafanaダッシュボード開発
   - Notion連携確立

4. **フェーズ4**: AI連携と高度化（2-3ヶ月）
   - AI分析機能の追加
   - 自動洞察生成

## ドキュメント

詳細な設計や実装方法については、以下のドキュメントを参照してください：

- [システム仕様書](system-spec.md) - 詳細な設計仕様とアーキテクチャ
- [開発ガイド](docs/development-guide.md) - 開発者向けガイド
- [ユーザーマニュアル](docs/user-manual.md) - 操作マニュアル

## 貢献方法

プロジェクトへの貢献を歓迎します。貢献方法については[CONTRIBUTING.md](docs/CONTRIBUTING.md)を参照してください。

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。

## お問い合わせ

プロジェクトに関するご質問やお問い合わせは、[Issues](https://github.com/your-organization/toyama-analytics/issues)にてお願いします。