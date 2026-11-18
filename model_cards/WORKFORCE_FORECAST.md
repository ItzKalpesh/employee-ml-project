# Model Card — Workforce Forecasting

## Purpose
Generate short-horizon planning estimates for headcount, exits, and monthly attrition rate. Forecasts are not guarantees and must not drive automated employment decisions.

## Data
- History: 2020-01 through 2026-09.
- Backtest: 2026-04 through 2026-09 (six-month holdout).
- Inputs listed in metadata: `monthly_headcount_history.csv`, `workforce_events.csv`, `sample_forecast.csv`.
- Trained through: 2026-09.
- Forecast horizon: 2026-10 through 2027-03.
- Central 80% prediction intervals.

## Method
- Candidate: `SARIMAX(0,1,1)x(0,1,1,12)` with workforce-event regressors.
- Baseline: 36-month linear trend + half-strength seasonal residual.
- Model selected independently per metric:
  - Headcount end: SARIMAX candidate.
  - Exits: seasonal baseline.
  - Monthly attrition rate: seasonal baseline.

## Metrics
Six-month holdout backtest:

| Metric | Method | MAE | RMSE | WAPE |
|---|---|---:|---:|---:|
| Monthly attrition rate | Seasonal baseline | 0.451 | 0.502 | 44.759% |
| Monthly attrition rate | SARIMAX candidate | 0.477 | 0.541 | 47.309% |
| Exits | Seasonal baseline | 0.566 | 0.860 | 81.484% |
| Exits | SARIMAX candidate | 0.597 | 0.912 | 86.004% |
| Headcount end | Seasonal baseline | 3.266 | 4.224 | 4.663% |
| Headcount end | SARIMAX candidate | 1.447 | 2.282 | 2.066% |

## Explanations
Known workforce-event regressors are included in the SARIMAX candidate. Event associations are not causal effects. A specific worked forecast example should be taken from the sanitized forecast output.

## Fairness
No employee-level protected-group prediction is produced by this aggregate forecasting model. Check department-level coverage and error patterns; small departments may have unstable forecasts.

## Limits and risks
- Exits and attrition WAPE are high, indicating substantial uncertainty.
- Backtest covers one six-month period.
- Future hiring freezes, hiring drives, and unrecorded events are unknown.
- Small departments and sparse exits series may have wide uncertainty.
- Intervals and aggregate sums rely on modelling assumptions.
- Forecasts are planning estimates for human review only.

## Version and owner
- Version: `cortexhr-forecast-sarimax-events-v1.0`.
- Metadata: `phase-4/models/task16_forecast_metadata.json`.
- Report: `phase-4/reports/task16_workforce_forecast_report.md`.
- Owner: CortexHR project team; named operational owner not recorded.
