-- データベース作成
CREATE DATABASE toyama_analytics;

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

-- インデックス作成
-- 全文検索用インデックス
CREATE INDEX documents_content_idx ON documents USING gin(to_tsvector('japanese', content));

-- 検索高速化用インデックス
CREATE INDEX documents_municipality_year_idx ON documents(municipality_id, fiscal_year);
CREATE INDEX budgets_municipality_year_idx ON budgets(municipality_id, fiscal_year);
CREATE INDEX keywords_document_idx ON keywords(document_id);

-- 初期データ投入（富山県の市町村）
INSERT INTO municipalities (name, region) VALUES
('富山市', '富山県中部'),
('高岡市', '富山県西部'),
('魚津市', '富山県東部'),
('氷見市', '富山県西部'),
('滑川市', '富山県東部'),
('黒部市', '富山県東部'),
('砺波市', '富山県西部'),
('小矢部市', '富山県西部'),
('南砺市', '富山県西部'),
('射水市', '富山県西部'),
('舟橋村', '富山県中部'),
('上市町', '富山県東部'),
('立山町', '富山県中部'),
('入善町', '富山県東部'),
('朝日町', '富山県東部');

-- トリガー作成（更新日時自動設定用）
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_municipalities_timestamp
    BEFORE UPDATE ON municipalities
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_documents_timestamp
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_budgets_timestamp
    BEFORE UPDATE ON budgets
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
