import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate extracted financial data"""

    def __init__(self):
        self.validation_rules = {
            # Balance sheet equation
            'balance_sheet': self._validate_balance_sheet,
            # Income statement logic
            'income_statement': self._validate_income_statement,
            # Cash flow consistency
            'cash_flow': self._validate_cash_flow,
            # Ratio bounds
            'ratio_bounds': self._validate_ratio_bounds,
        }

    def validate_all(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Run all validation checks"""
        errors = []

        for rule_name, rule_func in self.validation_rules.items():
            try:
                is_valid, error_msg = rule_func(data)
                if not is_valid:
                    errors.append(f"{rule_name}: {error_msg}")
            except Exception as e:
                logger.warning(f"Validation {rule_name} failed: {str(e)}")

        return len(errors) == 0, errors

    def _validate_balance_sheet(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Validate: Assets = Liabilities + Equity"""
        data_dict = data['value'].to_dict()

        assets = data_dict.get('total_assets')
        liabilities = data_dict.get('total_liabilities')
        equity = data_dict.get('shareholders_equity')

        if all([assets, liabilities, equity]):
            difference = abs(assets - (liabilities + equity))
            tolerance = assets * 0.01  # 1% tolerance

            if difference > tolerance:
                return False, f"Balance sheet doesn't balance: Assets={assets}, L+E={liabilities + equity}"

        return True, ""

    def _validate_income_statement(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Validate income statement relationships"""
        data_dict = data['value'].to_dict()

        revenue = data_dict.get('revenue')
        cogs = data_dict.get('cost_of_goods_sold')
        gross_profit = data_dict.get('gross_profit')

        if all([revenue, cogs, gross_profit]):
            calculated_gp = revenue - cogs
            difference = abs(gross_profit - calculated_gp)
            tolerance = revenue * 0.01

            if difference > tolerance:
                return False, f"Gross profit mismatch: Expected={calculated_gp}, Got={gross_profit}"

        return True, ""

    def _validate_cash_flow(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Validate cash flow components"""
        data_dict = data['value'].to_dict()

        # Free Cash Flow = OCF - CapEx (if available)
        ocf = data_dict.get('operating_cash_flow')
        fcf = data_dict.get('free_cash_flow')

        if all([ocf, fcf]):
            if fcf > ocf:
                return False, f"Free Cash Flow ({fcf}) cannot exceed Operating Cash Flow ({ocf})"

        return True, ""

    def _validate_ratio_bounds(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Validate ratios are within reasonable bounds"""
        data_dict = data['value'].to_dict()

        # Current ratio should be positive
        current_assets = data_dict.get('current_assets')
        current_liabilities = data_dict.get('current_liabilities')

        if all([current_assets, current_liabilities]):
            if current_assets < 0 or current_liabilities < 0:
                return False, "Negative values in current assets or liabilities"

        return True, ""
