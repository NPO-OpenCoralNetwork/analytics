# 富山県自治体データ分析システム 仕様書

## 1. 概要

### 1.1 目的
本システムは、NPO団体が富山県の自治体資料を効率的に分析し、地域ニーズを把握した上で効果的なプロジェクト提案を行うことを目的とする。Notion、GitHub、SQL、Grafanaを組み合わせたハイブリッド環境により、多様なスキルレベルのチームメンバーがデータドリブンな意思決定を行えるようにする。

### 1.2 システム概念図
```
[データソース] → [ETLパイプライン] → [SQLデータベース] ↔ [分析レイヤー] → [表示レイヤー]
                      ↑                     ↑               ↓
                   [GitHub]              [AI連携]     [Notion/Grafana]
```

### 1.3 主な機能
- 自治体文書のデジタル化と構造化
- 政策傾向と予算配分の分析
- 地域課題の可視化
- AI支援による洞察生成
- チーム協働でのプロジェクト提案作成

## 2. システムアーキテクチャ

### 2.1 コンポーネント構成

#### 2.1.1 データ層
| コンポーネント | 説明 | 技術要素 |
|--------------|------|---------|
| メインデータベース | 自治体データの永続的保存 | PostgreSQL 14+ |
| ファイルストレージ | 原本PDFなどの保存 | AWS S3 / MinIO |

#### 2.1.2 処理層
| コンポーネント | 説明 | 技術要素 |
|--------------|------|---------|
| ETLパイプライン | データ取り込み・変換 | Python, pandas, Apache Airflow |
| テキスト処理 | 文書解析・特徴抽出 | MeCab, BERT, spaCy |
| データ変換 | SQL変換処理 | dbt |

#### 2.1.3 分析層
| コンポーネント | 説明 | 技術要素 |
|--------------|------|---------|
| データ分析 | 統計分析・機械学習 | Python, scikit-learn, statsmodels |
| AI連携 | 自然言語処理・洞察生成 | LangChain, OpenAI API / Azure OpenAI |

#### 2.1.4 表示層
| コンポーネント | 説明 | 技術要素 |
|--------------|------|---------|
| ダッシュボード | データ可視化 | Grafana |
| 知識ベース | 文書管理・協働 | Notion |
| コード管理 | バージョン管理・CI/CD | GitHub, GitHub Actions |

### 2.2 データフロー

1. データ取り込み
   - 自治体ウェブサイトからのスクレイピング
   - PDF文書のテキスト抽出
   - 構造化データ(CSV, Excel)の取り込み

2. データ処理
   - テキストのクリーニングと正規化
   - キーワード抽出と分類
   - 時系列データの前処理

3. データ分析
   - トレンド分析
   - 予算配分分析
   - テキストマイニング
   - 地理空間分析

4. 結果表示
   - Grafanaでのインタラクティブダッシュボード
   - Notionでの分析レポート
   - AIによる洞察レポート

## 3. 各コンポーネント詳細仕様

### 3.1 PostgreSQLデータベース設計

#### 3.1.1 主要テーブル構成
```sql
-- 自治体マスタ
CREATE TABLE municipalities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    population INTEGER,
    area FLOAT,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文書テーブル
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    municipality_id INTEGER REFERENCES municipalities(id),
    title VARCHAR(200) NOT NULL,
    document_type VARCHAR(50),
    publish_date DATE,
    fiscal_year INTEGER,
    file_path VARCHAR(500),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 予算データ
CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    municipality_id INTEGER REFERENCES municipalities(id),
    fiscal_year INTEGER NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    amount BIGINT NOT NULL,
    is_expense BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- キーワード出現
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    keyword VARCHAR(100) NOT NULL,
    frequency INTEGER DEFAULT 1,
    importance FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 政策分野
CREATE TABLE policy_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES policy_areas(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 政策-文書関連付け
CREATE TABLE document_policy_mapping (
    document_id INTEGER REFERENCES documents(id),
    policy_area_id INTEGER REFERENCES policy_areas(id),
    confidence FLOAT DEFAULT 1.0,
    PRIMARY KEY (document_id, policy_area_id)
);
```

#### 3.1.2 インデックス設計
```sql
-- 全文検索用インデックス
CREATE INDEX documents_content_idx ON documents USING gin(to_tsvector('japanese', content));

-- 検索高速化用インデックス
CREATE INDEX documents_municipality_year_idx ON documents(municipality_id, fiscal_year);
CREATE INDEX budgets_municipality_year_idx ON budgets(municipality_id, fiscal_year);
CREATE INDEX keywords_document_idx ON keywords(document_id);
```

