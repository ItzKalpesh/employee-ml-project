# CortexHR — Submission Checklist

## GitHub Repository

Repository: https://github.com/ItzKalpesh/employee-ml-project

Task code, notebooks, reports, tests, and supporting evidence are maintained in this repository. Each task is tracked through its own pull request where applicable.

## Task 1 — Employee Attrition Data Audit

- **Status:** Completed; changes committed and pushed. Retrospective review PR #2 was opened; do not merge it.
- **Pull request:** https://github.com/ItzKalpesh/employee-ml-project/pull/2
- **Notebook:** `notebooks/01_data_audit.ipynb`
- **Report:** `reports/data-audit.md`
- **Supporting figures:**
  - `evidence/task1_audit_table.png`
  - `evidence/task1_class_balance.png`
  - `reports/attrition_distribution.png`
  - `reports/missing_values_top10.png`
- **Key findings:** Audited 2,389 records and 42 columns; 349 records are leavers (14.61%) and 2,040 are stayers (85.39%).
- **Review note:** The report documents the limits of the validation-ID comparison; do not claim complete independent detection of every planted issue unless separately verified.

## Task 2 — Reusable Feature Pipeline

- **Status:** Completed; Docker build successful and 6 automated tests passed.
- **Pull request:** https://github.com/ItzKalpesh/employee-ml-project/pull/3
- **Notebook:** `notebooks/02_feature_pipeline.ipynb`
- **Report:** `reports/task2_feature_pipeline_report.md`
- **Feature-building package:** `src/cortexhr_features/`
- **Supporting feature code:** `src/features/`
- **Package configuration:** `pyproject.toml`
- **Saved pipeline:** `models/feature_pipeline.joblib` (generated artifact; check repository tracking before relying on a GitHub copy)
- **Version metadata:** `models/metadata.json`
- **Tests:** `tests/test_pipeline.py` — 6 passed.
- **Package:** `cortexhr_features`
- **Version:** `features-1.0.0`
- **Build command:** `python -m cortexhr_features.build`
- **Docker build verification:** `docker build -t employee-ml-audit .`
- **Docker execution command:**

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace employee-ml-audit sh -c "pip install -e . && python -m cortexhr_features.build"
```

- **Docker test command:**

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace employee-ml-audit sh -c "pip install -e . && python -m pytest -q tests/test_pipeline.py"
```

## Task 3 — Honest Baseline Models

- **Status:** Completed; implementation PR #4 merged.
- **Pull request:** https://github.com/ItzKalpesh/employee-ml-project/pull/4
- **Notebook:** `notebooks/02_baselines.ipynb`
- **Evidence:**
  - `evidence/task3_baseline_comparison.png`
  - `evidence/task3_benchmark_analysis.png`
- **Results:** The balanced Logistic Regression baseline achieved ROC-AUC 0.699 and PR-AUC 0.297. The supplied benchmark reported ROC-AUC 0.713 and PR-AUC 0.332.
- **Review note:** Report the benchmark comparison honestly; the measured baseline is below the supplied benchmark on both metrics.

## Task 4 — Honest Evaluation & Risk Bands

