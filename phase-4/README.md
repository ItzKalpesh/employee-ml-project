# Aura Workforce - Phase 4

This folder contains the implementation and deliverables for Phase 4 (Tasks 16-20) of the Aura Workforce project. This README is maintained incrementally and serves as the Phase 4 record of implementation, results, evidence, and outstanding work.

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

---

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
| GET | `/v1/monitoring` | Latest Task 18 drift and fairness monitoring report (HR/ADMIN only) |

The application uses a `/v1` route prefix, loads models during application startup, validates requests and responses with Pydantic, includes error handling and CORS middleware, and provides a health endpoint.

### Local Verification

The Task 17 service was built and tested locally using Docker:

- Docker image built successfully from the repository root using `phase-4/src/task17/Dockerfile`.
- Swagger UI was verified at `http://localhost:8001/docs`.
- Health endpoint returned HTTP 200 at `http://localhost:8001/v1/health`.
- Gradio dashboard was opened at `http://localhost:8001/ui`.
- Smoke test passed **6/6** checks: health, attrition risk, attendance anomaly, payroll anomaly, resume ranking, and chatbot.

### Hosting and Deployment

The API is deployed on Render and tracks the repository's `main` branch.

- **Production API:** [https://employee-ml-project-ea41.onrender.com](https://employee-ml-project-ea41.onrender.com)
- **Swagger documentation:** [https://employee-ml-project-ea41.onrender.com/docs](https://employee-ml-project-ea41.onrender.com/docs)
- **Health endpoint:** [https://employee-ml-project-ea41.onrender.com/v1/health](https://employee-ml-project-ea41.onrender.com/v1/health)
- **Monitoring endpoint:** [https://employee-ml-project-ea41.onrender.com/v1/monitoring](https://employee-ml-project-ea41.onrender.com/v1/monitoring) - requires an authorized HR or ADMIN `X-Demo-User` header.
- **Dockerfile:** `phase-4/src/task17/Dockerfile`
- **Deployment status:** Live

The deployment was verified using the production API. The Task 18 monitoring endpoint was subsequently integrated into this service and deployed.

### Evidence

Task 17 evidence screenshots are stored in `evidence/task17/`:

- `task17_attendance.png` - Attendance anomaly UI and response.
- `task17_docker.png` - Docker/container verification.
- `task17_gradio_ui.png` - Gradio prediction dashboard.
- `task17_health.png` - Health endpoint response.
- `task17_payroll.png` - Payroll anomaly UI and response.
- `task17_smoke_test.png` - Six-endpoint smoke-test result.
- `task17_swagger.png` - Swagger API documentation.

### Limitations and Responsible Use

Anomaly flags do not establish fraud or misconduct. Attrition scores and other model outputs are decision-support signals and should be reviewed by appropriate people. They must not be used as the sole basis for employment decisions. Deployment and endpoint verification do not, by themselves, establish production readiness.

### Current Status

- [x] Versioned FastAPI application and model endpoints implemented.
- [x] Pydantic request/response validation, error handling, CORS, and health endpoint implemented.
- [x] Gradio prediction interface implemented.
- [x] Docker image built and local container verified.
- [x] Smoke test passed all 6 endpoint checks.
- [x] Evidence screenshots committed.
- [x] Pull request merged into `main`.
- [x] Cloud deployment completed and live endpoints verified.

---

## Task 18 - Drift and Fairness Monitoring

**Status:** Completed; [PR #24 - Task 18: Drift and Fairness Monitoring](https://github.com/ItzKalpesh/employee-ml-project/pull/24) merged into `main`.

### Objective

Implement automated monitoring for workforce model input drift and fairness indicators. Generate monitoring reports, automate execution through GitHub Actions, and expose the latest monitoring results through the Task 17 API.

### Implementation

Task 18 implementation is located in `src/task18/`:

- `monitor.py` - Monitoring pipeline for population stability, resume fairness, and pay fairness.
- `requirements.txt` - Monitoring dependencies.

Generated reports are stored in `reports/task18/`:

- `monitoring_report.json` - Consolidated monitoring results and overall status.
- `psi_monitoring.csv` - Population Stability Index results for the monitored attrition features.
- `resume_twin_fairness.csv` - Counterfactual resume twin-pair results.
- `resume_group_fairness.csv` - Resume ranking score comparisons across protected groups.
- `pay_fairness.csv` - Historical and predicted pay comparisons across protected groups.

### Drift Monitoring Methodology

Population Stability Index (PSI) is calculated by comparing the reference attrition dataset against the current scoring dataset for eight model input features.

The following thresholds are used:

| PSI value | Status | Interpretation |
|---|---|---|
| PSI < 0.10 | OK | Little distribution change |
| 0.10 to 0.25 | WATCH | Moderate distribution change |
| PSI > 0.25 | ALERT | Significant distribution change |

### PSI Results

| Feature | PSI | Status |
|---|---:|---|
| `tenure_months` | 0.208619 | WATCH |
| `total_experience_years` | 0.050952 | OK |
| `annual_fixed_pay` | 0.159346 | WATCH |
| `comp_ratio` | 0.103822 | WATCH |
| `months_since_last_raise` | 3.834631 | ALERT |
| `last_engagement_score` | 0.062674 | OK |
| `attendance_rate_3m` | 1.467049 | ALERT |
| `avg_overtime_hours_per_month_3m` | 0.035894 | OK |

**Overall drift status: ALERT**

Two features exceeded the ALERT threshold: `months_since_last_raise` and `attendance_rate_3m`. These results indicate substantial changes in their distributions between the reference and current scoring datasets. PSI measures feature distribution changes; it does not directly establish that model accuracy has declined.

### Resume Fairness Audit

The Task 12 resume fairness audit was repeated as part of the monitoring pipeline.

The audit includes:

- Counterfactual twin-pair testing.
- Gender-group score comparisons.
- College-tier group score comparisons.

For counterfactual testing, 25 resume twin pairs were evaluated while keeping skills and experience identical.

| Metric | Result |
|---|---:|
| Twin pairs evaluated | 25 |
| Mean absolute twin score gap | 0.000 |
| Maximum absolute twin score gap | 0.000 |
| Nonzero twin score gaps | 0 |
| Gender-group score gap | 0.020338 |
| College-tier score gap | 0.048542 |

The counterfactual twin test produced zero score differences across the evaluated pairs.

Protected attributes are loaded only after resume scoring for fairness auditing. They are not used as model predictors.

### Pay Fairness Audit

The Task 15 pay fairness audit was repeated using out-of-fold predictions from a five-fold cross-validation process.

The audit compares historical and predicted annual fixed pay across gender and career-gap groups.

Protected attributes, including gender and career-gap information, are excluded from the pay prediction model's input features and are used only for post-prediction fairness analysis.

| Group comparison | Historical pay gap | Predicted pay gap |
|---|---:|---:|
| Gender | 48,941.91 | 40,279.52 |
| Career gap | 50,653.30 | 74,105.30 |

The pay audit uses the `offered_annual_fixed` target and evaluates group-level differences between historical and predicted pay.

These comparisons are descriptive indicators. They do not establish causation or prove that a pay decision is fair or unfair.

### Automated Monitoring

The monitoring pipeline is automated using GitHub Actions.

Workflow file:

`.github/workflows/task18-monitor.yml`

The workflow:

1. Checks out the `main` branch.
2. Sets up Python 3.12.
3. Installs the Task 18 monitoring dependencies.
4. Restores required monitoring datasets and protected audit files from GitHub Secrets.
5. Executes `phase-4/src/task18/monitor.py`.
6. Uploads the generated monitoring reports as workflow artifacts.
7. Removes restored sensitive datasets and protected audit files.
8. Publishes updated monitoring reports to the `main` branch.

The workflow supports both scheduled and manual execution.

- **Scheduled execution:** Every Monday at 02:00 UTC.
- **Manual execution:** Available through GitHub Actions using `workflow_dispatch`.

Monitoring reports are committed to `reports/task18/` so the latest results can be accessed by the deployed API.

### Production API Integration

The Task 18 monitoring report is integrated into the Task 17 FastAPI application.

**Endpoint:**

`GET /v1/monitoring`

The endpoint reads the latest committed `reports/task18/monitoring_report.json` file and returns its contents.

Access is restricted by demo-user role:

| User role / condition | Expected response |
|---|---|
| HR | HTTP 200 |
| ADMIN | HTTP 200 |
| Employee | HTTP 403 |
| Missing authentication header | HTTP 401 |

The endpoint was verified against the deployed Render service.

**Production URL:**

https://employee-ml-project-ea41.onrender.com/v1/monitoring

The latest monitoring report was successfully returned by the production endpoint.

### PSI ALERT Investigation and Response Plan

When a monitored feature reaches the ALERT threshold:

1. Investigate the affected feature distributions, starting with `months_since_last_raise` and `attendance_rate_3m`.
2. Check data quality, missing values, unusual values, and changes in data collection or preprocessing.
3. Determine whether the observed distribution change reflects a genuine workforce change or a data pipeline issue.
4. Evaluate model performance using newly labelled data before deciding whether retraining is necessary.
5. Document investigation findings and corrective actions.
6. Require appropriate human review before making decisions based on model outputs.
7. Continue monitoring subsequent scoring data to determine whether the drift persists.

An ALERT does not automatically trigger model retraining. PSI is a drift indicator, not a direct model-performance metric.

### Evidence

Task 18 evidence screenshots are stored in `evidence/task18/`.

The evidence set records the following production and automation checks:

1. HR user successfully accessing the monitoring endpoint (HTTP 200).
2. ADMIN user successfully accessing the monitoring endpoint (HTTP 200).
3. Employee access correctly denied (HTTP 403).
4. Missing authentication correctly rejected (HTTP 401).
5. GitHub Actions monitoring workflow execution.
6. Successful completion of the monitoring workflow steps.
7. Monitoring reports successfully published to the `main` branch.
8. Render deployment showing the updated service as Live.

### Limitations and Responsible Use

- PSI measures changes in feature distributions; it does not directly measure prediction accuracy.
- A high PSI value requires investigation and does not automatically mean the model must be retrained.
- Fairness group comparisons are descriptive and do not establish causation.
- Small protected groups may produce unstable group-level estimates.
- Protected attributes are used for post-scoring audits and are not included as prediction features.
- Model outputs and fairness reports should support human review, not replace it.
- Monitoring results should be interpreted alongside data quality checks and newly labelled outcome data.

### Current Status

- [x] PSI monitoring implemented for eight attrition model input features.
- [x] PSI thresholds and overall drift status implemented.
- [x] Task 12 resume counterfactual twin fairness audit repeated.
- [x] Resume protected-group score comparisons generated.
- [x] Task 15 pay fairness audit repeated.
- [x] Historical and predicted pay gaps compared.
- [x] Automated GitHub Actions workflow configured.
- [x] Scheduled and manual workflow execution supported.
- [x] Monitoring reports generated and published to `main`.
- [x] Sensitive restored datasets removed after workflow execution.
- [x] Task 17 API integrated with the `/v1/monitoring` endpoint.
- [x] HR and ADMIN access verified; Employee and unauthenticated access restrictions verified.
- [x] Updated API deployed successfully on Render.
- [x] Eight Task 18 evidence screenshots added to `evidence/task18/`.

---


---

## Task 19 - HR Insights Console

### Objective

Provide an HR-facing web console that brings the project's key capabilities together in one interface and connects to the existing FastAPI backend.

### Implementation

Task 19 implementation is located in `src/task19/`:

- `app.py` - Streamlit HR Insights Console.
- `api_client.py` - API client for the hosted FastAPI service.
- `requirements.txt` - Streamlit application dependencies.
- `.env.example` - Environment-variable template.

**Pull request:** [#26 - HR Insights Console](https://github.com/ItzKalpesh/employee-ml-project/pull/26) - merged into `main`.

### Console Features

1. **Risks** - employee attrition-risk lookup.
2. **Anomalies** - attendance and payroll anomaly checks.
3. **Assistant** - HR FAQ/chat interface with follow-up conversation continuity.
4. **Resume Screener** - resume ranking against a selected job description.
5. **Forecast** - workforce headcount and exits forecast view.

### Verification Completed

- Live attrition-risk API integration tested using an HR demo user.
- Attendance and payroll anomaly integrations tested.
- HR Assistant tested, including follow-up conversation continuity.
- Resume Screener tested with a sample job.
- Forecast interface and API integration implemented. Live forecast verification remains pending until the required forecast data files are available in the deployed API environment.

### Usability and Deployment Status

- Desktop interface reviewed locally.
- A simulated first-time-user usability review was prepared; it is not a substitute for feedback from an independent participant.
- Actual external-user testing, phone testing, final screenshots, and separate frontend deployment verification remain pending.
- Add the verified Streamlit frontend deployment URL after deployment.

### Responsible Use

AI-generated outputs are labelled **"AI-generated — for human review"**. The console is a decision-support tool. Its outputs must not be used as the sole basis for employment-related decisions.

## Phase 4 Progress

| Task | Description | Status |
|---|---|---|
| Task 16 | Workforce headcount and exits forecasting | Completed |
| Task 17 | Versioned API, prediction interface, and cloud deployment | Completed |
| Task 18 | Drift and fairness monitoring | Completed |
| Task 19 | HR Insights Console | Implementation merged; deployment and validation in progress |
| Task 20 | Upcoming Phase 4 task | Not started |

Task 19 implementation was merged through PR #26. Forecast live verification, separate frontend deployment, phone testing, independent external-user testing, and final evidence capture remain outstanding. This README will be extended after each subsequent Phase 4 task is completed. Completed task sections should remain as the project record; new work should be added under its own task heading without overwriting earlier results.