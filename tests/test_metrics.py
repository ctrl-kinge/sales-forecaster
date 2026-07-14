import pandas as pd
import pytest

from forecaster.metrics import mae, rmse, score_forecasts


@pytest.fixture
def actual():
    idx = pd.date_range("2011-12-01", periods=4, freq="D")
    return pd.Series([100.0, 200.0, 300.0, 400.0], index=idx)


def test_mae_perfect_forecast(actual):
    assert mae(actual, actual.copy()) == 0.0

def test_mae_known_value(actual):
    forecast = actual + 10  # off by exactly 10 everywhere
    assert mae(actual, forecast) == 10.0

def test_rmse_known_value(actual):
    forecast = actual.copy()
    forecast.iloc[0] += 20  # single error of 20 -> rmse = sqrt(400/4) = 10
    assert rmse(actual, forecast) == 10.0

def test_rmse_penalizes_large_errors_more_than_mae(actual):
    forecast = actual.copy()
    forecast.iloc[0] += 40
    assert rmse(actual, forecast) > mae(actual, forecast)

def test_misaligned_index_raises(actual):
    forecast = actual.copy()
    forecast.index = forecast.index + pd.Timedelta(days=1)
    with pytest.raises(ValueError):
        mae(actual, forecast)

def test_score_forecasts_table(actual):
    forecasts = {"perfect": actual.copy(), "off_by_10": actual + 10}
    table = score_forecasts(actual, forecasts)
    assert list(table.index) == ["perfect", "off_by_10"]
    assert list(table.columns) == ["MAE", "RMSE"]
    assert table.loc["perfect", "MAE"] == 0.0
    assert table.loc["off_by_10", "MAE"] == 10.0
