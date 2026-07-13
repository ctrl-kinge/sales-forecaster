"""Cleaning and aggregation for retail transaction data.

Rules established in the Online Retail EDA (data-science-notebooks
notebook 01): cancellations have invoice numbers starting with "C",
and non-positive quantities/prices are returns or data errors.
"""
import pandas as pd


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Return valid sales rows with a derived Revenue column.

    Drops cancellations (InvoiceNo starting with "C") and rows with
    non-positive Quantity or UnitPrice. The input frame is not modified.
    """
    mask = (
        ~df["InvoiceNo"].astype(str).str.startswith("C")
        & (df["Quantity"] > 0)
        & (df["UnitPrice"] > 0)
    )
    sales = df.loc[mask].copy()
    sales["Revenue"] = sales["Quantity"] * sales["UnitPrice"]
    return sales


def daily_revenue(sales: pd.DataFrame) -> pd.Series:
    """Aggregate cleaned sales to a daily revenue series.

    Days with no sales inside the observed range become 0 — gaps are
    structural (e.g. store closed), and forecasting models need an
    unbroken daily index.
    """
    return sales.set_index("InvoiceDate")["Revenue"].resample("D").sum()
