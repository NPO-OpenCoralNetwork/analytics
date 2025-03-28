import os
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from pdf_processors.pdf_extractor import PDFExtractor
from langchain_processors.budget_analyzer import BudgetAnalyzer
from data_transformers.db_connector import DatabaseConnector

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/budget_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BudgetProcessor:
    """予算文書処理の統合クラス"""
    
    def __init__(self, pdf_dir: str):
        """
        初期化
        
        Args:
            pdf_dir: PDF文書が格納されているディレクトリパス
        """
        self.pdf_dir = pdf_dir
        self.pdf_extractor = PDFExtractor(pdf_dir)
        self.budget_analyzer = BudgetAnalyzer()
        self.db_connector = DatabaseConnector()
        
        # 処理結果の保存ディレクトリ
        self.output_dir = Path("output") / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_documents(self) -> List[Dict]:
        """
        文書の一括処理を実行
        
        Returns:
            List[Dict]: 処理結果のリスト
        """
        logger.info("Starting document processing...")
        
        try:
            # PDFの処理
            logger.info("Extracting text from PDFs...")
            pdf_results = self.pdf_extractor.process_pdf_directory()
            logger.info(f"Processed {len(pdf_results)} PDF documents")
            
            # 予算データの分析
            logger.info("Analyzing budget data...")
            analyzed_results = []
            for pdf_result in pdf_results:
                try:
                    budget_items = self.budget_analyzer.analyze_budget_document(pdf_result)
                    analyzed_results.extend(budget_items)
                    logger.info(f"Analyzed {len(budget_items)} budget items from {pdf_result['filename']}")
                except Exception as e:
                    logger.error(f"Error analyzing {pdf_result['filename']}: {str(e)}")
                    continue
            
            # データベースへの保存
            logger.info("Saving results to database...")
            project_ids = self.db_connector.save_budget_items([item.dict() for item in analyzed_results])
            logger.info(f"Saved {len(project_ids)} budget items to database")
            
            # 結果をJSONとして保存
            results_file = self.output_dir / "analysis_results.json"
            self.budget_analyzer.save_results(analyzed_results, str(results_file))
            logger.info(f"Saved analysis results to {results_file}")
            
            # Notionとの同期
            logger.info("Syncing with Notion...")
            notion_database_id = os.getenv("NOTION_DATABASE_ID")
            if notion_database_id:
                self.db_connector.sync_to_notion(notion_database_id)
                logger.info("Successfully synced with Notion")
            else:
                logger.warning("Notion database ID not provided, skipping sync")
            
            return analyzed_results
            
        except Exception as e:
            logger.error(f"Error in document processing: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description="予算文書処理スクリプト")
    parser.add_argument("--pdf-dir", required=True, help="処理対象のPDFが格納されているディレクトリ")
    parser.add_argument("--log-level", default="INFO", help="ログレベル（DEBUG/INFO/WARNING/ERROR）")
    args = parser.parse_args()
    
    # ログレベルの設定
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    try:
        # 処理の実行
        processor = BudgetProcessor(args.pdf_dir)
        results = processor.process_documents()
        
        logger.info(f"Successfully processed {len(results)} budget items")
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
