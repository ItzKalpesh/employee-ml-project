# CortexHR — Employee Analytics Project

## Project Overview

CortexHR is an employee analytics project developed as part of the Aura Workforce AI/ML track. The project covers employee-data auditing, reusable feature engineering, attrition baseline evaluation, attendance and payroll anomaly detection, anomaly explanations, a FastAPI scoring service, and an HR FAQ chatbot.

**Repository:** [employee-ml-project](https://github.com/ItzKalpesh/employee-ml-project)

## Project Workflow

Raw Data → Data Audit → Feature Engineering → Baseline Models → Model Evaluation → Anomaly APIs → HR FAQ Chatbot

## Task 1 — Data Audit and Leakage Hunt

**Status: Completed**

- [Open the data audit notebook](notebooks/01_data_audit.ipynb)
- [Read the audit report](reports/data-audit.md)
- [View audit evidence](evidence/task1_audit_table.png)
- [View attrition class distribution](evidence/task1_class_balance.png)

The audit examines dataset structure, missing values, duplicate candidates, invalid measurements, category inconsistencies, class imbalance, and potential data leakage.

The dataset contains 2,389 employee records, with approximately 14.6% labelled as leavers.

## Task 2 — Reusable Feature Pipeline

**Status: Completed**

- [Open the feature pipeline notebook](notebooks/02_feature_pipeline.ipynb)
- [Read the Task 2 report](reports/task2_feature_pipeline_report.md)
- Feature package: `src/cortexhr_features/` and `src/features/`
- Automated tests: `tests/test_pipeline.py`
- Saved pipeline: `models/feature_pipeline.joblib`
- Version metadata: `models/metadata.json`
- Package configuration: `pyproject.toml`

The pipeline engineers employee features, incorporates attendance and payroll information, handles missing values, scales numeric features, encodes categorical features, and excludes known leakage columns.

The verified Docker build succeeded, and six automated tests passed. The training split contained 1,911 rows and the held-out split contained 478 rows.

## Task 3 — Honest Baseline Models

**Status: Completed**

- [Open the baseline models notebook](notebooks/02_baselines.ipynb)
- [View baseline comparison](evidence/task3_baseline_comparison.png)
- [View benchmark analysis](evidence/task3_benchmark_analysis.png)

The baseline analysis compares a majority-class DummyClassifier, balanced Logistic Regression, and a balanced Decision Tree using stratified five-fold cross-validation.

Logistic Regression achieved a mean ROC-AUC of 0.699 compared with the supplied benchmark of 0.713. The results are documented without claiming that the model outperforms the benchmark.

## Task 4 — Honest Evaluation & Risk Bands

**Status: Completed**

- [Open the evaluation notebook](notebooks/04_model_evaluation.ipynb)
- [View metrics table](evidence/task4_metrics_table.png)
- [View calibration chart](evidence/task4_calibration_curve.png)
- [View lift chart](evidence/task4_lift_chart.png)
- [View manager evaluation note](reports/task4_manager_evaluation.md)

The evaluation uses stratified five-fold out-of-fold predictions to measure ROC-AUC, PR-AUC, precision, recall, and F1. It compares the results against the supplied benchmark, examines calibration, and applies the company's High/Medium/Low risk-band rule.

Logistic Regression achieved an ROC-AUC of 0.699 and PR-AUC of 0.297, compared with benchmark values of 0.713 and 0.332. The High band contained 239 employees, including 83 historical leavers, capturing 23.78% of all historical leavers. The results and limitations are documented honestly, and the manager note recommends supportive human review rather than automated employment decisions.


## Task 5 — Attendance Anomaly Detection

**Status: Completed**

- [Open the attendance anomaly notebook](notebooks/05_attendance_anomaly_detection.ipynb)
- [View detector flag counts](evidence/task5_detector_flag_counts.png)
- [View evaluation metrics](evidence/task5_evaluation_metrics.png)
- [View catch-rate results](reports/task5_catch_rate_results.csv)
- [View baseline comparison](reports/task5_baseline_comparison.csv)
- [View missed anomaly types](reports/task5_missed_anomaly_types.csv)
- [View missed-anomaly analysis](reports/task5_missed_anomaly_analysis.md)

The detector uses Isolation Forest with 3% contamination and combines its predictions with simple attendance rules. Predictions were saved before the unlocked validation labels were used for evaluation.

Isolation Forest achieved 40.27% precision and 59.33% recall, closely matching the supplied baseline of 40.30% precision and 59.30% recall. The combined detector achieved 18.42% precision and 79.33% recall, catching 119 of 150 injected anomalies while flagging 646 records.

The evaluation identified 31 missed anomalies, all classified as `IMPOSSIBLE_HOURS`. The accompanying analysis documents the likely limitations of the detector and recommends human review rather than automated employment decisions.

## Task 6 — Payroll Anomaly Detection

**Status: Completed; implementation and evaluation merged into `main`.**

- [Open the payroll anomaly detector notebook](notebooks/06_Payroll_Anomaly_Detector.ipynb)
- [View overall detector comparison](reports/task6_overall_detector_comparison.csv)
- [View per-error-type metrics](reports/task6_per_error_type_metrics.csv)
- [View baseline comparison](reports/task6_baseline_comparison.csv)
- [View detector flag counts](reports/task6_detector_flag_counts.csv)
- [View missed-anomaly analysis](reports/task6_missed_anomaly_analysis.csv)
- [View missed anomaly types](reports/task6_missed_anomaly_types.csv)
- [Read the Task 6 analysis report](reports/task6_missed_anomaly_analysis.md)
- [View detector flag-count evidence](evidence/task6_detector_flag_counts.png)
- [View evaluation metrics evidence](evidence/task6_evaluation_metrics.png)
- [View baseline reference evidence](evidence/task6_baseline_reference.png)

The detector combines Isolation Forest with interpretable payroll rules and engineered ratio features. The implemented checks include duplicate-payment detection, negative net pay, deductions exceeding gross pay, and payroll reconciliation issues.

**Measured evaluation results:**

| Detector | Precision | Recall | F1-score |
|---|---:|---:|---:|
| Isolation Forest | 20.11% | 37% | 0.2606 |
| Rules only | 81.25% | 65% | 0.7222 |
| Rules + Isolation Forest | 32.78% | 79% | 0.4633 |

The combined detector caught 79 of 100 labelled anomalies and missed 21. The missed cases comprised 14 `MISSED_DEDUCTION`, 5 `ZERO_PAY`, and 2 `OVERTIME_SPIKE` anomalies. The rules caught 42 labelled anomalies that Isolation Forest missed, including duplicate payments, role mismatches, and stale salaries.

Predictions were frozen before evaluation. The authorized validation labels were used for evaluation only, not for training or tuning. The combined detector improves recall but produces more false positives than the rules-only detector. Results are specific to the supplied dataset and do not establish production readiness.

## Task 7 — Reason Codes and Money at Risk

**Status: Completed; implementation PR merged into `main`.**

- [Open the reason codes and money-at-risk notebook](notebooks/07_Reason_Codes_and_Money_at_Risk.ipynb)
- [View explained anomaly results](reports/task7_explained_anomaly_results.csv)
- [View the 20-row flagged-record review](reports/task7_20_flagged_rows_review.csv)

The notebook explains payroll anomaly flags using reason codes and plain-English descriptions. It estimates potential financial exposure where the available payroll data supports a defensible calculation and preserves the official sample output schema.

**Validation results:**

- Total output records: 7,355
- Flagged records: 241
- Flagged records missing record IDs: 0
- Flagged records missing reason codes: 0
- Flagged records missing reason text: 0
- Review sample: 20 flagged records
- Official output columns match the sample schema.

**Money-at-risk limitations:** The available estimates total ₹2,55,55,337.18. This represents potential exposure, not confirmed financial loss. Fifty-one statistical-outlier records have blank monetary estimates because a defensible amount could not be established.

## Task 8 — Anomaly Scoring API

**Status: Completed; PR #10 merged into `main`.**

- **Pull request:** [#10 — Add anomaly scoring API](https://github.com/ItzKalpesh/employee-ml-project/pull/10) — merged.
- **API implementation:** `05_Starter/api_skeleton/app/main.py`
- **API instructions:** `05_Starter/api_skeleton/README.md`
- **Dependencies:** `05_Starter/requirements.txt`
- **Model preparation:** `src/prepare_anomaly_models.py`
- **Versioned model artifacts and metadata:**
  - `models/attendance_anomaly/1.0.0/model.joblib`
  - `models/attendance_anomaly/1.0.0/metadata.json`
  - `models/payroll_anomaly/1.0.0/model.joblib`
  - `models/payroll_anomaly/1.0.0/metadata.json`
- **Tests:** `tests/test_anomaly_api.py`

The FastAPI service exposes attendance and payroll anomaly-scoring endpoints, validates request bodies with Pydantic, loads the versioned models during application startup, and returns anomaly scores, flags, reason codes, explanations, and a potential money-at-risk estimate where applicable.

**Local verification:**

- The model preparation script successfully generated both models.
- All 10 tests passed locally.
- Attendance and payroll scoring endpoints returned HTTP 200 during manual testing.
- Invalid request bodies are covered by tests expecting HTTP 422.

**Run from the repository root:**

Install dependencies:

```powershell
python -m pip install -r .\05_Starter\requirements.txt
```

Start the API:

```powershell
python -m uvicorn app.main:app --app-dir .\05_Starter\api_skeleton
```

Open Swagger UI at `http://127.0.0.1:8000/docs`. Run tests with:

```powershell
python -m pytest -v
```

**Limitations:** The attrition-risk endpoint remains outside Task 8 scope. Anomaly flags and money-at-risk estimates support review; they do not establish fraud or confirmed financial loss. Training datasets remain excluded from Git, so retraining requires obtaining the datasets separately. The saved Task 8 model artifacts are included in PR #10. The HR chat endpoint was added in Task 9 (PR #11).

## Task 9 — HR FAQ Chatbot

**Status: Completed; PR #11 merged into `main`.**

- **Pull request:** [#11 — Add HR FAQ Chatbot](https://github.com/ItzKalpesh/employee-ml-project/pull/11) — merged.
- **Notebook:** `notebooks/08_hr_faq_chatbot.ipynb`
- **Service:** `05_Starter/api_skeleton/app/chatbot_service.py`
- **API integration:** `05_Starter/api_skeleton/app/main.py`
- **Summary:** `reports/task9_chatbot_summary.json`
- **Evaluation evidence:** `reports/task9_confusion_matrix.png`
- **Report:** `reports/task9_hr_faq_chatbot_report.md`
- **Endpoint:** `POST /v1/chat`

The chatbot uses TF-IDF features with Logistic Regression for intent classification and cosine-similarity retrieval for known HR FAQs. It searches the FAQ knowledge base before applying the intent-confidence threshold, uses a safe fallback for uncertain or out-of-scope messages, and includes a privacy guard for requests about another employee's salary.

**Evaluation and verification:**

- Held-out accuracy: **75.76%** across **33 intents** and **132 test messages** (100 correct and 32 incorrect predictions).
- The confidence threshold is `0.55`; the FAQ similarity threshold is `0.22`.
- All 10 automated tests passed locally during Task 9 verification.
- Manual Swagger checks verified known FAQ answers, safe fallback behavior, salary-request refusal, and regression responses from the existing attendance and payroll endpoints.

**Setup note:** The API service loads `models/hr_chatbot_bundle.joblib`. Run the training/evaluation notebook to generate this bundle in the expected location before starting the chatbot-enabled API. Ensure the notebook and API use compatible versions of scikit-learn when generating and loading the serialized bundle.

**Limitations:** Accuracy is measured on the supplied held-out test set and does not establish production readiness. The salary privacy guard uses heuristic text patterns and is not a complete privacy classifier. The chatbot provides HR FAQ assistance, not authorization to access private employee data; sensitive or uncertain cases should be referred to HR.

## Upcoming Tasks

Continue with the remaining project tasks according to the supplied project requirements. Tasks 1–9 are currently recorded as completed; keep this section and the submission checklist updated as further tasks are completed.

## Setup and Verification

The feature pipeline and tests were verified using Docker from the repository root.

Build the feature pipeline:

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace employee-ml-audit sh -c "pip install -e . && python -m cortexhr_features.build"
```

Run the automated tests:

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace employee-ml-audit sh -c "pip install -e . && python -m pytest -q tests/test_pipeline.py"
```

## Repository Structure

- `data/` — Input datasets and supporting data files.
- `notebooks/` — Task notebooks and analysis.
- `src/` — Feature engineering and preprocessing implementation.
- `tests/` — Automated tests.
- `models/` — Saved pipeline and metadata.
- `reports/` — Task reports.
- `evidence/` — Evidence screenshots.

## Data and Security

Do not commit credentials, API keys, passwords, or private environment files. Follow the programme's instructions for handling supplied datasets and model artifacts.