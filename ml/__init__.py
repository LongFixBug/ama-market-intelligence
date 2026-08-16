"""
AMA-System: Machine Learning & Multi-Agent Intelligence Package
"""
from ml.pipelines.market_analysis_pipeline import execute_market_pipeline
from ml.schemas.market_report import MarketReport

__all__ = ["execute_market_pipeline", "MarketReport"]
