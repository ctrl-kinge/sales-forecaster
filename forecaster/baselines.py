"""Baseline forecasting models.

These set the bar that any fancier model (Prophet, XGBoost) must clear.
If a model can't beat seasonal-naive on this data, it isn't learning
anything the weekly cycle doesn't already explain.

Every baseline has the same shape: (train, horizon, ...) -> forecast
Series covering the `horizon` days immediately after the train series.
"""
import numpy as np
import pandas as pd


def _forecast_index(train: pd.Series, horizon: int) -> pd.DatetimeIndex:
    start = train.index[-1] + pd.Timedelta(days=1)
    return pd.date_range(start, periods=horizon, freq="D")


def naive_last(train: pd.Series, horizon: int) -> pd.Series:
    """Repeat the last observed value."""
    return pd.Series(train.iloc[-1], index=_forecast_index(train, horizon))


def seasonal_naive(train: pd.Series, horizon: int, season: int = 7) -> pd.Series:
    """Repeat the last full season (default: last week, day-for-day)."""
    if len(train) < season:
        raise ValueError(f"train needs at least {season} observations")
    last_season = train.iloc[-season:].to_numpy()
    values = np.resize(last_season, horizon)
    return pd.Series(values, index=_forecast_index(train, horizon))


def moving_average(train: pd.Series, horizon: int, window: int = 7) -> pd.Series:
    """Repeat the mean of the last `window` observations."""
    if len(train) < window:
        raise ValueError(f"train needs at least {window} observations")
    return pd.Series(train.iloc[-window:].mean(), index=_forecast_index(train, horizon))
