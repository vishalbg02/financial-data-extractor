import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import easyocr
import re
import numpy as np
from typing import Dict, Any, List, Tuple
from fuzzywuzzy import fuzz
import logging

from extractors.base_extractor import BaseExtractor
from config import FINANCIAL_VARIABLES

logger = logging.getLogger(__name__)


class PDFExtractor(BaseExtractor):
    """Extract financial data from PDF files using multiple methods"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.text_content = []
        self.tables = []
        self.ocr_reader = easyocr.Reader(['en'])

    def extract(self) -> Dict[str, Any]:
        """Extract data from PDF using hybrid approach"""
        try:
            # Method 1: Extract text using pdfplumber
            self._extract_with_pdfplumber()

            # Method 2: Extract tables
            self._extract_tables()

            # Method 3: OCR for scanned PDFs
            if not self.text_content or len(self.text_content) < 100:
                self._extract_with_ocr()

            # Extract financial variables
            self.extracted_data = self._extract_financial_variables()

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
        """Extract text using OCR for scanned PDFs"""
        try:
            logger.info("Performing OCR extraction...")
            images = convert_from_path(self.file_path)

            for img in images:
                # Use EasyOCR
                result = self.ocr_reader.readtext(np.array(img))
                text = ' '.join([item[1] for item in result])
                self.text_content.append(text)

        except Exception as e:
            logger.warning(f"OCR extraction failed: {str(e)}")

    def _extract_financial_variables(self) -> Dict[str, Any]:
        """Extract financial variables from text and tables"""
        results = {}

        # Combine all text
        full_text = ' '.join(self.text_content)

        # Extract from tables first (higher accuracy)
        for var_key, var_aliases in FINANCIAL_VARIABLES.items():
            # Try tables first
            value = self._search_in_tables(var_aliases)
            if value is not None:
                results[var_key] = {
                    "value": value,
                    "source": "table",
                    "confidence": 0.95
                }
                continue

            # Try text extraction
            value = self._search_in_text(full_text, var_aliases)
            if value is not None:
                results[var_key] = {
                    "value": value,
                    "source": "text",
                    "confidence": 0.85
                }

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
