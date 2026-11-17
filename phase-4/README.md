# Aura Workforce - Phase 4

This folder contains the implementation and deliverables for Phase 4 (Tasks 16-20) of the Aura Workforce project. This README is maintained incrementally and will be updated after each task is completed so that it remains the Phase 4 record of implementation, results, evidence, and outstanding work.

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

### Evidence

The following Task 16 visualisations are stored in `evidence/`:

- `task16_attrition_forecast.png`
- `task16_exits_forecast.png`
- `task16_headcount_forecast.png`
- `task16_historical_trends.png`
- `task16_seasonality_profile.png`

### Limitations

- Exits and attrition forecasts have relatively high WAPE values.
- Evaluation uses a six-month holdout period.
- Future workforce events are unknown and are not assumed to occur.
- Forecast intervals rely on simplifying assumptions and should be interpreted with care.

Further improvements and monitoring are planned in subsequent Phase 4 tasks.

## Task 17 - Turn Your Models into a Working API

### Objective

Expose the existing workforce models and HR capabilities through a versioned API, provide a simple prediction interface, and verify the service locally before deployment.

### Implementation

Task 17 implementation is located in `src/task17/`:

- `app/main.py` - FastAPI application and versioned routes.
- `app/ui.py` - Gradio prediction dashboard.
- `app/` service modules - Resume ranking, attrition risk, anomaly detection, and chatbot integration.
- `requirements.txt` - Pinned API and dashboard dependencies.
- `.env.example` - Environment-variable template.
- `Dockerfile` - Container build and startup configuration.
- `smoke_test.py` - Endpoint smoke-test script.
- `README.md` - API usage and deployment notes.

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/v1/health` | Service health |
| POST | `/v1/resume/rank` | Resume ranking |
| GET | `/v1/attrition/risk/{employee_id}` | Employee attrition risk |
| POST | `/v1/anomaly/attendance` | Attendance anomaly scoring |
| POST | `/v1/anomaly/payroll` | Payroll anomaly scoring |
| POST | `/v1/chat` | HR FAQ/chat functionality |

The application uses a `/v1` route prefix, loads models during application startup, validates requests and responses with Pydantic, includes error handling and CORS middleware, and provides a health endpoint.

### Local Verification

The Task 17 service was built and tested locally using Docker:

- Docker image built successfully from the repository root using `phase-4/src/task17/Dockerfile`.
- Swagger UI was verified at `http://localhost:8001/docs`.
- Health endpoint returned HTTP 200 at `http://localhost:8001/v1/health`.
- Gradio dashboard was opened at `http://localhost:8001/ui`.
- Smoke test passed **6/6** checks: health, attrition risk, attendance anomaly, payroll anomaly, resume ranking, and chatbot.

These are local verification results; they do not represent a live cloud deployment.

### Evidence

All seven Task 17 evidence screenshots are stored in `evidence/task17/` and have been committed and pushed to the `task17-release-api` branch:

- `task17_attendance.png` - Attendance anomaly UI and response.
- `task17_docker.png` - Docker/container verification.
- `task17_gradio_ui.png` - Gradio prediction dashboard.
- `task17_health.png` - Health endpoint response.
- `task17_payroll.png` - Payroll anomaly UI and response.
- `task17_smoke_test.png` - Six-endpoint smoke-test result.
- `task17_swagger.png` - Swagger API documentation.

Evidence commit: `9951ec9` - `Add Task 17 deployment evidence and documentation`.

### Hosting and Deployment

The hosting options considered for Task 17 are Render, Railway, Hugging Face Spaces, and AWS. The application has been verified locally in Docker. A live deployment URL and live-endpoint test results have not yet been recorded; cloud deployment and verification remain outstanding.

### Limitations and Responsible Use

Anomaly flags do not establish fraud or misconduct. Attrition scores and other model outputs are decision-support signals and should be reviewed by appropriate people. They must not be used as the sole basis for employment decisions. Local verification does not establish production readiness.

### Current Status

- [x] Versioned FastAPI application and model endpoints implemented.
- [x] Pydantic request/response validation, error handling, CORS, and health endpoint implemented.
- [x] Gradio prediction interface implemented.
- [x] Docker image built and local container verified.
- [x] Smoke test passed all 6 endpoint checks.
- [x] Seven evidence screenshots committed and pushed to `task17-release-api`.
- [ ] Pull request from `task17-release-api` to `main` to be created and reviewed.
- [ ] Cloud deployment and live endpoint verification to be completed.

## Phase 4 Progress

| Task | Description | Status |
|---|---|---|
| Task 16 | Workforce headcount and exits forecasting | Completed |
| Task 17 | Versioned API and prediction interface | Implementation and local verification completed; PR and live deployment pending |
| Task 18 | Upcoming Phase 4 task | Not started |
| Task 19 | Upcoming Phase 4 task | Not started |
| Task 20 | Upcoming Phase 4 task | Not started |

This README will be extended after each subsequent Phase 4 task is completed. Completed task sections should remain as the project record; new work should be added under its own task heading without overwriting earlier results.
