"""Advanced analytics utilities for financial data analysis."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class FinancialAnalytics:
    """Advanced analytics for financial data."""

    @staticmethod
    def detect_anomalies(metrics: Dict[str, float], thresholds: Dict[str, Tuple[float, float]] = None) -> List[Dict[str, Any]]:
        """
        Detect anomalies in financial metrics.
        
        Args:
            metrics: Dictionary of financial metrics
            thresholds: Optional custom thresholds (min, max) for each metric
            
        Returns:
            List of detected anomalies with explanations
        """
        anomalies = []
        
        # Default thresholds for common metrics
        default_thresholds = {
            'current_ratio': (1.0, 3.0),  # Below 1.0 is concerning, above 3.0 may indicate inefficiency
            'quick_ratio': (0.5, 2.0),
            'debt_to_equity': (0.0, 2.0),  # Above 2.0 is high leverage
            'debt_ratio': (0.0, 0.6),  # Above 0.6 is concerning
            'gross_profit_margin': (20.0, 80.0),  # In percentage
            'net_profit_margin': (5.0, 50.0),
            'return_on_assets': (1.0, 30.0),
            'return_on_equity': (5.0, 40.0),
        }
        
        thresholds = thresholds or default_thresholds
        
        for metric_name, value in metrics.items():
            if metric_name in thresholds:
                min_val, max_val = thresholds[metric_name]
                
                if value < min_val:
                    severity = "high" if value < min_val * 0.5 else "medium"
                    anomalies.append({
                        'metric': metric_name,
                        'value': value,
                        'type': 'below_threshold',
                        'severity': severity,
                        'threshold': min_val,
                        'message': f"{metric_name.replace('_', ' ').title()} is below recommended minimum ({min_val})"
                    })
                elif value > max_val:
                    severity = "high" if value > max_val * 1.5 else "medium"
                    anomalies.append({
                        'metric': metric_name,
                        'value': value,
                        'type': 'above_threshold',
                        'severity': severity,
                        'threshold': max_val,
                        'message': f"{metric_name.replace('_', ' ').title()} is above recommended maximum ({max_val})"
                    })
        
        return anomalies

    @staticmethod
    def calculate_health_score(metrics: Dict[str, float]) -> Tuple[float, str]:
        """
        Calculate overall financial health score.
        
        Args:
            metrics: Dictionary of financial metrics
            
        Returns:
            Tuple of (score, rating) where score is 0-100 and rating is text
        """
        score = 0
        weight_sum = 0
        
        # Scoring weights for different metrics
        scoring_rules = {
            'current_ratio': {'weight': 10, 'ideal': 1.5, 'tolerance': 0.5},
            'quick_ratio': {'weight': 8, 'ideal': 1.0, 'tolerance': 0.3},
            'debt_to_equity': {'weight': 12, 'ideal': 0.5, 'tolerance': 0.5, 'inverse': True},
            'gross_profit_margin': {'weight': 15, 'ideal': 40.0, 'tolerance': 20.0},
            'net_profit_margin': {'weight': 15, 'ideal': 15.0, 'tolerance': 10.0},
            'return_on_assets': {'weight': 12, 'ideal': 10.0, 'tolerance': 5.0},
            'return_on_equity': {'weight': 15, 'ideal': 15.0, 'tolerance': 10.0},
            'asset_turnover': {'weight': 8, 'ideal': 1.5, 'tolerance': 0.5},
            'cash_ratio': {'weight': 5, 'ideal': 0.5, 'tolerance': 0.3},
        }
        
        for metric_name, rules in scoring_rules.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                ideal = rules['ideal']
                tolerance = rules['tolerance']
                weight = rules['weight']
                inverse = rules.get('inverse', False)
                
                # Calculate how close the value is to ideal
                if inverse:
                    # For metrics where lower is better (like debt ratios)
                    diff = max(0, value - ideal)
                else:
                    diff = abs(value - ideal)
                
                # Score this metric (100 = ideal, 0 = far from ideal)
                metric_score = max(0, 100 - (diff / tolerance * 100))
                metric_score = min(100, metric_score)  # Cap at 100
                
                score += metric_score * weight
                weight_sum += weight
        
        if weight_sum > 0:
            final_score = score / weight_sum
        else:
            final_score = 0
        
        # Determine rating
        if final_score >= 80:
            rating = "Excellent"
        elif final_score >= 65:
            rating = "Good"
        elif final_score >= 50:
            rating = "Fair"
        elif final_score >= 35:
            rating = "Poor"
        else:
            rating = "Critical"
        
        return round(final_score, 1), rating

    @staticmethod
    def generate_insights(metrics: Dict[str, float], normalized_data: pd.DataFrame) -> List[str]:
        """
        Generate actionable insights from financial metrics.
        
        Args:
            metrics: Dictionary of financial metrics
            normalized_data: DataFrame of normalized financial data
            
        Returns:
            List of insight strings
        """
        insights = []
        
        # Profitability insights
        if 'gross_profit_margin' in metrics and 'net_profit_margin' in metrics:
            gpm = metrics['gross_profit_margin']
            npm = metrics['net_profit_margin']
            
            if gpm > 40 and npm < 10:
                insights.append("🔍 High gross margin but low net margin suggests high operating expenses")
            elif gpm > 50:
                insights.append("✅ Strong gross profit margin indicates good pricing power")
            elif gpm < 20:
                insights.append("⚠️ Low gross profit margin may indicate pricing pressure or high COGS")
        
        # Liquidity insights
        if 'current_ratio' in metrics:
            cr = metrics['current_ratio']
            if cr < 1.0:
                insights.append("🚨 Current ratio below 1.0 indicates potential liquidity issues")
            elif cr > 3.0:
                insights.append("💡 High current ratio may indicate inefficient use of current assets")
            else:
                insights.append("✅ Current ratio is within healthy range")
        
        # Leverage insights
        if 'debt_to_equity' in metrics:
            dte = metrics['debt_to_equity']
            if dte > 2.0:
                insights.append("⚠️ High debt-to-equity ratio indicates significant financial leverage")
            elif dte < 0.5:
                insights.append("✅ Conservative capital structure with low debt levels")
        
        # Efficiency insights
        if 'asset_turnover' in metrics:
            at = metrics['asset_turnover']
            if at < 0.5:
                insights.append("💡 Low asset turnover suggests underutilized assets")
            elif at > 2.0:
                insights.append("✅ High asset turnover indicates efficient asset utilization")
        
        # Investment insights
        if 'return_on_equity' in metrics:
            roe = metrics['return_on_equity']
            if roe > 20:
                insights.append("🌟 Excellent return on equity indicates strong profitability")
            elif roe < 5:
                insights.append("⚠️ Low return on equity may concern investors")
        
        # Cash position insights
        if 'cash_ratio' in metrics:
            cash_r = metrics['cash_ratio']
            if cash_r > 1.0:
                insights.append("💰 Strong cash position provides financial flexibility")
            elif cash_r < 0.2:
                insights.append("⚠️ Low cash ratio may limit ability to meet short-term obligations")
        
        return insights

    @staticmethod
    def get_metric_trend(metric_value: float, metric_name: str) -> str:
        """
        Get trend indicator for a metric.
        
        Args:
            metric_value: Current value of the metric
            metric_name: Name of the metric
            
        Returns:
            Emoji trend indicator
        """
        # This is simplified - in production, you'd compare with historical data
        # For now, we'll use threshold-based indicators
        
        positive_metrics = ['current_ratio', 'quick_ratio', 'gross_profit_margin', 
                           'net_profit_margin', 'return_on_assets', 'return_on_equity',
                           'asset_turnover', 'cash_ratio']
        
        negative_metrics = ['debt_to_equity', 'debt_ratio']
        
        if metric_name in positive_metrics:
            # For positive metrics, categorize by value ranges
            thresholds = {
                'current_ratio': 1.5,
                'quick_ratio': 1.0,
                'gross_profit_margin': 30.0,
                'net_profit_margin': 10.0,
                'return_on_assets': 8.0,
                'return_on_equity': 15.0,
                'asset_turnover': 1.0,
                'cash_ratio': 0.5,
            }
            
            threshold = thresholds.get(metric_name, 0)
            if metric_value >= threshold:
                return "📈"  # Positive
            else:
                return "📉"  # Below threshold
        
        elif metric_name in negative_metrics:
            # For negative metrics, lower is better
            thresholds = {
                'debt_to_equity': 1.0,
                'debt_ratio': 0.5,
            }
            
            threshold = thresholds.get(metric_name, 1.0)
            if metric_value <= threshold:
                return "📈"  # Good (low debt)
            else:
                return "📉"  # High debt
        
        return "➡️"  # Neutral

    @staticmethod
    def generate_summary_report(metrics: Dict[str, float], normalized_data: pd.DataFrame) -> str:
        """
        Generate a comprehensive summary report.
        
        Args:
            metrics: Dictionary of financial metrics
            normalized_data: DataFrame of normalized financial data
            
        Returns:
            Formatted summary report string
        """
        report_parts = []
        
        # Header
        report_parts.append("# Financial Analysis Summary Report\n")
        
        # Health score
        score, rating = FinancialAnalytics.calculate_health_score(metrics)
        report_parts.append(f"## Overall Financial Health: {rating} ({score}/100)\n")
        
        # Key metrics
        report_parts.append("## Key Financial Metrics\n")
        
        if 'revenue' in normalized_data.index:
            revenue = normalized_data.loc['revenue', 'value']
            report_parts.append(f"- **Revenue**: ${revenue:,.2f}")
        
        if 'net_income' in normalized_data.index:
            net_income = normalized_data.loc['net_income', 'value']
            report_parts.append(f"- **Net Income**: ${net_income:,.2f}")
        
        if 'total_assets' in normalized_data.index:
            assets = normalized_data.loc['total_assets', 'value']
            report_parts.append(f"- **Total Assets**: ${assets:,.2f}")
        
        report_parts.append("")
        
        # Insights
        insights = FinancialAnalytics.generate_insights(metrics, normalized_data)
        if insights:
            report_parts.append("## Key Insights\n")
            for insight in insights:
                report_parts.append(f"- {insight}")
            report_parts.append("")
        
        # Anomalies
        anomalies = FinancialAnalytics.detect_anomalies(metrics)
        if anomalies:
            report_parts.append("## Detected Anomalies\n")
            for anomaly in anomalies:
                severity_icon = "🚨" if anomaly['severity'] == 'high' else "⚠️"
                report_parts.append(f"- {severity_icon} {anomaly['message']}")
            report_parts.append("")
        
        return "\n".join(report_parts)