### 3.2 ETLパイプライン仕様

#### 3.2.1 データ取り込みワークフロー
1. スクレイピングパイプライン
   - 頻度: 週1回
   - 対象: 富山県内市町村公式Webサイト
   - 取得項目: 新規公開文書、議事録、報道発表

2. PDF処理パイプライン
   - 頻度: 日次
   - 処理: OCR、テキスト抽出、メタデータ抽出
   - 出力: テキストデータ、文書メタデータ

3. 構造化データ処理
   - 頻度: 月次
   - 対象: 予算データ、統計データ
   - 処理: データクリーニング、正規化、時系列変換

#### 3.2.2 GitHub連携仕様
- リポジトリ構成:
  ```
  /data-pipelines/
    /scrapers/
    /pdf-processors/
    /data-transformers/
  /analysis/
    /budget-analysis/
    /text-mining/
    /geo-analysis/
  /dashboards/
    /grafana-dashboards/
    /notion-templates/
  /ai-integration/
    /langchain-processors/
    /insight-generators/
  ```

- GitHub Actions:
  - `weekly-scrape.yml`: 週次スクレイピング
  - `daily-pdf-process.yml`: 日次PDF処理
  - `monthly-data-update.yml`: 月次データ更新
  - `on-demand-analysis.yml`: オンデマンド分析

### 3.3 Grafanaダッシュボード仕様

#### 3.3.1 メインダッシュボード
- **富山県政策トレンドダッシュボード**
  - パネル1: 政策分野別キーワード出現頻度（時系列）
  - パネル2: 自治体別予算配分比較
  - パネル3: 地域別重点施策マップ
  - パネル4: 最新政策文書リスト

#### 3.3.2 分析ダッシュボード
- **予算分析ダッシュボード**
  - パネル1: 分野別予算推移（過去5年）
  - パネル2: 自治体間予算配分比較
  - パネル3: 一人当たり予算額比較
  - パネル4: 予算執行率分析

- **政策分析ダッシュボード**
  - パネル1: キーワードクラウド
  - パネル2: 政策関連性ネットワーク
  - パネル3: 政策文書-予算相関分析
  - パネル4: 政策実施状況追跡

#### 3.3.3 Notionとの連携
- 埋め込み用iframe生成
- スナップショット自動保存機能
- ダッシュボードURLリンク生成

### 3.4 Notion設計仕様

#### 3.4.1 ワークスペース構成
```
富山県自治体分析
├── 📁 プロジェクト管理
│   ├── 📄 全体計画
│   ├── 📄 タスク管理
│   └── 📄 ミーティングノート
├── 📁 自治体別ページ
│   ├── 📄 富山市
│   ├── 📄 高岡市
│   └── ...
├── 📁 分析レポート
│   ├── 📄 予算分析
│   ├── 📄 政策トレンド分析
│   └── 📄 地域課題マッピング
├── 📁 提案作成
│   ├── 📄 提案テンプレート
│   ├── 📄 過去の提案
│   └── 📄 提案ステータス管理
└── 📁 リソース
    ├── 📄 データソース一覧
    ├── 📄 分析手法ガイド
    └── 📄 Grafanaダッシュボード
```

#### 3.4.2 データベース設計
- **自治体DB**
  - プロパティ: 名前、人口、地域、予算規模、主要産業、連絡先、最終更新日

- **文書DB**
  - プロパティ: タイトル、自治体、文書種別、発行日、URL、分析ステータス、担当者

- **プロジェクト提案DB**
  - プロパティ: 提案名、対象自治体、予算規模、期間、ステータス、担当者、作成日

- **分析タスクDB**
  - プロパティ: タスク名、種別、優先度、担当者、ステータス、期日、関連文書

#### 3.4.3 テンプレート
- 自治体分析シート
- 政策分析レポート
- プロジェクト提案テンプレート
- 議事録テンプレート

### 3.5 AI連携仕様

