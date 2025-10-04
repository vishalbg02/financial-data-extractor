import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class FinancialCalculator:
    """Calculate financial metrics from normalized data"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.metrics = {}

    def calculate_all_metrics(self) -> Dict[str, float]:
        """Calculate all financial metrics"""
        try:
            # Convert DataFrame to dict for easier access
            data_dict = self.data["value"].to_dict()

            # Profitability Ratios
            self.metrics["gross_profit_margin"] = self._gross_profit_margin(data_dict)
            self.metrics["operating_profit_margin"] = self._operating_profit_margin(data_dict)
            self.metrics["net_profit_margin"] = self._net_profit_margin(data_dict)
            self.metrics["return_on_assets"] = self._return_on_assets(data_dict)
            self.metrics["return_on_equity"] = self._return_on_equity(data_dict)
            self.metrics["return_on_invested_capital"] = self._return_on_invested_capital(data_dict)

            # Liquidity Ratios
            self.metrics["current_ratio"] = self._current_ratio(data_dict)
            self.metrics["quick_ratio"] = self._quick_ratio(data_dict)
            self.metrics["cash_ratio"] = self._cash_ratio(data_dict)
            self.metrics["working_capital_ratio"] = self._working_capital_ratio(data_dict)

            # Leverage Ratios
            self.metrics["debt_to_equity"] = self._debt_to_equity(data_dict)
            self.metrics["debt_ratio"] = self._debt_ratio(data_dict)

            # Efficiency Ratios
            self.metrics["asset_turnover"] = self._asset_turnover(data_dict)
            self.metrics["inventory_turnover"] = self._inventory_turnover(data_dict)
            self.metrics["receivables_turnover"] = self._receivables_turnover(data_dict)

            # Remove None values
            self.metrics = {k: v for k, v in self.metrics.items() if v is not None}

            logger.info(f"Calculated {len(self.metrics)} financial metrics")
            return self.metrics

        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            raise

    def _get_value(self, data_dict: Dict, key: str, default=None):
        """Safely get value from data dictionary"""
        return data_dict.get(key, default)

    def _gross_profit_margin(self, data: Dict) -> float:
        """(Revenue - COGS) / Revenue * 100"""
        revenue = self._get_value(data, "revenue")
        cogs = self._get_value(data, "cost_of_goods_sold")

        if revenue and revenue != 0:
            gross_profit = revenue - (cogs or 0)
            return round((gross_profit / revenue) * 100, 2)
        return None

    def _operating_profit_margin(self, data: Dict) -> float:
        """Operating Income / Revenue * 100"""
        operating_income = self._get_value(data, "operating_income")
        revenue = self._get_value(data, "revenue")

        if revenue and revenue != 0 and operating_income:
            return round((operating_income / revenue) * 100, 2)
        return None

    def _net_profit_margin(self, data: Dict) -> float:
        """Net Income / Revenue * 100"""
        net_income = self._get_value(data, "net_income")
        revenue = self._get_value(data, "revenue")

        if revenue and revenue != 0 and net_income:
            return round((net_income / revenue) * 100, 2)
        return None

    def _return_on_assets(self, data: Dict) -> float:
        """Net Income / Total Assets * 100"""
        net_income = self._get_value(data, "net_income")
        total_assets = self._get_value(data, "total_assets")

        if total_assets and total_assets != 0 and net_income:
            return round((net_income / total_assets) * 100, 2)
        return None

    def _return_on_equity(self, data: Dict) -> float:
        """Net Income / Shareholders Equity * 100"""
        net_income = self._get_value(data, "net_income")
        equity = self._get_value(data, "shareholders_equity")

        if equity and equity != 0 and net_income:
            return round((net_income / equity) * 100, 2)
        return None

    def _current_ratio(self, data: Dict) -> float:
        """Current Assets / Current Liabilities"""
        current_assets = self._get_value(data, "current_assets")
        current_liabilities = self._get_value(data, "current_liabilities")

        if current_liabilities and current_liabilities != 0 and current_assets:
            return round(current_assets / current_liabilities, 2)
        return None

    def _quick_ratio(self, data: Dict) -> float:
        """(Current Assets - Inventory) / Current Liabilities"""
        current_assets = self._get_value(data, "current_assets")
        inventory = self._get_value(data, "inventory", 0)
        current_liabilities = self._get_value(data, "current_liabilities")

        if current_liabilities and current_liabilities != 0 and current_assets:
            return round((current_assets - inventory) / current_liabilities, 2)
        return None

    def _debt_to_equity(self, data: Dict) -> float:
        """Total Debt / Shareholders Equity"""
        total_debt = self._get_value(data, "total_debt")
        equity = self._get_value(data, "shareholders_equity")

        if equity and equity != 0 and total_debt:
            return round(total_debt / equity, 2)
        return None

    def _asset_turnover(self, data: Dict) -> float:
        """Revenue / Total Assets"""
        revenue = self._get_value(data, "revenue")
        total_assets = self._get_value(data, "total_assets")

        if total_assets and total_assets != 0 and revenue:
            return round(revenue / total_assets, 2)
        return None

    def _inventory_turnover(self, data: Dict) -> float:
        """COGS / Average Inventory"""
        cogs = self._get_value(data, "cost_of_goods_sold")
        inventory = self._get_value(data, "inventory")

        if inventory and inventory != 0 and cogs:
            return round(cogs / inventory, 2)
        return None

    def _return_on_invested_capital(self, data: Dict) -> float:
        """Net Operating Profit After Tax / Invested Capital * 100"""
        operating_income = self._get_value(data, "operating_income")
        total_assets = self._get_value(data, "total_assets")
        current_liabilities = self._get_value(data, "current_liabilities")
        
        if operating_income and total_assets and current_liabilities:
            # Simplified ROIC calculation
            invested_capital = total_assets - current_liabilities
            if invested_capital != 0:
                # Approximate NOPAT as operating income * 0.75 (assuming 25% tax rate)
                nopat = operating_income * 0.75
                return round((nopat / invested_capital) * 100, 2)
        return None

    def _cash_ratio(self, data: Dict) -> float:
        """Cash / Current Liabilities"""
        cash = self._get_value(data, "cash")
        current_liabilities = self._get_value(data, "current_liabilities")

        if current_liabilities and current_liabilities != 0 and cash:
            return round(cash / current_liabilities, 2)
        return None

    def _working_capital_ratio(self, data: Dict) -> float:
        """(Current Assets - Current Liabilities) / Total Assets"""
        current_assets = self._get_value(data, "current_assets")
        current_liabilities = self._get_value(data, "current_liabilities")
        total_assets = self._get_value(data, "total_assets")

        if total_assets and total_assets != 0 and current_assets and current_liabilities:
            working_capital = current_assets - current_liabilities
            return round(working_capital / total_assets, 2)
        return None

    def _debt_ratio(self, data: Dict) -> float:
        """Total Debt / Total Assets"""
        total_debt = self._get_value(data, "total_debt")
        total_assets = self._get_value(data, "total_assets")

        if total_assets and total_assets != 0 and total_debt:
            return round(total_debt / total_assets, 2)
        return None

    def _receivables_turnover(self, data: Dict) -> float:
        """Revenue / Average Receivables"""
        revenue = self._get_value(data, "revenue")
        receivables = self._get_value(data, "receivables")

        if receivables and receivables != 0 and revenue:
            return round(revenue / receivables, 2)
        return None

    def get_metrics_dataframe(self) -> pd.DataFrame:
        """Return metrics as a DataFrame"""
        df = pd.DataFrame([self.metrics]).T
        df.columns = ["value"]
        df.index.name = "metric"
        return df
