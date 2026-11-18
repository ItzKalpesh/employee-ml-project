# Task 20 — Final Model Audit and Handover

## Executive summary
CortexHR combines employee-risk analytics, attendance/payroll anomaly detection, HR FAQ assistance, resume ranking, fair-pay recommendations, workforce forecasting, a FastAPI backend, and a Streamlit HR console. The project contains useful decision-support capabilities, but the evidence does not justify treating every component as ready for autonomous or high-impact employment decisions.

## Evidence status
This audit is based on repository metadata and reports surfaced during the Task 20 inventory. The metrics below are previously recorded results. They have **not yet been freshly rerun during this final audit**. The completion checklist must not be marked fully complete until the evaluation notebooks/scripts are rerun and their outputs reconciled with the live service.

## Model-by-model assessment

| Component | Evidence | Assessment |
|---|---|---|
| Attrition XGBoost v2 | Nested OOF ROC-AUC 0.7176 raw / 0.7109 calibrated; calibrated recall@0.50 0.0172 | Do not release calibrated 0.50 threshold as an operational screening gate. Human-reviewed exploratory signal only. |
| Attendance anomaly | Precision 0.403, recall 0.593; 221 flagged vs 150 injected/reference anomalies | Investigative triage only; verify attendance and leave records. |
| Payroll anomaly | Precision 0.217, recall 0.400; 184 flagged vs 100 injected/reference anomalies | High false-alert burden; not suitable for automated fraud claims. |
| HR chatbot | Bundle test accuracy 75.76%; confidence threshold 0.55; FAQ similarity 0.22 | Limited FAQ assistant with fallback and escalation; verify per-intent performance and current policy content. |
| Resume screener | TF-IDF + skill coverage + experience fit; 25-pair counterfactual twin gaps zero | Human ranking aid only; limited fairness tests do not establish overall fairness. |
| Fair-pay recommender | Linear Regression MAE 82,141.38, R² 0.9662; career-gap predicted group gap 74,105.30 | Illustrative compensation support only; further adjusted fairness analysis required. |
| Workforce forecasting | Headcount SARIMAX WAPE 2.066%; exits/attrition seasonal baseline WAPE 81.484%/44.759% | Headcount planning support; exits/attrition forecasts are uncertain and should be clearly caveated. |

## Baseline comparison
Attrition references: dummy ROC-AUC 0.500 / PR-AUC 0.146; balanced Logistic Regression 0.713 / 0.332; decision tree 0.650 / 0.256; Random Forest 0.715 / 0.336. The leaky Logistic Regression row with perfect scores is explicitly invalid due to target leakage and must never be presented as a valid benchmark.

Raw XGBoost v2 exceeds the supplied Random Forest reference by only +0.0026 ROC-AUC and +0.0045 PR-AUC. This is a reference comparison, not a same-run benchmark experiment.

## Fairness and governance
- Resume counterfactual twin-score gaps were zero across 25 tested pairs, before and after; this is narrow evidence, not a general fairness guarantee.
- Resume designated-job group mean gaps were 0.0203 for gender and 0.0485 for college tier.
- Fair-pay predicted gender group gap was 40,279.52 versus historical 48,941.91.
- Fair-pay predicted career-gap group gap was 74,105.30 versus historical 50,653.30; this is a concern requiring role-/level-adjusted review.
- Attrition subgroup fairness metrics were not present in the available evidence extract.
- Monitoring PSI thresholds in the project helper are <0.10 stable, 0.10–0.25 watch, >0.25 drift; alerts require investigation, not automatic retraining.

## Which model would I not release?
I would not release the calibrated attrition model as an operational employee-screening or intervention gate at a 0.50 threshold: its nested out-of-fold recall is only 1.72%, meaning it misses almost all leavers at that operating point. I would also withhold payroll anomaly automation because precision is only 21.7%. Both may remain restricted research/triage tools with mandatory human review while thresholding, validation, and monitoring are improved.