- **Status:** Completed; PR #5 merged into main.
- **Pull request:** [PR #5](https://github.com/ItzKalpesh/employee-ml-project/pull/5) — merged.
- **Notebook:** `notebooks/04_model_evaluation.ipynb`
- **Helper:** `cortexhr_helpers.py`
- **Metrics:** `reports/task4_metrics.csv`
- **Benchmark comparison:** `reports/task4_benchmark_comparison.csv`
- **Calibration values:** `reports/task4_calibration_values.csv`
- **Risk-band counts:** `reports/task4_risk_band_counts.csv`
- **High-band capture:** `reports/task4_high_band_capture.csv`
- **Manager note:** `reports/task4_manager_evaluation.md`
- **Evidence images:**
  - `evidence/task4_metrics_table.png`
  - `evidence/task4_calibration_curve.png`
  - `evidence/task4_lift_chart.png`
- **Measured results:** Out-of-fold ROC-AUC 0.699 and PR-AUC 0.297, compared with supplied benchmark values of 0.713 and 0.332.
- **Risk-band results:** High — 239 employees, 83 historical leavers (34.73% observed rate); Medium — 478 employees, 112 historical leavers (23.43%); Low — 1,672 employees, 154 historical leavers (9.21%).
- **High-band capture:** 83 of 349 historical leavers (23.78%); top-10% lift approximately 2.39× the overall leaver base rate.
- **Limitations:** Results are below the supplied benchmark on ROC-AUC and PR-AUC. Scores support human review and should not be treated as verified individual probabilities or used for automated employment decisions.

## Task 5 — Attendance Anomaly Detection

- **Status:** Completed; implementation PR #6 merged into `main`.
- **Pull request:** [#6 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/6).
- **Notebook:** `notebooks/05_attendance_anomaly_detection.ipynb`
- **Validation helper:** `cortexhr_helpers.py` — `catch_rate()`
- **Predictions:** `reports/task5_attendance_anomaly_predictions.csv`
- **Detector flag counts:** `reports/task5_detector_flag_counts.csv`
- **Catch-rate results:** `reports/task5_catch_rate_results.csv`
- **Baseline comparison:** `reports/task5_baseline_comparison.csv`
- **Missed anomalies:** `reports/task5_missed_anomalies.csv`
- **Missed anomaly types:** `reports/task5_missed_anomaly_types.csv`
- **Missed-anomaly analysis:** `reports/task5_missed_anomaly_analysis.md`
- **Evidence images:**
  - `evidence/task5_detector_flag_counts.png`
  - `evidence/task5_evaluation_metrics.png`
- **Method:** Isolation Forest with 3% contamination, combined with simple attendance rules. Predictions were saved before loading the unlocked validation labels for evaluation.
- **Measured results:** Isolation Forest achieved 40.27% precision and 59.33% recall, closely matching the supplied baseline of 40.30% precision and 59.30% recall.
- **Combined detector:** 646 records flagged; 119 of 150 injected anomalies caught; precision 18.42% and recall 79.33%.
- **Missed anomalies:** 31, all classified as `IMPOSSIBLE_HOURS`. The analysis note discusses likely detector limitations without claiming a proven cause.
- **Limitations:** The combined detector improves recall but flags more records, reducing precision. Results support attendance-data quality checks and human review, not automated employment decisions.
- **Pull request:** [#6 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/6).

**Data handling:** Keep `unlock_CX-05_attendance_anomaly_labels.csv` out of Git commits and pushes.

## Task 6 — Payroll Anomaly Detection

- **Status:** Completed; implementation and evaluation committed and merged into `main`.
- **Pull request:** [#7 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/7)
- **Notebook:** `notebooks/06_Payroll_Anomaly_Detector.ipynb`
- **Frozen predictions:** `reports/task6_payroll_anomaly_predictions_frozen.csv`
- **Prediction output:** `reports/task6_payroll_anomaly_predictions.csv`
- **Overall metrics:** `reports/task6_overall_detector_comparison.csv`
- **Per-error-type metrics:** `reports/task6_per_error_type_metrics.csv`
- **Baseline comparison:** `reports/task6_baseline_comparison.csv`
- **Detector flag counts:** `reports/task6_detector_flag_counts.csv`
- **Missed-anomaly analysis:** `reports/task6_missed_anomaly_analysis.csv`
- **Missed anomaly types:** `reports/task6_missed_anomaly_types.csv`
- **Rules caught, model missed:** `reports/task6_rules_caught_model_missed.csv`
- **Rule flag counts:** `reports/task6_rule_flag_counts.csv`
- **Written analysis:** `reports/task6_missed_anomaly_analysis.md`
- **Evidence images:**
  - `evidence/task6_baseline_reference.png`
  - `evidence/task6_detector_flag_counts.png`
  - `evidence/task6_evaluation_metrics.png`
- **Measured results:** Isolation Forest achieved 20.11% precision and 37% recall. Rules-only detection achieved 81.25% precision and 65% recall. The combined detector achieved 32.78% precision and 79% recall, catching 79 of 100 labelled anomalies.
- **Missed anomalies:** 21 combined-detector misses: 14 `MISSED_DEDUCTION`, 5 `ZERO_PAY`, and 2 `OVERTIME_SPIKE`.
- **Method:** Engineered payroll ratios and applied domain-specific validation rules alongside Isolation Forest. Predictions were frozen before the authorized validation labels were used for evaluation.
- **Limitations:** The combined detector improves recall at the cost of more false positives. Results are specific to the supplied dataset and do not establish production readiness.

**Data handling:** Keep `unlock_CX-06_payroll_anomaly_labels.csv` out of Git commits and pushes. The labels were used only for post-development evaluation, not for model training or tuning.

## Task 7 — Reason Codes and Money at Risk

- **Status:** Completed; implementation PR merged.
- **Pull request:** [Task 7 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/9)
- **Notebook:** `notebooks/07_Reason_Codes_and_Money_at_Risk.ipynb`
- **Main output:** `reports/task7_explained_anomaly_results.csv`
- **Review sample:** `reports/task7_20_flagged_rows_review.csv`
- **Purpose:** Map payroll anomaly flags to reason codes and plain-English explanations, estimate potential financial exposure where supported by the available data, and preserve the official sample output schema.
- **Validation results:**
  - Total output records: 7,355
  - Flagged records: 241
  - Flagged records missing record IDs: 0
  - Flagged records missing reason codes: 0
  - Flagged records missing reason text: 0
  - Review sample: 20 records
  - Official output columns match the sample schema.
- **Financial-risk limitation:** Available estimates total ₹2,55,55,337.18. These represent potential exposure, not confirmed losses. Fifty-one statistical-outlier records have blank monetary estimates because a defensible amount could not be established.

## Task 8 — Anomaly Scoring API

- **Status:** Completed; PR #10 merged into `main`.
- **Pull request:** [#10 — Add anomaly scoring API](https://github.com/ItzKalpesh/employee-ml-project/pull/10).
- **API implementation:** `05_Starter/api_skeleton/app/main.py`
- **API README:** `05_Starter/api_skeleton/README.md`
- **Dependencies:** `05_Starter/requirements.txt`
- **Model preparation script:** `src/prepare_anomaly_models.py`
- **Model artifacts and metadata:**
  - `models/attendance_anomaly/1.0.0/model.joblib`
  - `models/attendance_anomaly/1.0.0/metadata.json`
  - `models/payroll_anomaly/1.0.0/model.joblib`
  - `models/payroll_anomaly/1.0.0/metadata.json`
- **Tests:** `tests/test_anomaly_api.py`
- **Implementation:** FastAPI attendance and payroll scoring endpoints, Pydantic request validation, model loading at application startup, versioned metadata, anomaly scores, flags, reason codes, explanations, and potential money-at-risk estimates where supported.
- **Verification:** The model preparation script ran successfully; all 10 local tests passed; both scoring endpoints returned HTTP 200 during manual testing; invalid-input tests check HTTP 422 responses.
- **Data and model handling:** Both trained `.joblib` artifacts are included in the merged PR. Training datasets remain excluded from Git and must be obtained separately to retrain the models.
- **Limitations:** Attrition-risk and chat endpoints are outside Task 8 scope. Anomaly flags and exposure estimates require human review and do not establish fraud or confirmed financial loss.

**Run from the repository root:**

```powershell
python -m pip install -r .\05_Starter\requirements.txt
python -m uvicorn app.main:app --app-dir .\05_Starter\api_skeleton
python -m pytest -v
```

Open Swagger UI at `http://127.0.0.1:8000/docs` after starting the service.

## Task 9 — HR FAQ Chatbot

- **Status:** Completed; PR #11 merged into `main`.
- **Pull request:** [#11 — Add HR FAQ Chatbot](https://github.com/ItzKalpesh/employee-ml-project/pull/11) — merged.
- **Notebook:** `notebooks/08_hr_faq_chatbot.ipynb`
- **Chatbot service:** `05_Starter/api_skeleton/app/chatbot_service.py`
- **API integration:** `05_Starter/api_skeleton/app/main.py`
- **Endpoint:** `POST /v1/chat`
- **Summary artifact:** `reports/task9_chatbot_summary.json`
- **Confusion-matrix evidence:** `reports/task9_confusion_matrix.png`
- **Report:** `reports/task9_hr_faq_chatbot_report.md`
- **Method:** TF-IDF features and Logistic Regression for intent classification; cosine-similarity matching for HR FAQ retrieval; confidence-based fallback and salary privacy guard.
- **Thresholds:** Intent confidence `0.55`; FAQ similarity `0.22`.
- **Held-out evaluation:** 75.76% accuracy across 33 intents and 132 messages; 100 predictions correct and 32 incorrect. Macro F1-score: 0.75; weighted F1-score: 0.75.
- **Confusion-matrix review:** 33 rows and 33 columns; diagonal total: 100 correct predictions. Lower-performing intents identified: `help` (F1 0.29), `team_members` (0.33), `hr_policy_leave` (0.44), `holiday_list` (0.50), `who_to_contact` (0.50), and `working_hours` (0.57). Misclassified examples: `reports/task9_misclassified_messages.csv`.
- **Verification:** All 10 automated tests passed locally. Manual Swagger checks covered FAQ responses, fallback behavior, salary privacy refusal, and regression checks of the attendance and payroll endpoints.
- **Privacy and limitations:** The salary guard is heuristic and is not a complete privacy classifier. The model's held-out accuracy does not establish production readiness. Uncertain or sensitive requests should be referred to HR.
- **Model bundle setup:** `models/hr_chatbot_bundle.joblib` must be generated by running `notebooks/08_hr_faq_chatbot.ipynb` before starting the chatbot-enabled API. Keep scikit-learn versions compatible between training and serving.

## Task 10 — HR Chatbot Memory and Permissions

- **Status:** Completed; PR #13 merged into `main`.
- **Pull request:** [#13 — Task 10: Add Chatbot Memory and Role-Based Permissions](https://github.com/ItzKalpesh/employee-ml-project/pull/13).
- **Notebook:** `notebooks/09_chatbot_memory_permissions.ipynb`
- **Report:** `reports/task10_chatbot_memory_permissions_report.md`
- **Dialogue test runner:** `05_Starter/api_skeleton/run_task10_dialogues.py`
- **API endpoint:** `POST /v1/chat`
- **Memory implementation:** `05_Starter/api_skeleton/app/memory_service.py`
- **Permission implementation:** `05_Starter/api_skeleton/app/permission_service.py`
- **Mock HR service:** `05_Starter/mock_services/`

**Dialogue acceptance results:**
- 12 supplied dialogues.
- 28 total turns.
- 28 passed, 0 failed, 0 errors.
- 100.00% expected-intent accuracy.

**Security validation:** Other-employee salary privacy, request-body role-spoofing prevention, authentication enforcement, and genuine HR authorization checks.

**Regression verification:** Tasks 8 and 9 automated tests: 10/10 passed. Python syntax compilation passed.

**Evidence files:**
- `reports/task10_dialogue_test_results.csv`
- `reports/task10_dialogue_test_summary.csv`
- `reports/task10_security_test_results.csv`
- `reports/task10_mock_service_route_checks.csv`

**Backend limitation:** Analytics operations without an implemented backend return configured failure responses rather than fabricated results.

## GitHub Handoff

- **Repository:** [employee-ml-project](https://github.com/ItzKalpesh/employee-ml-project)
- **Task 1 retrospective review PR:** #2 — do not merge.
- **Task 2 PR:** [#3 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/3).
- **Task 3 PR:** [#4 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/4).
- **Task 4 PR:** [#5 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/5).
- **Task 5 — Attendance Anomaly Detection (Phase 1):** [#6 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/6).
- **Task 6 — Payroll Anomaly Detection (Phase 2):** [#7 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/7).
- **Task 7 — Reason Codes and Money at Risk:** [#9 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/9).
- **Task 8 — Anomaly Scoring API:** [#10 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/10).
- **Task 9 — HR FAQ Chatbot:** [#11 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/11).
- **Task 10 — HR Chatbot Memory and Permissions:** [#13 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/13).

### Phase Status

- **Phase 1:** Tasks 1–5 completed.
- **Phase 2:** Tasks 6–10 completed.
- **Final review package:** Prepare after all required tasks and reports are complete.

## Final Review Package

Prepare the final review attachment only after all required tasks and reports are complete. Follow the programme's instructions for dataset inclusion and sensitive files. Keep interim Phase 1 report files local until the final report is approved for submission.

Before final submission:
- Verify that the pull request links and statuses for Tasks 1–9 are correct.
- Verify the `phase-1` tag points to the final completed Phase 1 commit.
- Ensure the root `README.md` reflects the completed Task 9 work.
- Generate and check the required 2–3 page PDF report under 10 MB.
- Do not include `notebook_changes.txt`, local-only interim reports, secrets, or sensitive/unapproved datasets in a commit.
