import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import re
from fuzzywuzzy import fuzz
import logging

from extractors.base_extractor import BaseExtractor
from config import FINANCIAL_VARIABLES

logger = logging.getLogger(__name__)


class ExcelExtractor(BaseExtractor):
    """Extract financial data from Excel files"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.sheets = {}

    def extract(self) -> Dict[str, Any]:
        """Extract data from Excel file"""
        try:
            # Read all sheets using context manager
            with pd.ExcelFile(self.file_path) as excel_file:
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                    self.sheets[sheet_name] = df.copy()  # Create a copy to ensure file handle is released

            # Extract financial variables
            self.extracted_data = self._extract_financial_variables()

            logger.info(f"Successfully extracted data from {len(self.sheets)} sheets")
            return self.extracted_data

        except Exception as e:
            logger.error(f"Error extracting Excel data: {str(e)}")
            raise
        finally:
            # Explicitly clear any remaining references
            for sheet_name in list(self.sheets.keys()):
                del self.sheets[sheet_name]
            self.sheets.clear()

    def _extract_financial_variables(self) -> Dict[str, Any]:
        """Extract financial variables from all sheets"""
        results = {}

        for sheet_name, df in self.sheets.items():
            logger.info(f"Processing sheet: {sheet_name}")

            for var_key, var_aliases in FINANCIAL_VARIABLES.items():
                if var_key not in results:
                    # Search for variable in this sheet
                    value = self._search_variable(df, var_aliases)
                    if value is not None:
                        results[var_key] = {
                            "value": value,
                            "source_sheet": sheet_name,
                            "confidence": self._calculate_confidence(var_aliases, df)
                        }

        return results

    def _search_variable(self, df: pd.DataFrame, aliases: List[str]) -> float:
        """Search for a variable in the dataframe using fuzzy matching"""
        best_match_score = 0
        best_value = None

        for row_idx in range(len(df)):
            for col_idx in range(len(df.columns)):
                cell_value = str(df.iloc[row_idx, col_idx]).lower().strip()

                for alias in aliases:
                    # Fuzzy string matching
                    score = fuzz.ratio(cell_value, alias.lower())

                    if score > 85 and score > best_match_score:
                        # Look for numeric value in adjacent cells
                        numeric_value = self._find_adjacent_number(df, row_idx, col_idx)
                        if numeric_value is not None:
                            best_match_score = score
                            best_value = numeric_value

        return best_value

    def _find_adjacent_number(self, df: pd.DataFrame, row: int, col: int) -> float:
        """Find numeric value adjacent to the matched label"""
        # Check right
        if col + 1 < len(df.columns):
            value = self._parse_number(df.iloc[row, col + 1])
            if value is not None:
                return value

        # Check below
        if row + 1 < len(df):
            value = self._parse_number(df.iloc[row + 1, col])
            if value is not None:
                return value

        # Check diagonal (down-right)
        if row + 1 < len(df) and col + 1 < len(df.columns):
            value = self._parse_number(df.iloc[row + 1, col + 1])
            if value is not None:
                return value

        return None

    def _parse_number(self, value: Any) -> float:
        """Parse numeric value from cell"""
        try:
            if pd.isna(value):
                return None

            # Convert to string and clean
            str_value = str(value).strip()

            # Remove common formatting
            str_value = str_value.replace(',', '').replace('$', '').replace('€', '')
            str_value = str_value.replace('(', '-').replace(')', '')
            str_value = str_value.replace('%', '')

            # Handle thousands/millions notation
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

            # Try to convert to float
            number = float(str_value) * multiplier
            return number

        except (ValueError, TypeError):
            return None

    def _calculate_confidence(self, aliases: List[str], df: pd.DataFrame) -> float:
        """Calculate confidence score for extraction"""
        # This is a simplified confidence calculation
        # In production, you'd use more sophisticated methods
        return 0.9

    def validate(self) -> bool:
        """Validate extracted data"""
        if not self.extracted_data:
            return False

        # Check if we extracted at least some key variables
        key_variables = ['revenue', 'net_income', 'total_assets']
        found_count = sum(1 for var in key_variables if var in self.extracted_data)

        return found_count >= 1

    def extract_full_text(self) -> str:
        """
        Extract full text content for RAG/QA purposes.
        
        Returns:
            Full text content of the Excel file
        """
        if not self.sheets:
            # Need to load the file first
            try:
                self.sheets = pd.read_excel(self.file_path, sheet_name=None)
            except Exception as e:
                logger.error(f"Error loading Excel file: {e}")
                return ""
        
        text_parts = []
        
        for sheet_name, df in self.sheets.items():
            text_parts.append(f"Sheet: {sheet_name}")
            
            # Convert dataframe to text representation
            # Include headers and data
            for col in df.columns:
                text_parts.append(f"Column: {col}")
            
            # Convert rows to text
            for idx, row in df.iterrows():
                row_text = ' | '.join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                if row_text:
                    text_parts.append(row_text)
            
            text_parts.append("")  # Blank line between sheets
        
        return '\n'.join(text_parts)
