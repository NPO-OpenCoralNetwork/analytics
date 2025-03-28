from typing import Dict, List, Optional
from datetime import datetime
import os
import json
from notion_client import Client
from supabase import create_client, Client as SupabaseClient
from postgrest import APIError

class DatabaseConnector:
    """Supabase接続とNotion連携を管理するクラス"""
    
    def __init__(self):
        """初期化"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URLとKeyが必要です")

        self.notion_token = os.getenv("NOTION_API_KEY")
        if not self.notion_token:
            raise ValueError("Notion APIトークンが必要です")

        self.supabase: SupabaseClient = create_client(supabase_url, supabase_key)
        self.notion = Client(auth=self.notion_token)

    def save_budget_items(self, items: List[Dict]) -> List[int]:
        """予算項目をデータベースに保存"""
        ids = []
        
        try:
            for item in items:
                # 政策分野の取得または作成
                policy_area_id = self._get_policy_area_id(item["policy_area"])
                
                # プロジェクトの保存
                project_data = {
                    "name": item["project_name"],
                    "description": item["description"],
                    "budget_amount": item["budget_amount"],
                    "kpi_json": json.dumps(item["kpi"]),
                    "municipality_id": 1,  # 富山市のID
                    "policy_area_id": policy_area_id,
                    "fiscal_year": item["fiscal_year"]
                }
                
                result = self.supabase.table("projects").insert(project_data).execute()
                project_id = result.data[0]["id"]
                ids.append(project_id)
                
                # KPI履歴の保存
                if item["kpi"]:
                    self._save_kpi_history(project_id, item["kpi"])
            
            return ids
            
        except APIError as e:
            print(f"Error saving budget items: {str(e)}")
            raise

    def _get_policy_area_id(self, policy_area: str) -> int:
        """施策分野のIDを取得（存在しない場合は新規作成）"""
        try:
            # 既存の政策分野を検索
            result = self.supabase.table("policy_areas") \
                .select("id") \
                .eq("name", policy_area) \
                .execute()
            
            if result.data:
                return result.data[0]["id"]
            
            # 新規作成
            insert_result = self.supabase.table("policy_areas").insert({
                "name": policy_area,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            return insert_result.data[0]["id"]
            
        except APIError as e:
            print(f"Error getting policy area ID: {str(e)}")
            raise

    def _save_kpi_history(self, project_id: int, kpi_data: Dict):
        """KPI履歴を保存"""
        try:
            for metric_name, value in kpi_data.items():
                if isinstance(value, dict):
                    target_value = value.get("target")
                    current_value = value.get("current", 0)
                else:
                    target_value = value
                    current_value = 0

                self.supabase.table("kpi_history").insert({
                    "project_id": project_id,
                    "metric_name": metric_name,
                    "metric_value": current_value,
                    "target_value": target_value,
                    "measured_date": datetime.now().isoformat()
                }).execute()
                
        except APIError as e:
            print(f"Error saving KPI history: {str(e)}")
            raise

    def sync_to_notion(self, database_id: str):
        """Supabaseのデータをトionと同期"""
        try:
            # ビューからデータを取得
            result = self.supabase.from_("notion_project_view").select("*").execute()
            
            for row in result.data:
                self._create_notion_page(database_id, row)
                
        except APIError as e:
            print(f"Error syncing to Notion: {str(e)}")
            raise

    def _create_notion_page(self, database_id: str, data: Dict):
        """
        Notionページを作成
        
        Args:
            database_id: NotionデータベースID
            data: ページデータ
        """
        try:
            self.notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "事業名": {"title": [{"text": {"content": data["事業名"]}}]},
                    "事業概要": {"rich_text": [{"text": {"content": data["事業概要"]}}]},
                    "予算額": {"number": data["予算額"]},
                    "施策分野": {"select": {"name": data["施策分野"]}},
                    "自治体": {"select": {"name": data["自治体名"]}},
                    "KPI": {"rich_text": [{"text": {"content": json.dumps(data["KPI情報"], ensure_ascii=False)}}]}
                }
            )
        except Exception as e:
            print(f"Error creating Notion page: {str(e)}")
            raise

if __name__ == "__main__":
    # 使用例
    connector = DatabaseConnector()
    
    # サンプルデータの保存
    sample_items = [{
        "project_name": "地域活性化推進事業",
        "description": "地域コミュニティの活性化を目的とした総合的な支援事業",
        "budget_amount": 10000000,
        "policy_area": "地域振興",
        "fiscal_year": 2025,
        "kpi": {
            "地域活動参加者数": {"target": 1000, "current": 0},
            "新規コミュニティ事業数": {"target": 5, "current": 0}
        }
    }]
    
    try:
        # データベースに保存
        project_ids = connector.save_budget_items(sample_items)
        print(f"Created projects: {project_ids}")
        
        # Notionと同期
        notion_database_id = os.getenv("NOTION_DATABASE_ID")
        connector.sync_to_notion(notion_database_id)
        print("Synced with Notion successfully")
        
    except Exception as e:
        print(f"Error in sample execution: {str(e)}")
