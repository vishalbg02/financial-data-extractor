import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import easyocr
import re
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Callable
from fuzzywuzzy import fuzz
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from extractors.base_extractor import BaseExtractor
from config import FINANCIAL_VARIABLES
from utils.cache_manager import get_cache_manager
from utils.performance_monitor import get_performance_monitor
from utils.optimized_ocr import OptimizedOCR

logger = logging.getLogger(__name__)


class PDFExtractor(BaseExtractor):
    """Extract financial data from PDF files using multiple methods"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.text_content = []
        self.tables = []
        # Use optimized OCR instead of direct EasyOCR
        self.ocr_engine = OptimizedOCR(use_gpu=False, enable_cache=True)
        self.cache_manager = get_cache_manager()
        self.performance_monitor = get_performance_monitor()
        self.progress_callback = None

    def set_progress_callback(self, callback: Callable[[str, int, int], None]):
        """
        Set callback for progress tracking
        
        Args:
            callback: Function(operation, current, total) to call for progress updates
        """
        self.progress_callback = callback
    
    def extract(self) -> Dict[str, Any]:
        """Extract data from PDF using hybrid approach"""
        try:
            # Check cache first
            cache_key = f"pdf_extract_{self.cache_manager._get_file_hash(self.file_path)}"
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info("Using cached PDF extraction result")
                return cached_result
            
            with self.performance_monitor.measure("PDF extraction"):
                # Method 1: Extract text using pdfplumber
                self._extract_with_pdfplumber()

                # Method 2: Extract tables
                self._extract_tables()

                # Method 3: OCR for scanned PDFs
                if not self.text_content or len(''.join(self.text_content)) < 100:
                    self._extract_with_ocr()

                # Extract financial variables
                self.extracted_data = self._extract_financial_variables()

            # Cache result
            self.cache_manager.set(cache_key, self.extracted_data)
            
            logger.info(f"Successfully extracted data from PDF")
            return self.extracted_data

        except Exception as e:
            logger.error(f"Error extracting PDF data: {str(e)}")
            raise

    def _extract_with_pdfplumber(self):
        """Extract text using pdfplumber"""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        self.text_content.append(text)
        except Exception as e:
            logger.warning(f"PDFPlumber extraction failed: {str(e)}")

    def _extract_tables(self):
        """Extract tables from PDF"""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        self.tables.extend(tables)
        except Exception as e:
            logger.warning(f"Table extraction failed: {str(e)}")

    def _extract_with_ocr(self):
        """Extract text using OCR for scanned PDFs with batch processing"""
        try:
            logger.info("Performing OCR extraction with batch processing...")
            images = convert_from_path(self.file_path)
            
            if self.progress_callback:
                self.progress_callback("OCR Processing", 0, len(images))
            
            def ocr_progress(current, total):
                if self.progress_callback:
                    self.progress_callback("OCR Processing", current, total)
            
            # Use batch OCR processing for better performance
            texts = self.ocr_engine.extract_text_batch(
                [np.array(img) for img in images],
                preprocess=True,
                progress_callback=ocr_progress
            )
            
            self.text_content.extend(texts)
            logger.info(f"OCR extraction completed for {len(images)} pages")

        except Exception as e:
            logger.warning(f"OCR extraction failed: {str(e)}")

    def _extract_financial_variables(self) -> Dict[str, Any]:
        """Extract financial variables from text and tables with parallel processing"""
        with self.performance_monitor.measure("Financial variable extraction"):
            results = {}

            # Combine all text
            full_text = ' '.join(self.text_content)

            # Use parallel processing for variable extraction
            def extract_variable(var_item):
                var_key, var_aliases = var_item
                # Try tables first (higher accuracy)
                value = self._search_in_tables(var_aliases)
                if value is not None:
                    return (var_key, {
                        "value": value,
                        "source": "table",
                        "confidence": 0.95
                    })

                # Try text extraction
                value = self._search_in_text(full_text, var_aliases)
                if value is not None:
                    return (var_key, {
                        "value": value,
                        "source": "text",
                        "confidence": 0.85
                    })
                
                return (var_key, None)
            
            # Process variables in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_var = {
                    executor.submit(extract_variable, item): item[0]
                    for item in FINANCIAL_VARIABLES.items()
                }
                
                for future in as_completed(future_to_var):
                    var_key, result = future.result()
                    if result is not None:
                        results[var_key] = result

            return results

    def _search_in_tables(self, aliases: List[str]) -> float:
        """Search for variable in extracted tables"""
        for table in self.tables:
            for row in table:
                for cell_idx, cell in enumerate(row):
                    if cell is None:
                        continue

                    cell_text = str(cell).lower().strip()

                    for alias in aliases:
                        score = fuzz.ratio(cell_text, alias.lower())

                        if score > 85:
                            # Look for number in the same row
                            for value_cell in row[cell_idx + 1:]:
                                number = self._parse_number(value_cell)
                                if number is not None:
                                    return number

        return None

    def _search_in_text(self, text: str, aliases: List[str]) -> float:
        """Search for variable in text using pattern matching"""
        for alias in aliases:
            # Create pattern: alias followed by number
            pattern = rf"{re.escape(alias)}\s*[:=]?\s*\$?\s*([\d,]+\.?\d*)\s*([KMB])?"
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                number_str = match.group(1)
                multiplier_str = match.group(2)

                try:
                    number = float(number_str.replace(',', ''))

                    # Apply multiplier
                    if multiplier_str:
                        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
                        number *= multipliers.get(multiplier_str.upper(), 1)

                    return number
                except ValueError:
                    continue

        return None

    def _parse_number(self, value: Any) -> float:
        """Parse numeric value"""
        try:
            if value is None:
                return None

            str_value = str(value).strip()
            str_value = str_value.replace(',', '').replace('$', '').replace('€', '')
            str_value = str_value.replace('(', '-').replace(')', '')

            # Handle multipliers
            multiplier = 1
            if 'k' in str_value.lower():
                multiplier = 1000
                str_value = str_value.lower().replace('k', '')
            elif 'm' in str_value.lower():
                multiplier = 1000000
                str_value = str_value.lower().replace('m', '')
            elif 'b' in str_value.lower():
                multiplier = 1000000000
                str_value = str_value.lower().replace('b', '')

            number = float(str_value) * multiplier
            return number

        except (ValueError, TypeError):
            return None

    def validate(self) -> bool:
        """Validate extracted data"""
        return bool(self.extracted_data)

    def extract_full_text(self) -> str:
        """
        Extract full text content for RAG/QA purposes.
        
        Returns:
            Full text content of the PDF
        """
        # If text_content is already populated from extraction, use it
        if self.text_content:
            return '\n\n'.join(self.text_content)
        
        # Otherwise, extract text
        try:
            text_parts = []
            
            # Extract text using pdfplumber
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            # Add table content as text
            if self.tables:
                for table in self.tables:
                    table_text = '\n'.join([' | '.join([str(cell) for cell in row if cell]) for row in table])
                    text_parts.append(f"Table:\n{table_text}")
            
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            logger.error(f"Error extracting full text from PDF: {e}")
            return ""
