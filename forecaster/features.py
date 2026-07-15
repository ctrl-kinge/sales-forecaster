"""Calendar feature engineering for regression forecasting.

Features are derived from the date alone, so the same function builds
the design matrix for both training dates and future forecast dates.
Columns are fixed-width (all 7 weekdays, all 12 months) regardless of
which dates appear — train and forecast matrices must always align.
"""
import pandas as pd

_EPOCH = pd.Timestamp("2010-01-01")


def make_calendar_features(index: pd.DatetimeIndex) -> pd.DataFrame:
    X = pd.DataFrame(index=index)
    for d in range(7):
        X[f"dow_{d}"] = (index.dayofweek == d).astype(int)
    for m in range(1, 13):
        X[f"month_{m}"] = (index.month == m).astype(int)
    X["trend"] = (index - _EPOCH).days
    return X
