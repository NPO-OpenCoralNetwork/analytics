-- Supabase用スキーマ定義
-- Note: Supabaseでは自動的にデータベースが作成されるため、CREATE DATABASE文は不要です

-- 自治体マスタ
-- 拡張機能の有効化（Supabaseで必要な場合）
create extension if not exists "uuid-ossp";

-- RLSポリシーの設定用関数
create or replace function auth.is_admin()
returns boolean as $$
  select
    coalesce(
      current_setting('request.jwt.claims', true)::json->>'role' = 'admin',
      false
    );
$$ language sql security definer;

-- 自治体テーブル
create table municipalities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    population INTEGER,
    area FLOAT,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文書テーブル
-- 文書テーブル
create table documents (
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
-- 予算テーブル
create table budgets (
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
-- キーワードテーブル
create table keywords (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    keyword VARCHAR(100) NOT NULL,
    frequency INTEGER DEFAULT 1,
    importance FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 政策分野
-- 政策分野テーブル
create table policy_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES policy_areas(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 政策-文書関連付け
-- 政策-文書マッピングテーブル
create table document_policy_mapping (
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

-- RLSポリシーの設定
alter table municipalities enable row level security;
alter table documents enable row level security;
alter table budgets enable row level security;
alter table keywords enable row level security;
alter table policy_areas enable row level security;
alter table document_policy_mapping enable row level security;

-- 読み取りポリシー（全ユーザー）
create policy "全ユーザーに読み取りを許可" on municipalities for select using (true);
create policy "全ユーザーに読み取りを許可" on documents for select using (true);
create policy "全ユーザーに読み取りを許可" on budgets for select using (true);
create policy "全ユーザーに読み取りを許可" on keywords for select using (true);
create policy "全ユーザーに読み取りを許可" on policy_areas for select using (true);
create policy "全ユーザーに読み取りを許可" on document_policy_mapping for select using (true);

-- 書き込みポリシー（管理者のみ）
create policy "管理者のみ書き込み可能" on municipalities for insert with check (auth.is_admin());
create policy "管理者のみ書き込み可能" on documents for insert with check (auth.is_admin());
create policy "管理者のみ書き込み可能" on budgets for insert with check (auth.is_admin());
create policy "管理者のみ書き込み可能" on keywords for insert with check (auth.is_admin());
create policy "管理者のみ書き込み可能" on policy_areas for insert with check (auth.is_admin());
create policy "管理者のみ書き込み可能" on document_policy_mapping for insert with check (auth.is_admin());

-- 更新・削除ポリシー（管理者のみ）
create policy "管理者のみ更新可能" on municipalities for update using (auth.is_admin());
create policy "管理者のみ更新可能" on documents for update using (auth.is_admin());
create policy "管理者のみ更新可能" on budgets for update using (auth.is_admin());
create policy "管理者のみ更新可能" on keywords for update using (auth.is_admin());
create policy "管理者のみ更新可能" on policy_areas for update using (auth.is_admin());
create policy "管理者のみ更新可能" on document_policy_mapping for update using (auth.is_admin());

-- トリガー作成（更新日時自動設定用）
create or replace function update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

create trigger update_municipalities_timestamp
    BEFORE UPDATE ON municipalities
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

create trigger update_documents_timestamp
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

create trigger update_budgets_timestamp
-- Notionビュー
create or replace view notion_project_view as
select 
    p.name as "事業名",
    p.description as "事業概要",
    p.budget_amount as "予算額",
    pa.name as "施策分野",
    m.name as "自治体名",
    p.kpi_json as "KPI情報"
from projects p
join municipalities m on p.municipality_id = m.id
join policy_areas pa on p.policy_area_id = pa.id;

-- APIビュー（Supabase Edge Functions用）
create or replace view api_project_summary as
select 
    p.id,
    p.name,
    p.description,
    p.budget_amount,
    pa.name as policy_area,
    m.name as municipality,
    p.fiscal_year,
    p.kpi_json,
    p.created_at,
    p.updated_at
from projects p
join municipalities m on p.municipality_id = m.id
join policy_areas pa on p.policy_area_id = pa.id;