#### 3.5.1 LangChain実装
```python
# 基本構成例
from langchain import PromptTemplate, LLMChain, SQLDatabase
from langchain.llms import OpenAI
from langchain.agents import create_sql_agent
from langchain.tools.sql_database.tool import QuerySQLDataBaseTool

# データベース接続
db = SQLDatabase.from_uri("postgresql://user:pass@localhost/toyama_data")

# SQL生成エージェント
sql_agent = create_sql_agent(
    llm=OpenAI(temperature=0),
    toolkit=QuerySQLDataBaseTool(db=db),
    verbose=True
)

# 政策分析プロンプト
policy_analysis_prompt = PromptTemplate(
    input_variables=["municipality", "keywords", "budget_data"],
    template="""
    富山県{municipality}の政策分析を行ってください。
    
    主要キーワード: {keywords}
    
    予算データ: {budget_data}
    
    以下の点について分析してください：
    1. この自治体の主要な政策方針
    2. 予算配分から見る優先事項
    3. 他自治体との比較での特徴
    4. NPOとして提案できる可能性のあるプロジェクト
    """
)

policy_chain = LLMChain(llm=OpenAI(temperature=0.7), prompt=policy_analysis_prompt)
```

#### 3.5.2 自然言語→SQL変換
- クエリ例: "富山市の過去3年間の福祉関連予算の推移を教えて"
- 変換SQL:
```sql
SELECT fiscal_year, SUM(amount) as total_amount
FROM budgets
JOIN municipalities ON budgets.municipality_id = municipalities.id
WHERE municipalities.name = '富山市'
  AND category = '福祉'
  AND fiscal_year >= (SELECT MAX(fiscal_year) - 2 FROM budgets)
GROUP BY fiscal_year
ORDER BY fiscal_year;
```

#### 3.5.3 自動洞察生成
- 頻度: 週1回
- 入力: 新規文書、予算更新、キーワードトレンド
- 出力: Notionページへの自動投稿

## 4. 実装計画

### 4.1 フェーズ分割

#### フェーズ1: 基盤構築（1-2ヶ月）
- Notion環境セットアップ
- GitHub環境構築
- 基本データ収集と手動分析

#### フェーズ2: データベース実装（2-3ヶ月）
- PostgreSQL設計と実装
- 基本ETLパイプライン構築
- 初期データ投入

#### フェーズ3: 可視化基盤（1-2ヶ月）
- Grafanaセットアップ
- 基本ダッシュボード作成
- Notion連携確立

#### フェーズ4: AI連携と高度化（2-3ヶ月）
- LangChain実装
- 自動洞察生成
- 高度な分析機能追加

### 4.2 リソース要件

#### ハードウェア/クラウド
- PostgreSQL: 最小2vCPU/4GB RAM
- ETLサーバー: 最小2vCPU/4GB RAM
- Grafana: 最小1vCPU/2GB RAM
- ストレージ: 初期100GB（文書保存用）

#### ソフトウェア/サービス
- Notion: チームプラン
- GitHub: チームプラン
- PostgreSQL: 14+
- Grafana: OSS版 or Grafana Cloud
- OpenAI API / Azure OpenAI

#### 人的リソース
- データエンジニア: 0.5人月
- バックエンド開発者: 1人月
- データアナリスト: 1人月
- プロジェクトマネージャー: 0.5人月

## 5. 運用・保守計画

### 5.1 定期メンテナンス
- データベースバックアップ: 日次
- インデックス再構築: 週次
- システム状態チェック: 日次
- パッチ適用: 月次

### 5.2 モニタリング
- ETL成功率
- クエリ実行時間
- API利用量（特にAI API）
- ストレージ使用量

### 5.3 拡張計画
- 自治体職員向け閲覧インターフェース
- 市民参加型データ収集メカニズム
- 政策シミュレーションモジュール

## 6. セキュリティと個人情報保護

### 6.1 データ保護方針
- 個人識別情報の匿名化処理
- アクセス制御とユーザー権限管理
- 通信経路の暗号化（HTTPS/TLS）

### 6.2 バックアップと復旧
- 自動バックアップスケジュール
- オフサイトバックアップ保存
- 復旧手順とテスト計画

## 7. 付録

### 7.1 用語集
- ETL: Extract, Transform, Load（抽出、変換、読み込み）
- API: Application Programming Interface
- AI: Artificial Intelligence（人工知能）
- NLP: Natural Language Processing（自然言語処理）

### 7.2 参考資料
- PostgreSQL公式ドキュメント
- Grafana公式ドキュメント
- LangChain公式ドキュメント
- Notion API公式ドキュメント

---

文書バージョン: 1.0  
作成日: 2025年3月28日  
最終更新日: 2025年3月28日