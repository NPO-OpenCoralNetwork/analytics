import os
from typing import Dict, List
from pypdf import PdfReader
from datetime import datetime

class PDFExtractor:
    def __init__(self, pdf_dir: str):
        """
        PDFデータ抽出クラスの初期化
        
        Args:
            pdf_dir (str): PDF文書が格納されているディレクトリパス
        """
        self.pdf_dir = pdf_dir

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        PDFファイルからテキストを抽出
        
        Args:
            pdf_path (str): PDFファイルのパス
            
        Returns:
            str: 抽出されたテキスト
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {str(e)}")
            return ""

    def extract_metadata(self, pdf_path: str) -> Dict:
        """
        PDFファイルのメタデータを抽出
        
        Args:
            pdf_path (str): PDFファイルのパス
            
        Returns:
            Dict: メタデータ情報
        """
        try:
            reader = PdfReader(pdf_path)
            metadata = reader.metadata
            return {
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "creation_date": metadata.get("/CreationDate", ""),
                "modification_date": metadata.get("/ModDate", ""),
                "file_size": os.path.getsize(pdf_path),
                "pages": len(reader.pages)
            }
        except Exception as e:
            print(f"Error extracting metadata from {pdf_path}: {str(e)}")
            return {}

    def process_pdf_directory(self) -> List[Dict]:
        """
        指定されたディレクトリ内の全PDFファイルを処理
        
        Returns:
            List[Dict]: 処理結果のリスト
        """
        results = []
        for filename in os.listdir(self.pdf_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(self.pdf_dir, filename)
                try:
                    result = {
                        "filename": filename,
                        "path": pdf_path,
                        "metadata": self.extract_metadata(pdf_path),
                        "text": self.extract_text_from_pdf(pdf_path),
                        "processed_at": datetime.now().isoformat()
                    }
                    results.append(result)
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    continue
        return results

    def get_text_by_page(self, pdf_path: str) -> List[str]:
        """
        PDFファイルのテキストをページ単位で抽出
        
        Args:
            pdf_path (str): PDFファイルのパス
            
        Returns:
            List[str]: ページごとのテキストのリスト
        """
        try:
            reader = PdfReader(pdf_path)
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text())
            return pages
        except Exception as e:
            print(f"Error extracting pages from {pdf_path}: {str(e)}")
            return []

if __name__ == "__main__":
    # 使用例
    pdf_dir = "path/to/pdf/directory"
    extractor = PDFExtractor(pdf_dir)
    
    # 単一のPDFファイルを処理
    pdf_path = "example.pdf"
    text = extractor.extract_text_from_pdf(pdf_path)
    metadata = extractor.extract_metadata(pdf_path)
    
    print(f"Extracted text length: {len(text)}")
    print(f"Metadata: {metadata}")
