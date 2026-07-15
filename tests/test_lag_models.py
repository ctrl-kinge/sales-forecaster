import numpy as np
import pandas as pd
import pytest

from forecaster.models import lag_regression_forecast


def _weekly_series_with_shift(days: int = 84) -> pd.Series:
    """Weekly pattern whose level doubles halfway through the series."""
    idx = pd.date_range("2011-01-03", periods=days, freq="D")
    dow_effect = np.array([100, 120, 140, 160, 180, 60, 10])
    values = dow_effect[idx.dayofweek].astype(float)
    values[days // 2:] *= 2  # level shift the calendar can't see
    return pd.Series(values, index=idx)


def test_forecast_shape_and_index():
    train = _weekly_series_with_shift()
    fc = lag_regression_forecast(train, horizon=7, lags=(7, 14))
    assert len(fc) == 7
    assert fc.index[0] == train.index[-1] + pd.Timedelta(days=1)

def test_lag_smaller_than_horizon_raises():
    train = _weekly_series_with_shift()
    with pytest.raises(ValueError):
        lag_regression_forecast(train, horizon=28, lags=(7, 14))

def test_tracks_level_shift():
    # after the shift, lag features see the new level; forecast should sit
    # near the doubled pattern, not the full-history average
    train = _weekly_series_with_shift(84)
    fc = lag_regression_forecast(train, horizon=7, lags=(7, 14))
    idx = pd.date_range(train.index[-1] + pd.Timedelta(days=1), periods=7, freq="D")
    dow_effect = np.array([100, 120, 140, 160, 180, 60, 10])
    expected = pd.Series(dow_effect[idx.dayofweek].astype(float) * 2, index=idx)
    assert (fc - expected).abs().mean() < 20.0

def test_insufficient_history_raises():
    train = _weekly_series_with_shift(20)
    with pytest.raises(ValueError):
        lag_regression_forecast(train, horizon=7, lags=(7, 14))