## Final audit actions still required
1. Re-run all model evaluation notebooks/scripts in a controlled environment and record timestamp, package versions, seeds, and outputs.
2. Confirm model cards' missing data date ranges, per-intent chatbot metrics, resume ranking metrics, exact feature importance and sanitized worked examples.
3. Verify live API responses and deployed artifact versions for all supported endpoints.
4. Confirm exact route coverage for resume ranking, fair-pay, and forecasting.
5. Complete final challenge implementation and tests on its own branch.
6. Record the five-minute demo and verify its link.
7. Create and verify `v1.0.0` tag only after final approval.

## Release decision
**Conditional / restricted release.** The platform may be presented as a human-reviewed HR analytics prototype. Do not describe it as a validated autonomous employment decision system. The final `v1.0.0` tag remains pending fresh evaluation, live version reconciliation, final challenge verification, and demo link verification.

## Task 20 Verification Addendum — 18 November 2026

### Local Docker API verification

The Task 17 application was built and run locally using the Docker image `cortexhr-task17:task20`.

All eight tested API endpoints returned successful responses:

| Endpoint | Result |
|---|---|
| GET /v1/health | HTTP 200 |
| GET /v1/monitoring | HTTP 200 |
| GET /v1/attrition/risk/EMP-0002 | HTTP 200 |
| POST /v1/anomaly/attendance | HTTP 200 |
| POST /v1/anomaly/payroll | HTTP 200 |
| POST /v1/resume/rank | HTTP 200 |
| POST /v1/chat | HTTP 200 |
| GET /v1/forecast | Successful response |

The chatbot test initially returned HTTP 422 because the request included an unsupported `user_role` field. Removing that field and retaining `message` and `session_id` produced HTTP 200. This was a request-schema correction, not a model-code change.

These results verify local API functionality only. They do not establish that the deployed service is running the same image or model artifacts.

### Payroll evaluation clarification

The original Task 6 evaluation CSVs were inspected during the final audit.

Standalone Isolation Forest:
- Precision: 0.2011
- Recall: 0.3700
- F1: 0.2606
- Flagged: 184
- True positives: 37
- False positives: 147
- False negatives: 63

Detector comparison:
- Rules only: precision 0.8125, recall 0.6500, F1 0.7222.
- Rules + Isolation Forest: precision 0.3278, recall 0.7900, F1 0.4633.

The previously recorded 0.217 precision and 0.400 recall refer to the supplied payroll baseline, not our standalone Isolation Forest. The payroll model card has been corrected accordingly.

### Monitoring verification

The local monitoring endpoint returned HTTP 200 and reported the following PSI values:

| Feature | PSI | Status |
|---|---:|---|
| tenure_months | 0.209 | WATCH |
| annual_fixed_pay | 0.159 | WATCH |
| comp_ratio | 0.104 | WATCH |
| months_since_last_raise | 3.835 | ALERT |
| attendance_rate_3m | 1.467 | ALERT |

WATCH and ALERT findings require investigation. PSI indicates distribution change and does not, by itself, prove model performance degradation.

### Architecture and artifact verification

- Mermaid architecture source and SVG export are present under `architecture/`.
- Fair-pay recommender is represented as offline decision-support analysis because no dedicated FastAPI prediction route was found in the inspected route inventory.
- The HR chatbot artifact `models/hr_chatbot_bundle.joblib` exists. Its notebook records test accuracy 75.76%, confidence threshold 0.55, and FAQ similarity threshold 0.22. No explicit artifact version identifier was verified.
- The attrition artifact `models/attrition/attrition-v2/model.joblib` exists.
- No saved Fair-pay estimator artifact or explicit version was found in the repository search.
- No verified attrition feature-importance or individual explanation evidence was found in the searched notebooks and reports.

### Final release blockers

1. Freshly rerun the model evaluation workflows in a controlled environment and record package versions, seeds, timestamps, and outputs.
2. Reconcile model-card metrics with the fresh evaluation results.
3. Verify deployed API behavior and artifact versions against the local Docker build.
4. Record the five-minute demonstration and test its link.
5. Complete final Git review and obtain release approval before creating tag `v1.0.0`.

The project remains a conditional, human-reviewed HR analytics prototype. Successful local endpoint tests do not establish autonomous employment-decision readiness or full production validation.
