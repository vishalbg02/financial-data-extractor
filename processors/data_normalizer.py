import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalize and combine data from multiple sources"""

    def __init__(self):
        self.normalized_data = {}

    def normalize(self, extracted_data_list: List[Dict[str, Any]]) -> pd.DataFrame:
        """Normalize data from multiple sources"""
        try:
            # Combine data from all sources
            combined_data = self._combine_sources(extracted_data_list)

            # Resolve conflicts
            resolved_data = self._resolve_conflicts(combined_data)

            # Convert to DataFrame
            df = self._to_dataframe(resolved_data)

            # Clean and standardize
            df = self._clean_data(df)

            logger.info(f"Normalized {len(df)} financial variables")
            return df

        except Exception as e:
            logger.error(f"Error normalizing data: {str(e)}")
            raise

    def _combine_sources(self, extracted_data_list: List[Dict[str, Any]]) -> Dict[str, List]:
        """Combine data from multiple sources"""
        combined = {}

        for source_idx, source_data in enumerate(extracted_data_list):
            for var_key, var_info in source_data.items():
                if var_key not in combined:
                    combined[var_key] = []

                combined[var_key].append({
                    "value": var_info.get("value"),
                    "confidence": var_info.get("confidence", 0.5),
                    "source_index": source_idx,
                    "source_type": var_info.get("source", "unknown")
                })

        return combined

    def _resolve_conflicts(self, combined_data: Dict[str, List]) -> Dict[str, Any]:
        """Resolve conflicts when multiple sources provide different values"""
        resolved = {}

        for var_key, values in combined_data.items():
            if len(values) == 1:
                # Only one source, use it directly
                resolved[var_key] = values[0]["value"]
            else:
                # Multiple sources - use weighted average or highest confidence
                resolved[var_key] = self._resolve_multi_value(values)

        return resolved

    def _resolve_multi_value(self, values: List[Dict]) -> float:
        """Resolve multiple values for the same variable"""
        # Sort by confidence
        values_sorted = sorted(values, key=lambda x: x["confidence"], reverse=True)

        # If highest confidence is significantly higher, use it
        if values_sorted[0]["confidence"] - values_sorted[1]["confidence"] > 0.2:
            return values_sorted[0]["value"]

        # Otherwise, use weighted average
        total_weight = sum(v["confidence"] for v in values)
        weighted_sum = sum(v["value"] * v["confidence"] for v in values)

        return weighted_sum / total_weight if total_weight > 0 else values_sorted[0]["value"]

    def _to_dataframe(self, resolved_data: Dict[str, Any]) -> pd.DataFrame:
        """Convert resolved data to DataFrame"""
        df = pd.DataFrame([resolved_data]).T
        df.columns = ["value"]
        df.index.name = "variable"
        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data"""
        # Remove null values
        df = df.dropna()

        # Ensure numeric types
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

        # Remove any remaining NaN
        df = df.dropna()

        # Round to 2 decimal places
        df["value"] = df["value"].round(2)

        return df

