# Aura Workforce - Phase 4

This folder contains the implementation and deliverables for Phase 4 (Tasks 16-20) of the Aura Workforce project.

## Task 16 - Workforce Headcount and Exits Forecasting

### Objective

Analyse historical workforce data and forecast monthly headcount, exits, and attrition rates for the next six months.

### Project Structure

```text
phase-4/
├── data/
│   └── raw/
├── notebooks/
├── reports/
├── evidence/
├── models/
└── src/
```

### Input Datasets

The following datasets are stored in `data/raw/`:

- `monthly_headcount_history.csv` - Historical monthly workforce data.
- `workforce_events.csv` - Workforce events used as forecasting features.
- `sample_forecast.csv` - Reference forecast output format.

### Methodology

Two forecasting approaches were evaluated:

1. **Seasonal baseline:** Uses a 36-month linear trend with a seasonal adjustment.
2. **SARIMAX candidate:** Uses a seasonal time-series model with workforce event and calendar features.

A six-month holdout period (April-September 2026) was used to compare model performance.

### Backtest Results

| Metric | Seasonal baseline WAPE | SARIMAX WAPE | Selected model |
|---|---:|---:|---|
| Headcount | 4.663% | 2.066% | SARIMAX |
| Exits | 81.484% | 86.004% | Seasonal baseline |
| Attrition rate | 44.759% | 47.309% | Seasonal baseline |

Models were selected separately for each metric based on holdout performance.

### Main Notebook

`notebooks/16_headcount_forecast.ipynb`

Run the notebook after installing its required dependencies. It loads the datasets, performs validation and backtesting, generates forecasts, and saves the output files.

### Deliverables

- `reports/` - Forecasts, backtest predictions, evaluation metrics, and the detailed Task 16 report.
- `models/` - Forecast metadata.
- `evidence/` - Historical trends, seasonality, and forecast visualisations.
- `notebooks/` - Task 16 implementation notebook.

### Limitations

- Exits and attrition forecasts have relatively high WAPE values.
- Evaluation uses a six-month holdout period.
- Future workforce events are unknown and are not assumed to occur.
- Forecast intervals rely on simplifying assumptions and should be interpreted with care.

Further improvements and monitoring are planned in subsequent Phase 4 tasks.