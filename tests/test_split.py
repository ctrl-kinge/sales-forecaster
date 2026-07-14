import pandas as pd
import pytest

from forecaster.split import split_train_test


@pytest.fixture
def series():
    idx = pd.date_range("2011-01-01", periods=10, freq="D")
    return pd.Series(range(10), index=idx, dtype=float)


def test_split_sizes(series):
    train, test = split_train_test(series, test_days=3)
    assert len(train) == 7
    assert len(test) == 3

def test_test_set_is_the_tail(series):
    _, test = split_train_test(series, test_days=3)
    assert list(test.values) == [7.0, 8.0, 9.0]

def test_no_overlap_and_no_gap(series):
    train, test = split_train_test(series, test_days=3)
    assert train.index.max() < test.index.min()
    assert (test.index.min() - train.index.max()).days == 1

def test_rejects_test_days_too_large(series):
    with pytest.raises(ValueError):
        split_train_test(series, test_days=10)

def test_rejects_non_positive_test_days(series):
    with pytest.raises(ValueError):
        split_train_test(series, test_days=0)
