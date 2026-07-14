"""Forecast accuracy metrics.

MAE and RMSE only: MAPE is deliberately absent because the daily revenue
series contains structural zero days (store closed), and percentage
errors are undefined at zero actuals.
"""
import numpy as np
import pandas as pd


def _check_aligned(actual: pd.Series, forecast: pd.Series) -> None:
    if not actual.index.equals(forecast.index):
        raise ValueError("actual and forecast must share the same index")


def mae(actual: pd.Series, forecast: pd.Series) -> float:
    """Mean absolute error — average miss in revenue units."""
    _check_aligned(actual, forecast)
    return float((actual - forecast).abs().mean())


def rmse(actual: pd.Series, forecast: pd.Series) -> float:
    """Root mean squared error — like MAE but punishes big misses harder."""
    _check_aligned(actual, forecast)
    return float(np.sqrt(((actual - forecast) ** 2).mean()))


def score_forecasts(actual: pd.Series, forecasts: dict[str, pd.Series]) -> pd.DataFrame:
    """Score named forecasts against the actuals; one row per model."""
    rows = {name: {"MAE": mae(actual, fc), "RMSE": rmse(actual, fc)}
            for name, fc in forecasts.items()}
    return pd.DataFrame.from_dict(rows, orient="index")[["MAE", "RMSE"]]
