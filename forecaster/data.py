"""Download and cache the UCI Online Retail dataset.

Same source and caching pattern as data-science-notebooks: fetch the
zip once, parse the xlsx, and cache as CSV so later loads are fast.
"""
import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "online_retail.csv"


def download() -> Path:
    """Ensure the dataset CSV exists locally and return its path."""
    if CSV_PATH.exists():
        return CSV_PATH

    print(f"Downloading {URL} ...")
    resp = requests.get(URL, timeout=120)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        xlsx_name = next(n for n in zf.namelist() if n.endswith(".xlsx"))
        with zf.open(xlsx_name) as f:
            print("Parsing xlsx (takes a minute)...")
            df = pd.read_excel(f)

    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
    print(f"Saved {len(df):,} rows to {CSV_PATH}")
    return CSV_PATH


def load_raw() -> pd.DataFrame:
    """Load the raw dataset, downloading it first if needed."""
    return pd.read_csv(download(), parse_dates=["InvoiceDate"])


if __name__ == "__main__":
    download()
