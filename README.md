# CortexHR — Employee Analytics Project

## Project Overview

CortexHR is an employee analytics project developed as part of the Aura Workforce AI/ML track. The project covers employee-data auditing, reusable feature engineering, attrition baseline evaluation, attendance and payroll anomaly detection, anomaly explanations, a FastAPI scoring service, an HR FAQ chatbot, and resume ranking against job descriptions.

**Repository:** [employee-ml-project](https://github.com/ItzKalpesh/employee-ml-project)

## Project Workflow

Raw Data → Data Audit → Feature Engineering → Baseline Models → Model Evaluation → Anomaly APIs → HR FAQ Chatbot → Resume Ranking

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
- Macro F1-score: **0.75**; weighted F1-score: **0.75**.
- The confusion matrix contains 33 intent rows and columns; its diagonal totals 100 correct predictions.
- Lower-performing intents identified during error analysis: `help` (F1 0.29), `team_members` (0.33), `hr_policy_leave` (0.44), `holiday_list` (0.50), `who_to_contact` (0.50), and `working_hours` (0.57).
- Misclassified examples are recorded in `reports/task9_misclassified_messages.csv` (as identified in the notebook review).
- The confidence threshold is `0.55`; the FAQ similarity threshold is `0.22`.
- All 10 automated tests passed locally during Task 9 verification.
- Manual Swagger checks verified known FAQ answers, safe fallback behavior, salary-request refusal, and regression responses from the existing attendance and payroll endpoints.

**Setup note:** The API service loads `models/hr_chatbot_bundle.joblib`. Run the training/evaluation notebook to generate this bundle in the expected location before starting the chatbot-enabled API. Ensure the notebook and API use compatible versions of scikit-learn when generating and loading the serialized bundle.

**Limitations:** Accuracy is measured on the supplied held-out test set and does not establish production readiness. The salary privacy guard uses heuristic text patterns and is not a complete privacy classifier. The chatbot provides HR FAQ assistance, not authorization to access private employee data; sensitive or uncertain cases should be referred to HR.

## Task 10 — HR Chatbot Memory and Permissions

- **Status:** Completed; [PR #13](https://github.com/ItzKalpesh/employee-ml-project/pull/13) merged into `main`.
- **Notebook:** `notebooks/09_chatbot_memory_permissions.ipynb`
- **Chatbot service:** `05_Starter/api_skeleton/app/chatbot_service.py`
- **API integration:** `05_Starter/api_skeleton/app/main.py`
- **Memory service:** `05_Starter/api_skeleton/app/memory_service.py`
- **Permission service:** `05_Starter/api_skeleton/app/permission_service.py`
- **Mock HR service:** `05_Starter/mock_services/`
- **Dialogue test runner:** `05_Starter/api_skeleton/run_task10_dialogues.py`
- **Report:** `reports/task10_chatbot_memory_permissions_report.md`
- **Endpoint:** `POST /v1/chat`

**Implementation:**

Extended the HR FAQ chatbot with session-based conversational memory, slot extraction, multi-turn follow-up handling, trusted demo-user authentication using `X-Demo-User`, and intent-level role authorization. Integrated supported employee-owned HR operations with the supplied mock HR service and added protection against unauthorized salary disclosure.

**Dialogue evaluation:**

- Dialogue scenarios: **12**
- Total turns: **28**
- Passed: **28**
- Failed: **0**
- Errors: **0**
- Intent accuracy: **100.00%**

**Security and regression validation:**

- Other-employee salary disclosure refusal.
- Request-body role-spoofing prevention.
- Authentication enforcement for protected intents.
- Genuine HR identity authorization.
- Task 8 and Task 9 regression tests: **10/10 passed**.
- Python syntax compilation: passed.

**Evidence:**

- `reports/task10_dialogue_test_results.csv`
- `reports/task10_dialogue_test_summary.csv`
- `reports/task10_security_test_results.csv`
- `reports/task10_mock_service_route_checks.csv`

**Limitations:** Analytics operations without an implemented backend return configured failure responses rather than fabricated results. The dialogue evaluation measures expected-intent matching on the supplied test dialogues and does not establish production readiness.

## Task 11 — Resume Ranking Against Job Descriptions

**Status: Completed; [PR #14](https://github.com/ItzKalpesh/employee-ml-project/pull/14) merged into `main`.**

- **Pull request:** [#14 — Task 11: Resume Ranking Against Job Descriptions](https://github.com/ItzKalpesh/employee-ml-project/pull/14) — merged.
- **Notebook:** `notebooks/10_resume_job_ranking.ipynb`
- **Input datasets:**
  - `data/job_descriptions.csv`
  - `data/resumes.csv`
  - `data/resume_job_labels.csv`
- **Task README:** `reports/README_Task11.md`
- **Analysis report:** `reports/task11_resume_ranking_report.md`
- **Ranking summary:** `reports/task11_ranking_summary.json`
- **Ranking outputs:** `reports/task11_resume_rankings.csv` and `reports/task11_ranking_quality_by_job.csv`
- **Misranking analysis:** `reports/task11_five_misranked_resumes.csv`
- **Representative review:** `reports/task11_representative_review.csv`
- **Skill extraction audits:** `reports/task11_skill_extraction_audit.csv` and `reports/task11_skill_extraction_by_layout.csv`

The baseline ranks resumes against job descriptions using required-skill coverage, nice-to-have skill coverage, TF-IDF cosine similarity, and experience fit. It compares candidate rankings with the available human suitability labels and documents a representative review of five resumes against three job descriptions, plus five misranked examples.

**Evaluation on the 555 available human-labeled resume–job pairs:**

- Precision@5: **94.0%**
- Recall@5: **54.9%**
- NDCG@5: **0.960**
- Spearman correlation: **0.828**

The evaluation is based on the labeled pairs; it does not treat the remaining unlabeled resume–job combinations as human-verified outcomes.

**Fairness and limitations:** Name, gender, age, and college tier are not used as scoring features. The implementation also excludes direct identifiers such as email and location from the scoring formula. Excluding these fields does not prove the system is free of indirect bias. The ranking is a baseline for recruiter review, not an automated hiring decision. The API endpoint is documented as a proposal; this task did not modify the existing FastAPI implementation.

## Task 12 — Resume Screener Fairness Audit

**Status: Completed; [PR #15](https://github.com/ItzKalpesh/employee-ml-project/pull/15) merged into `main`.**

- **Pull request:** [#15 — Task 12: Resume Screener Fairness Audit](https://github.com/ItzKalpesh/employee-ml-project/pull/15) — merged.
- **Notebook:** `notebooks/11_resume_fairness_audit.ipynb`
- **Analysis report:** `reports/task12_resume_fairness_report.md`
- **Overall summary:** `reports/task12_fairness_summary.json`
- **Before-fix baseline:** `reports/task12_before_fairness_summary.json`
- **Counterfactual pair scores:** `reports/task12_before_fairness_pair_scores.csv`
- **Before/after gap comparison:** `reports/task12_before_after_gap_table.csv`
- **Protected-group summary:** `reports/task12_protected_group_score_summary.csv`
- **Job-family gap analysis:** `reports/task12_group_gaps_by_job_family.csv`
- **Ranking quality comparison:** `reports/task12_ranking_quality_comparison.csv`

**Audit methodology:**

Reproduced the Task 11 weighted resume-ranking scorer and evaluated 25 counterfactual resume twin pairs. The pairs were tested against the same job context to examine whether changes to gender-coded names and college tier affected ranking scores.

Protected attributes were loaded separately for post-scoring group analysis and were not used as model inputs.

**Counterfactual results:**

- Twin pairs evaluated: **25**
- Pairs with zero score difference: **25**
- Mean absolute score gap: **0.000**
- Maximum absolute score gap: **0.000**
- Nonzero-gap pairs: **0**

**Protected-group analysis:**

- Gender group mean-score gap: **0.0203**
- College-tier group mean-score gap: **0.0485**

These are descriptive group-level differences, not proof of discrimination or causal effects. Differences may reflect job-family composition and job-relevant candidate characteristics.

**Fairness interpretation and limitations:**

The supplied counterfactual tests found no score changes across the 25 tested twin pairs. This does not establish overall fairness or rule out indirect bias. Group-level differences require careful interpretation, particularly where subgroup sizes are limited. The ranking system remains a decision-support baseline for human recruiter review, not an automated hiring decision system.

Protected-attribute validation data is kept separate from the public repository and is not included in this PR.

## Task 13 — Attrition Model V2: Honest Baseline Comparison

**Status: Implementation completed; [PR #16](https://github.com/ItzKalpesh/employee-ml-project/pull/16) opened for review.**

- **Pull request:** [#16 — Task 13: Attrition Model V2: Honest Baseline Comparison](https://github.com/ItzKalpesh/employee-ml-project/pull/16).
- **Notebook:** `notebooks/13_attrition_model_v2.ipynb`
- **Versioned model:** `models/attrition/attrition-v2/model.joblib`
- **Model metadata:** `models/attrition/attrition-v2/metadata.json`
- **Analysis report:** `reports/task13_attrition_model_v2_report.md`
- **Summary:** `reports/task13_summary.json`
- **Model comparison:** `reports/task13_model_comparison.csv`
- **Fold-level metrics:** `reports/task13_fold_metrics.csv`
- **Tuning log:** `reports/task13_tuning_log.csv`
- **Calibration comparison:** `reports/task13_calibration_comparison.csv`
- **Calibration evidence:** `evidence/task13_calibration_comparison.png`

**Methodology:**

Reused the existing attrition feature pipeline and the same stratified five-fold splits as Task 3. LightGBM and XGBoost gradient-boosting models were evaluated using nested cross-validation, with three-fold hyperparameter tuning performed only inside each outer training fold. Preprocessing was fitted within each fold. XGBoost probabilities were also evaluated after sigmoid calibration.

**Pooled out-of-fold comparison:**

| Model | ROC-AUC | PR-AUC | Precision @ 0.50 | Recall @ 0.50 | F1 @ 0.50 | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Task 3 Logistic Regression | 0.6995 | 0.2971 | 0.2565 | 0.5960 | 0.3586 | 0.2070 |
| LightGBM V2 | 0.7030 | 0.3383 | 0.3015 | 0.5072 | 0.3782 | 0.1730 |
| XGBoost V2 raw | 0.7176 | 0.3405 | 0.2763 | 0.5415 | 0.3659 | 0.1866 |
| XGBoost V2 sigmoid calibrated | 0.7109 | 0.3320 | 0.6667 | 0.0172 | 0.0335 | 0.1136 |

Raw XGBoost improved ROC-AUC by **0.0181** and PR-AUC by **0.0434** over the Task 3 Logistic Regression baseline. It also exceeded the supplied Random Forest reference (ROC-AUC 0.715; PR-AUC 0.336), but that reference is not a same-run evaluation.

**Tuning and calibration:**

The XGBoost search tested `max_depth` values 2 and 3 and `n_estimators` values 150 and 300. The selected full-data parameters were `max_depth=2` and `n_estimators=150`; the full-data CV score was used for parameter selection, not as an unbiased performance estimate. Sigmoid calibration reduced Brier score from 0.1866 to 0.1136 and log loss from 0.5544 to 0.3771. At the comparison threshold of 0.50, calibrated recall was only 0.0172, so this threshold is not suitable as an operational intervention rule.

**Limitations and responsible use:**

Evaluation is internal cross-validation on the supplied historical dataset, not prospective deployment validation. Calibration improves probability-error metrics but does not guarantee useful decisions at a particular threshold. Benchmark values may differ because of feature and environment differences. Model scores are for supportive human review only and must not independently determine hiring, promotion, compensation, discipline, or termination.

## Task 14 — Explain Every Person's Attrition Risk

**Status: Completed; [PR #17 — merged into `main`](https://github.com/ItzKalpesh/employee-ml-project/pull/17).**

- **Pull request:** [#17 — Task 14: Explain Every Person's Attrition Risk](https://github.com/ItzKalpesh/employee-ml-project/pull/17)
- **Notebook:** `notebooks/14_attrition_risk_explanations.ipynb`
- **SHAP evidence:** `evidence/task14_shap_summary.png`
- **Analysis report:** `reports/task14_attrition_risk_report.md`
- **Summary:** `reports/task14_summary.json`
- **Full employee-level report:** `reports/task14_attrition_risk_report.csv` (generated locally; excluded from the public PR).
- **Human-review sample:** `reports/task14_review_sample_10.csv` (generated locally; excluded from the public PR).

**Methodology:**

- Scored 430 active employees using the versioned `attrition-v2` model.
- Assigned High, Medium, and Low risk bands.
- Used SHAP to identify the top three positive risk contributors for each employee.
- Grouped transformed feature contributions back to the original model features.
- Generated plain-English explanations for all 430 employees.
- Created a 10-employee sample for manual explanation review.

**Validation results:**

- Total employee records: 430.
- Unique employees: 430.
- High risk: 43; Medium risk: 86; Low risk: 301.
- Missing explanations: 0.
- Duplicate employee records: 0.
- All basic report validation checks passed.
- Ten employee explanations manually reviewed.

**Limitations:**

SHAP explanations describe model associations, not causal relationships. Contributions were calculated from raw XGBoost estimators before sigmoid calibration and are not an exact additive decomposition of the final calibrated ensemble risk score. Outputs support responsible human review, not automated employment decisions.

## Upcoming Tasks

Continue with the remaining project tasks according to the supplied project requirements. Tasks 1–14 are currently recorded as completed; keep this section and the submission checklist updated as further tasks are completed.

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