# sales-forecaster

[![CI](https://github.com/ctrl-kinge/sales-forecaster/actions/workflows/ci.yml/badge.svg)](https://github.com/ctrl-kinge/sales-forecaster/actions/workflows/ci.yml)

Supermarket sales forecasting — from raw retail transactions to a deployed
forecast dashboard. Research groundwork lives in
[data-science-notebooks](https://github.com/ctrl-kinge/data-science-notebooks)
(notebook 01: Online Retail EDA).

## Roadmap

- [x] **Phase 1 — Data layer:** cached UCI Online Retail download, invoice-level
  cleaning, daily revenue aggregation (tested)
- [ ] **Phase 2 — Models:** moving-average baseline → regression → Prophet/XGBoost,
  with honest evaluation
- [ ] **Phase 3 — Dashboard:** forecasts per product/category in a web UI
- [ ] **Phase 4 — Ship it:** CI (done early), Docker, live deployment

## Setup

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

## Usage

```python
from forecaster.data import load_raw
from forecaster.prep import clean_sales, daily_revenue

series = daily_revenue(clean_sales(load_raw()))  # downloads on first call
```

## Tests

```powershell
pytest tests/ -v
```
