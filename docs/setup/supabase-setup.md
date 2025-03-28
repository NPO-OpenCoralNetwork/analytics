# Supabase設定ガイド

## 1. プロジェクトの作成

1. Supabaseダッシュボード（https://app.supabase.com）にアクセス
2. 「New Project」をクリック
3. 以下の情報を入力：
   - Organization: 任意の組織名
   - Name: `toyama-analytics`
   - Database Password: 安全なパスワードを設定
   - Region: Tokyo (または最寄りのリージョン)
   - Pricing Plan: Free (または必要に応じてPro)

## 2. データベースの設定

1. SQL Editorを開く
2. `schema.sql`の内容を貼り付けて実行
3. 実行結果を確認し、全てのテーブルとポリシーが正しく作成されていることを確認

## 3. API設定

### 必要な認証情報の取得
1. Project Settings > API から以下の情報を取得：
   - Project URL (`SUPABASE_URL`)
   - anon public key (`SUPABASE_ANON_KEY`)
   - service_role key (`SUPABASE_KEY`)

### 環境変数の設定
```bash
cp .env.example .env
```

.envファイルを編集：
```env
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
```

## 4. Row Level Security (RLS)の設定

既に`schema.sql`で以下のポリシーが設定されています：

1. 読み取りポリシー
   - 全てのテーブルで全ユーザーに読み取りを許可

2. 書き込み・更新ポリシー
   - 管理者ロールを持つユーザーのみに許可

## 5. ユーザー認証の設定

### 管理者ユーザーの作成
1. Authentication > Users に移動
2. "Invite user"をクリック
3. メールアドレスを入力
4. 招待メールが送信される

### 管理者ロールの付与
1. SQL Editorで以下を実行：
```sql
update auth.users
set raw_user_meta_data = '{"role": "admin"}'
where email = '管理者のメールアドレス';
```

## 6. バックアップ設定

### 自動バックアップ（Pro プラン以上）
1. Project Settings > Database に移動
2. Backups セクションで設定：
   - Daily backups: 有効化
   - Backup retention period: 7日

### 手動バックアップ
1. Dashboard > Database
2. "Create backup"をクリック
3. バックアップ完了後、ダウンロード可能

## 7. 監視とログ

### リアルタイムログの確認
1. Project Settings > API に移動
2. API Requests セクションでログを確認

### パフォーマンス監視
1. Dashboard > Database
2. Performance メトリクスを確認：
   - CPU使用率
   - メモリ使用率
   - ディスク使用量

## 8. 本番環境の注意点

1. セキュリティ
   - `service_role`キーは安全に管理
   - 本番環境では環境変数を適切に設定
   - RLSポリシーの定期的な見直し

2. パフォーマンス
   - インデックスの定期的な確認
   - クエリパフォーマンスの監視
   - 必要に応じてプランのアップグレード

3. バックアップ
   - 定期的なバックアップの確認
   - リストア手順の確認と文書化

## 9. トラブルシューティング

### よくある問題と解決方法

1. RLSエラー
   ```
   エラー: new row violates row-level security policy
   ```
   - 解決: ユーザーロールと権限を確認

2. 接続エラー
   ```
   エラー: could not connect to server
   ```
   - 解決: URLとAPIキーを確認

3. クエリタイムアウト
   ```
   エラー: query timeout
   ```
   - 解決: クエリの最適化やインデックスの追加を検討

## 10. 参考リンク

- Supabase 公式ドキュメント: https://supabase.com/docs
- PostgreSQL 公式ドキュメント: https://www.postgresql.org/docs/
- Row Level Security: https://supabase.com/docs/guides/auth/row-level-security
