# Phase 3 — Forecast Dashboard ("Can anything beat copying last week?")

**Date:** 2026-07-20 · **Status:** Approved (brainstormed with visual companion)

## Goal

A Next.js/TypeScript dashboard that tells the Phase 2 story visually:
the rolling-origin leaderboard, the 56-day forecast-vs-actual overlay,
and a per-fold explorer. Doubles as Adrian's TypeScript/React learning
vehicle. Portfolio-grade: a visitor with 30 seconds gets the verdict;
one with 5 minutes gets the evidence.

## Decisions

| Question | Decision |
|---|---|
| Data flow | Static JSON export from Python; committed; imported at build. No API. |
| V1 scope | Leaderboard, forecast-vs-actual chart, per-fold explorer. History explorer deferred. |
| Layout | Scroll story: verdict → evidence → microscope (option A) |
| Identity | Lab notebook: paper `#faf6ef`, ink `#1c1a17`, Fraunces + Inter, earth-tone chart palette (option A) |
| Location | `dashboard/` folder in this repo |
| Charts | Recharts |

## Architecture

```
forecaster/export.py  --python -m forecaster.export-->  dashboard/data/*.json
                                                            |
                                        (typed import at build time)
                                                            v
dashboard/ (Next.js App Router, TS)  --next build-->  static site (Vercel in Phase 4)
```

- `forecaster/export.py`: pure builder functions (`build_leaderboard`,
  `build_folds`, `build_meta`) + a `__main__` writer. Runs the same
  8-fold × 7-day backtest as `python -m forecaster`. Pytest-covered.
- `dashboard/data/`: `leaderboard.json`, `folds.json`, `meta.json` —
  committed (static dataset), regenerable with one command.
- `dashboard/lib/types.ts` mirrors the JSON contract;
  `dashboard/lib/transform.ts` derives chart series from folds
  (vitest-covered).

## Data contract

- `leaderboard.json`: `[{ model, label, mae, rmse, champion }]` sorted by MAE
- `folds.json`: `[{ fold, start, end, actual: [{date, value}], forecasts: { <model>: [{date, value}] }, scores: { <model>: {mae, rmse} } }]`
- `meta.json`: `{ dataset, protocol, horizon, n_folds, train_start, train_end, generated_at }`

Model keys match `python -m forecaster` names. Dates are ISO `YYYY-MM-DD`.

## Page (single scroll, `app/page.tsx`)

1. **Hero** — headline "Can anything beat copying last week?", protocol
   subtitle from `meta.json`.
2. **Leaderboard** — one card per model: rank, MAE (big serif numeral),
   RMSE, champion crown on seasonal-naive, one-line "why" blurb.
3. **ForecastChart** — 56 test days; actual revenue as bold ink line,
   each model toggleable via legend chips (React state).
4. **FoldExplorer** — 8 week buttons; selection zooms the chart to that
   fold and shows its score table (per-fold winner highlighted).
5. **Footer** — verdict paragraph, links to repo + notebooks.

Model palette: seasonal-naive `#3d6b35` (green), lag regression
`#8a6414` (wheat), calendar `#a8432e` (clay), naive-last `#6b5f4e`
(taupe), moving-average `#54718a` (slate). Actuals: ink `#1c1a17`.

## Error handling & testing

- Data problems fail at build time (import + `tsc`), not at runtime.
- Transforms guard empty/mismatched fold arrays.
- Python: pytest on export shapes/sorting/champion flag.
- TS: vitest on transforms; CI `dashboard` job: `npm ci`, `tsc --noEmit`
  (via `next build`), vitest.

## Build sessions

- **3a (2026-07-20):** export module + JSON + Next.js scaffold + hero +
  leaderboard live; CI dashboard job.
- **3b:** ForecastChart with legend toggles + transform tests.
- **3c:** FoldExplorer + polish + README section with screenshot.
- **Phase 4:** Vercel deploy, Docker note, README badges.
