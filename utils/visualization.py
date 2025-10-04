import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class Visualizer:
    """Create visualizations for financial data"""

    @staticmethod
    def create_metrics_bar_chart(metrics: Dict[str, float], title: str = "Financial Metrics"):
        """Create bar chart for metrics"""
        df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])

        fig = px.bar(
            df,
            x='Metric',
            y='Value',
            title=title,
            color='Value',
            color_continuous_scale='Viridis'
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            showlegend=False
        )

        return fig

    @staticmethod
    def create_radar_chart(metrics: Dict[str, float], title: str = "Performance Radar"):
        """Create radar chart for metrics"""

        fig = go.Figure(data=go.Scatterpolar(
            r=list(metrics.values()),
            theta=[k.replace('_', ' ').title() for k in metrics.keys()],
            fill='toself',
            line_color='rgb(102, 126, 234)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(metrics.values()) * 1.1]
                )
            ),
            showlegend=False,
            title=title
        )

        return fig

    @staticmethod
    def create_waterfall_chart(data: Dict[str, float], title: str = "Financial Waterfall"):
        """Create waterfall chart"""

        labels = list(data.keys())
        values = list(data.values())

        fig = go.Figure(go.Waterfall(
            x=labels,
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))

        fig.update_layout(
            title=title,
            showlegend=False,
            height=500
        )

        return fig
