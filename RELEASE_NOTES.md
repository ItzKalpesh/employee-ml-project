# CortexHR v1.0.0 — Release Notes (Candidate)

**Release status:** Conditional release candidate. Create the Git tag only after the final audit, fresh evaluation, deployed-service verification, demo verification, and release approval.

## Included

- Reusable employee feature pipeline (`features-1.0.0`).
- Attrition risk model (`attrition-v2`, XGBoost with sigmoid calibration).
- Attendance anomaly detector (`1.0.0`, Isolation Forest with reason-code support).
- Payroll anomaly detector (`1.0.0`, Isolation Forest with reason-code support).
- HR FAQ chatbot with TF-IDF + Logistic Regression intent classification, FAQ retrieval, confidence/similarity thresholds, and safe fallback.
- Resume/job ranking and fairness audit workflow.
- Fair-pay recommendation experiment and post-score fairness audit (offline analytical workflow).
- Workforce forecasting with per-metric model selection and central 80% prediction intervals.
- FastAPI backend and Streamlit HR Insights Console.
- Monitoring, reports, model cards, architecture documentation, and audit evidence.

## Not included / not claimed

- Autonomous hiring, firing, promotion, compensation, disciplinary, or employee-performance decisions.
- A guarantee that anomaly flags represent fraud or misconduct.
- A guarantee of prospective validation or production outcome validation for every model.
- A claim that every model has passed a freshly rerun final evaluation.
- A claim that all protected-group fairness risks have been eliminated.
- A claim that SARIMAX is best for every forecast metric.
- A dedicated FastAPI prediction endpoint or verified deployable estimator artifact for the Fair-pay recommender.
- A claim that successful local Docker API tests establish deployed-service equivalence.

## Known limitations

### Attrition
- Calibrated recall at threshold 0.50 is 1.72%; the calibrated model should not be treated as a reliable high-recall screening or intervention gate.
- Raw XGBoost v2 only marginally exceeds the supplied Random Forest reference; this is not a same-run benchmark experiment.
- Verified global feature-importance and individual prediction explanation evidence remains unavailable in the final audit.

### Attendance anomaly
- Our standalone Isolation Forest achieved precision 0.4027 and recall 0.5933 on 7,339 records with 150 injected/reference anomalies.
- The combined detector achieved higher recall (0.7933) but lower precision (0.1842).
- Flags require investigation and verification against source attendance records.

### Payroll anomaly
- Our standalone Isolation Forest achieved precision 0.2011, recall 0.3700, and F1 0.2606 on 7,355 records with 100 injected/reference anomalies.
- The supplied payroll baseline achieved precision 0.217 and recall 0.400; these are baseline results, not our standalone model's metrics.
- Rules-only detection achieved precision 0.8125 and recall 0.6500.
- The combined Rules + Isolation Forest detector achieved precision 0.3278 and recall 0.7900, with a high false-positive burden.
- Alerts must remain human-review signals, not automatic payroll corrections or enforcement decisions.

### HR FAQ chatbot
- Recorded test accuracy is 75.76%.
- Confidence threshold is 0.55 and FAQ similarity threshold is 0.22.
- Per-intent performance varies; weaker intents require further review.
- FAQ content is demonstration/training content and must not be assumed to represent verified company policy.
- The saved bundle exists, but an explicit artifact version identifier has not been verified.

### Resume screener
- Fairness evidence is limited to 25 counterfactual pairs and selected group comparisons.
- Ranking is decision support for recruiter review, not automated hiring or rejection.

### Fair-pay recommender
- Reported held-out Linear Regression MAE is ₹82,141.38 and R² is 0.9662.
- The predicted career-gap group difference is ₹74,105.30 compared with a historical difference of ₹50,653.30; this requires further review.
- No saved estimator artifact or explicit model version was verified.
- The recommender is an offline analytical experiment and is not exposed through a dedicated FastAPI prediction route.

### Workforce forecasting
- Exits WAPE is 81.484% and monthly attrition-rate WAPE is 44.759%.
- Headcount forecasting performed better than exits and attrition forecasting in the recorded backtest.
- Forecasts are planning aids and should be interpreted with uncertainty intervals and business context.

### Monitoring and data quality
- The local monitoring report recorded WATCH PSI values for `tenure_months` (0.209), `annual_fixed_pay` (0.159), and `comp_ratio` (0.104).
- ALERT PSI values were recorded for `months_since_last_raise` (3.835) and `attendance_rate_3m` (1.467).
- PSI alerts indicate distribution changes requiring investigation; they do not independently prove model performance degradation.
- Historical datasets, proxy features, drift, missingness, and source-system quality can affect results.

## Local API verification

On 18 November 2026, the local Docker image `cortexhr-task17:task20` was tested.

The following endpoints returned successful responses:

- `GET /v1/health`
- `GET /v1/monitoring`
- `GET /v1/attrition/risk/EMP-0002`
- `POST /v1/anomaly/attendance`
- `POST /v1/anomaly/payroll`
- `POST /v1/resume/rank`
- `POST /v1/chat`
- `GET /v1/forecast`

The chatbot request required the documented `message` and `session_id` fields; an unsupported `user_role` field was removed to obtain HTTP 200.

These tests verify local API functionality only. Deployed-service equivalence and deployed artifact versions remain to be confirmed.

## Responsible use

All AI-generated outputs are for human review. Verify source records, consider employee context, document decisions, and provide a route for correction or appeal. Do not use model scores as the sole grounds for adverse employment action.

## Versioning

- Intended release tag: `v1.0.0`.
- Tag must point to the final audited commit on `main`, after approval and successful verification.
- This document describes a conditional release candidate; it does not itself authorize release.