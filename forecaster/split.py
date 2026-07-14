"""Time-based train/test splitting.

Forecasting data must be split by time, never randomly — a random split
would let the model "see the future" and inflate evaluation scores.
"""
import pandas as pd


def split_train_test(series: pd.Series, test_days: int) -> tuple[pd.Series, pd.Series]:
    """Hold out the final `test_days` observations as the test set."""
    if test_days <= 0:
        raise ValueError("test_days must be positive")
    if test_days >= len(series):
        raise ValueError("test_days must be smaller than the series length")
    return series.iloc[:-test_days], series.iloc[-test_days:]
