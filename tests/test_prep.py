"""Tests for forecaster.prep — cleaning and aggregation.

Cleaning rules come from the Online Retail EDA (data-science-notebooks
notebook 01): drop cancellations (InvoiceNo starting with "C") and
non-positive quantities/prices, then derive Revenue.
"""
import pandas as pd
import pytest

from forecaster.prep import clean_sales, daily_revenue


@pytest.fixture
def raw():
    return pd.DataFrame({
        "InvoiceNo": ["536365", "C536366", "536367", "536368", "536369"],
        "Quantity": [6, 6, -2, 10, 4],
        "UnitPrice": [2.50, 2.50, 1.00, 0.00, 5.00],
        "InvoiceDate": pd.to_datetime([
            "2011-01-03 10:00", "2011-01-03 11:00", "2011-01-03 12:00",
            "2011-01-04 09:00", "2011-01-05 14:00",
        ]),
    })


class TestCleanSales:
    def test_drops_cancellations(self, raw):
        cleaned = clean_sales(raw)
        assert not cleaned["InvoiceNo"].astype(str).str.startswith("C").any()

    def test_drops_non_positive_quantity_and_price(self, raw):
        cleaned = clean_sales(raw)
        assert (cleaned["Quantity"] > 0).all()
        assert (cleaned["UnitPrice"] > 0).all()

    def test_adds_revenue_column(self, raw):
        cleaned = clean_sales(raw)
        expected = cleaned["Quantity"] * cleaned["UnitPrice"]
        pd.testing.assert_series_equal(cleaned["Revenue"], expected, check_names=False)

    def test_keeps_only_valid_rows(self, raw):
        cleaned = clean_sales(raw)
        assert list(cleaned["InvoiceNo"]) == ["536365", "536369"]

    def test_does_not_mutate_input(self, raw):
        before = raw.copy()
        clean_sales(raw)
        pd.testing.assert_frame_equal(raw, before)


class TestDailyRevenue:
    def test_aggregates_by_day_and_fills_gaps(self, raw):
        series = daily_revenue(clean_sales(raw))
        # Jan 3 has one valid sale (6 * 2.50), Jan 4 none valid, Jan 5 one (4 * 5.00)
        assert series.loc["2011-01-03"] == 15.0
        assert series.loc["2011-01-04"] == 0.0
        assert series.loc["2011-01-05"] == 20.0
        assert len(series) == 3

    def test_daily_frequency(self, raw):
        series = daily_revenue(clean_sales(raw))
        assert series.index.freqstr == "D"
