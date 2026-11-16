# Task 16 --- Workforce Headcount and Exits Forecast

**Phase:** 4 --- Release\
**Project:** CortexHR\
**Forecast origin:** September 2026\
**Forecast horizon:** October 2026--March 2027\
**Historical period:** January 2020--September 2026

## 1. Objective

Forecast workforce headcount and exits for the next six months, show
central 80% prediction intervals, account for known workforce events,
and test forecast performance on the most recent six historical months.

## 2. Data used

The task used the following supplied files:

-   `monthly_headcount_history.csv` --- 972 rows and 14 columns,
    covering company-level and department-level monthly workforce
    history.
-   `workforce_events.csv` --- 9 workforce events.
-   `sample_forecast.csv` --- 72 rows and 10 columns, used as the
    required output template.

The data checks reported no missing values in the history, events, or
sample template. The headcount movement reconciliation check reported 0
mismatches.

The company-level `ALL` row was not added to the department rows.
Company headcount and exits forecasts were calculated by summing
department forecasts, including department D00.

## 3. Forecasting approach

Two approaches were evaluated:

1.  **Seasonal baseline:** a linear trend fitted on the latest 36
    months, plus a half-strength month-of-year seasonal residual.
2.  **SARIMAX candidate:** SARIMAX `(0,1,1) × (0,1,1,12)` with
    workforce-event and calendar regressors.

Known workforce events were represented as model features. Since future
workforce events were not supplied, future event indicators were set to
zero. March financial-year-end and April appraisal calendar flags were
retained.

A central 80% prediction interval was produced for each forecast.
Department-level forecast variances were combined under an independence
assumption when calculating company-level aggregate intervals.

## 4. Six-month holdout backtest

The backtest trained through March 2026 and evaluated forecasts from
April to September 2026. Lower WAPE indicates better performance.

  Metric                   Model                   MAE    RMSE      WAPE
  ------------------------ ------------------- ------- ------- ---------
  Monthly attrition rate   Seasonal baseline     0.451   0.502   44.759%
  Monthly attrition rate   SARIMAX candidate     0.477   0.541   47.309%
  Exits                    Seasonal baseline     0.566   0.860   81.484%
  Exits                    SARIMAX candidate     0.597   0.912   86.004%
  Headcount                Seasonal baseline     3.266   4.224    4.663%
  Headcount                SARIMAX candidate     1.447   2.282    2.066%

### Selected models

  Forecast metric          Selected model        Holdout WAPE
  ------------------------ ------------------- --------------
  Headcount                SARIMAX candidate           2.066%
  Exits                    Seasonal baseline          81.484%
  Monthly attrition rate   Seasonal baseline          44.759%

The final forecast generation was corrected to use the selected model
for each metric. The final validation also checked that saved headcount
forecasts used the selected method and that supplementary exits
forecasts used the selected seasonal baseline.

## 5. Forecast outputs and evidence

The notebook generated the following deliverables inside the Phase 4
folder:

-   `task16_forecast.csv` --- sample-compatible headcount and company
    attrition forecast.
-   `task16_exits_forecast.csv` --- supplementary exits forecast by
    department and company.
-   `task16_backtest_predictions.csv` --- six-month holdout predictions.
-   `task16_backtest_metrics.csv` --- overall model comparison metrics.
-   `task16_backtest_series_metrics.csv` --- per-series backtest
    metrics.
-   `task16_workforce_events_review.csv` --- supplied workforce event
    register.
-   `task16_forecast_metadata.json` --- forecast metadata and model
    version.

Evidence charts:

-   `task16_historical_trends.png`
-   `task16_seasonality_profile.png`
-   `task16_headcount_forecast.png`
-   `task16_exits_forecast.png`
-   `task16_attrition_forecast.png`

## 6. Validation results

The final notebook validation completed successfully:

-   Main forecast row count and columns match `sample_forecast.csv`.
-   Six forecast months are present and 80% interval ordering is valid.
-   Supplementary exits forecast was created.
-   Six-month holdout backtest contains no missing predictions.
-   Headcount forecast methods match the selected models.
-   Company-level headcount aggregation was validated.
-   Exits forecasts use the selected seasonal baseline.
-   Reports, metadata, and evidence were saved inside `phase-4/`.

## 7. Limitations and interpretation

-   The exits and attrition forecasts have relatively high holdout WAPE
    (81.484% and 44.759%). These results indicate substantial
    uncertainty and should not be presented as highly accurate
    predictions.
-   The backtest uses one six-month holdout period; performance may
    differ in other periods.
-   Future hiring freezes, hiring drives, and other workforce events
    cannot be anticipated without future event information.
-   Event associations are model inputs and do not establish causal
    effects.
-   Small departments and sparse exits series may have wide uncertainty.
-   Aggregate forecast intervals assume independent department-level
    forecast errors.
-   Forecasts are planning estimates for human review, not guaranteed
    outcomes.

## 8. What I learned and next steps

This task demonstrated how to inspect workforce time-series data,
explore trend and seasonality, encode known events, compare a seasonal
baseline with SARIMAX, and evaluate forecasts using a time-based
holdout. It also showed why different workforce metrics can require
different forecasting approaches.

Next, I would improve exits and attrition forecasting by testing
additional features and model specifications, evaluating multiple
rolling backtest windows, and incorporating confirmed future workforce
events when available.

------------------------------------------------------------------------

**Task 16 status:** Notebook execution and final validation completed.\
**Model selection:** SARIMAX for headcount; seasonal baseline for exits
and monthly attrition.
