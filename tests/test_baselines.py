import pandas as pd
import pytest

from forecaster.baselines import moving_average, naive_last, seasonal_naive


@pytest.fixture
def train():
    # 14 days: week 1 = 10..70, week 2 = 100..700 (day-of-week pattern x10)
    idx = pd.date_range("2011-01-03", periods=14, freq="D")  # starts Monday
    values = [10, 20, 30, 40, 50, 60, 70, 100, 200, 300, 400, 500, 600, 700]
    return pd.Series(values, index=idx, dtype=float)


class TestForecastShape:
    """All baselines must forecast the `horizon` days immediately after train."""

    @pytest.mark.parametrize("model", [naive_last, seasonal_naive, moving_average])
    def test_index_continues_train(self, train, model):
        fc = model(train, horizon=3)
        expected = pd.date_range("2011-01-17", periods=3, freq="D")
        assert list(fc.index) == list(expected)


class TestNaiveLast:
    def test_repeats_last_value(self, train):
        fc = naive_last(train, horizon=3)
        assert list(fc.values) == [700.0, 700.0, 700.0]


class TestSeasonalNaive:
    def test_repeats_last_season(self, train):
        fc = seasonal_naive(train, horizon=3, season=7)
        # next Mon/Tue/Wed should copy last week's Mon/Tue/Wed
        assert list(fc.values) == [100.0, 200.0, 300.0]

    def test_horizon_longer_than_season_wraps(self, train):
        fc = seasonal_naive(train, horizon=9, season=7)
        assert list(fc.values[:2]) == [100.0, 200.0]
        assert list(fc.values[7:]) == [100.0, 200.0]  # wraps to season start

    def test_train_shorter_than_season_raises(self, train):
        with pytest.raises(ValueError):
            seasonal_naive(train.iloc[:5], horizon=3, season=7)


class TestMovingAverage:
    def test_mean_of_last_window(self, train):
        fc = moving_average(train, horizon=2, window=7)
        assert list(fc.values) == [400.0, 400.0]  # mean of 100..700

    def test_train_shorter_than_window_raises(self, train):
        with pytest.raises(ValueError):
            moving_average(train.iloc[:5], horizon=2, window=7)
