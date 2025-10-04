import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors.excel_extractor import ExcelExtractor
from extractors.pdf_extractor import PDFExtractor
import pandas as pd


class TestExcelExtractor(unittest.TestCase):

    def test_parse_number(self):
        """Test number parsing"""
        extractor = ExcelExtractor("dummy.xlsx")

        # Test basic number
        self.assertEqual(extractor._parse_number("1000"), 1000.0)

        # Test with comma
        self.assertEqual(extractor._parse_number("1,000"), 1000.0)

        # Test with dollar sign
        self.assertEqual(extractor._parse_number("$1,000"), 1000.0)

        # Test with K
        self.assertEqual(extractor._parse_number("10K"), 10000.0)

        # Test with M
        self.assertEqual(extractor._parse_number("5M"), 5000000.0)

    def test_find_adjacent_number(self):
        """Test finding adjacent numbers"""
        extractor = ExcelExtractor("dummy.xlsx")

        # Create test DataFrame
        df = pd.DataFrame([
            ['Revenue', 1000000],
            ['Expenses', 500000]
        ])

        # Test finding number to the right
        value = extractor._find_adjacent_number(df, 0, 0)
        self.assertEqual(value, 1000000.0)


class TestPDFExtractor(unittest.TestCase):

    def test_parse_number(self):
        """Test number parsing in PDF extractor"""
        extractor = PDFExtractor("dummy.pdf")

        # Test basic scenarios
        self.assertEqual(extractor._parse_number("1000"), 1000.0)
        self.assertEqual(extractor._parse_number("$1,000.50"), 1000.5)
        self.assertIsNone(extractor._parse_number("abc"))


if __name__ == '__main__':
    unittest.main()
