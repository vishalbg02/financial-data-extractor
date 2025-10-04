import os
from pathlib import Path

# Base Configuration
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Financial Variables to Extract
FINANCIAL_VARIABLES = {
    # Income Statement
    "revenue": ["revenue", "sales", "total revenue", "net sales", "gross sales"],
    "cost_of_goods_sold": ["cogs", "cost of goods sold", "cost of sales"],
    "gross_profit": ["gross profit", "gross income"],
    "operating_expenses": ["operating expenses", "opex", "operating costs"],
    "operating_income": ["operating income", "ebit", "operating profit"],
    "net_income": ["net income", "net profit", "net earnings", "profit after tax"],

    # Balance Sheet
    "total_assets": ["total assets", "assets"],
    "current_assets": ["current assets"],
    "total_liabilities": ["total liabilities", "liabilities"],
    "current_liabilities": ["current liabilities"],
    "shareholders_equity": ["shareholders equity", "equity", "stockholders equity"],
    "cash": ["cash", "cash and equivalents", "cash & equivalents"],

    # Cash Flow
    "operating_cash_flow": ["operating cash flow", "cash from operations", "ocf"],
    "investing_cash_flow": ["investing cash flow", "cash from investing"],
    "financing_cash_flow": ["financing cash flow", "cash from financing"],
    "free_cash_flow": ["free cash flow", "fcf"],

    # Other Metrics
    "total_debt": ["total debt", "debt"],
    "inventory": ["inventory", "inventories"],
    "accounts_receivable": ["accounts receivable", "receivables"],
    "accounts_payable": ["accounts payable", "payables"],
}

# Financial Metrics to Calculate
FINANCIAL_METRICS = [
    "gross_profit_margin",
    "operating_profit_margin",
    "net_profit_margin",
    "return_on_assets",
    "return_on_equity",
    "current_ratio",
    "quick_ratio",
    "debt_to_equity",
    "asset_turnover",
    "inventory_turnover",
    "days_sales_outstanding",
    "earnings_per_share",
]

# Model Configuration
MODEL_CONFIG = {
    "similarity_threshold": 0.75,
    "confidence_threshold": 0.85,
    "max_fuzzy_ratio": 85,
}

# File Upload Settings
ALLOWED_EXCEL_EXTENSIONS = ['.xlsx', '.xls', '.xlsm', '.csv']
ALLOWED_PDF_EXTENSIONS = ['.pdf']
MAX_FILE_SIZE_MB = 100  # Maximum file size in megabytes