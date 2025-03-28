from typing import Dict, List, Optional
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
import json

class BudgetItem(BaseModel):
    """予算項目のデータモデル"""
    project_name: str = Field(description="事業名")
    budget_amount: int = Field(description="予算額（円）")
    policy_area: str = Field(description="施策分野")
    description: str = Field(description="事業概要")
    fiscal_year: int = Field(description="年度")
    kpi: Dict = Field(description="KPI/目標値")

class BudgetAnalyzer:
    """予算文書の分析クラス"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            api_key: OpenAI APIキー（未指定の場合は環境変数から取得）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI APIキーが必要です")

        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo-16k",
            openai_api_key=self.api_key
        )
        
        self.parser = PydanticOutputParser(pydantic_object=BudgetItem)

    def create_extraction_prompt(self) -> PromptTemplate:
        """抽出用プロンプトテンプレートの作成"""
        template = """
        以下の予算文書から、事業情報を抽出してJSON形式で出力してください。
        
        入力文書:
        {text}
        
        以下の形式で出力してください:
        {format_instructions}
        
        注意事項:
        - 予算額は数値型で出力（カンマや円マークは除去）
        - 事業名は正式名称を使用
        - KPIがある場合は具体的な指標と目標値を含める
        - 施策分野は最も適切なカテゴリを選択
        
        回答:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def analyze_budget_text(self, text: str) -> BudgetItem:
        """
        予算文書のテキストを分析し、構造化データを抽出
        
        Args:
            text: 分析対象のテキスト
            
        Returns:
            BudgetItem: 構造化された予算情報
        """
        prompt = self.create_extraction_prompt()
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(text=text)
            return self.parser.parse(result)
        except Exception as e:
            print(f"Error analyzing budget text: {str(e)}")
            raise

    def analyze_budget_document(self, document: Dict) -> List[BudgetItem]:
        """
        予算文書全体を分析
        
        Args:
            document: 文書情報を含む辞書
            
        Returns:
            List[BudgetItem]: 抽出された予算項目のリスト
        """
        results = []
        
        # ページごとに処理
        pages = document.get("text", "").split("\n\n")
        for page in pages:
            if not page.strip():
                continue
                
            try:
                budget_item = self.analyze_budget_text(page)
                results.append(budget_item)
            except Exception as e:
                print(f"Error processing page: {str(e)}")
                continue
                
        return results

    def save_results(self, results: List[BudgetItem], output_path: str):
        """
        分析結果をJSONファイルとして保存
        
        Args:
            results: 分析結果のリスト
            output_path: 出力ファイルパス
        """
        output_data = [item.dict() for item in results]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 使用例
    analyzer = BudgetAnalyzer()
    
    sample_text = """
    事業名：地域活性化推進事業
    予算額：10,000,000円
    
    事業概要：
    地域コミュニティの活性化を目的とし、以下の施策を実施する。
    1. 地域活動支援補助金の交付
    2. コミュニティスペースの整備
    3. 地域活動コーディネーターの配置
    
    KPI：
    - 地域活動参加者数：年間1000人
    - 新規コミュニティ事業：5件
    """
    
    try:
        result = analyzer.analyze_budget_text(sample_text)
        print(json.dumps(result.dict(), ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
