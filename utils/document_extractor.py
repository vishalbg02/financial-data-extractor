"""
Document text extraction for RAG processing
"""
import logging
from pathlib import Path
from typing import Optional, List, Dict
import pandas as pd

logger = logging.getLogger(__name__)


class DocumentTextExtractor:
    """Extract text from various document formats for RAG"""
    
    @staticmethod
    def extract_from_excel(file_path: str) -> Dict[str, str]:
        """
        Extract text from Excel file
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dict with sheet names as keys and text content as values
        """
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            text_content = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Convert DataFrame to text representation
                text_parts = []
                
                # Add column headers
                text_parts.append("Columns: " + ", ".join(str(col) for col in df.columns))
                
                # Add rows as text
                for idx, row in df.iterrows():
                    row_text = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
                    if row_text:
                        text_parts.append(row_text)
                
                text_content[sheet_name] = "\n".join(text_parts)
            
            logger.info(f"Extracted text from {len(text_content)} sheets in Excel file")
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text from Excel: {e}")
            return {}
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            import PyPDF2
            import pdfplumber
            
            text_parts = []
            
            # Try pdfplumber first (better for tables)
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
                        
                        # Extract tables
                        tables = page.extract_tables()
                        for table_num, table in enumerate(tables):
                            if table:
                                table_text = f"\n[Table {table_num + 1}]\n"
                                for row in table:
                                    table_text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                                text_parts.append(table_text)
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2")
                
                # Fallback to PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
            
            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    @staticmethod
    def extract_from_csv(file_path: str) -> str:
        """
        Extract text from CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Extracted text content
        """
        try:
            df = pd.read_csv(file_path)
            
            text_parts = []
            
            # Add column headers
            text_parts.append("Columns: " + ", ".join(str(col) for col in df.columns))
            
            # Add rows as text
            for idx, row in df.iterrows():
                row_text = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
                if row_text:
                    text_parts.append(row_text)
            
            full_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from CSV")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from CSV: {e}")
            return ""
    
    @staticmethod
    def extract_from_file(file_path: str) -> Dict[str, str]:
        """
        Extract text from a file (auto-detect format)
        
        Args:
            file_path: Path to file
            
        Returns:
            Dict with extracted text (key is section/sheet name)
        """
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()
        
        result = {}
        
        if file_ext in ['.xlsx', '.xls', '.xlsm']:
            result = DocumentTextExtractor.extract_from_excel(str(file_path))
        elif file_ext == '.csv':
            result['data'] = DocumentTextExtractor.extract_from_csv(str(file_path))
        elif file_ext == '.pdf':
            result['document'] = DocumentTextExtractor.extract_from_pdf(str(file_path))
        else:
            logger.warning(f"Unsupported file format: {file_ext}")
        
        return result
