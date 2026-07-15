import numpy as np
import pandas as pd

from forecaster.models import regression_forecast


def _weekly_series(days: int, start: str = "2011-01-03") -> pd.Series:
    """Synthetic series: known day-of-week pattern plus linear trend."""
    idx = pd.date_range(start, periods=days, freq="D")
    dow_effect = np.array([100, 120, 140, 160, 180, 60, 0])  # Mon..Sun
    values = dow_effect[idx.dayofweek] + 2.0 * np.arange(days)
    return pd.Series(values.astype(float), index=idx)


def test_forecast_index_continues_train():
    train = _weekly_series(56)
    fc = regression_forecast(train, horizon=7)
    assert fc.index[0] == train.index[-1] + pd.Timedelta(days=1)
    assert len(fc) == 7

def test_recovers_weekly_pattern_and_trend():
    # a linear model given the true feature set should nail this series
    train = _weekly_series(56)
    fc = regression_forecast(train, horizon=14)
    expected = _weekly_series(70).iloc[-14:]
    assert (fc - expected).abs().max() < 1.0

def test_beats_flat_forecast_on_patterned_data():
    train = _weekly_series(56)
    fc = regression_forecast(train, horizon=7)
    actual = _weekly_series(63).iloc[-7:]
    flat = pd.Series(train.mean(), index=actual.index)
    assert (fc - actual).abs().mean() < (flat - actual).abs().mean()
