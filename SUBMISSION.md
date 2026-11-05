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

## Task 11 — Resume Ranking Against Job Descriptions

- **Status:** Completed; PR #14 merged into `main`.
- **Pull request:** [#14 — Task 11: Resume Ranking Against Job Descriptions](https://github.com/ItzKalpesh/employee-ml-project/pull/14).
- **Notebook:** `notebooks/10_resume_job_ranking.ipynb`
- **Input datasets:**
  - `data/job_descriptions.csv`
  - `data/resumes.csv`
  - `data/resume_job_labels.csv`
- **Task README:** `reports/README_Task11.md`
- **Analysis report:** `reports/task11_resume_ranking_report.md`
- **Ranking summary:** `reports/task11_ranking_summary.json`
- **Ranking outputs:** `reports/task11_resume_rankings.csv`, `reports/task11_ranking_quality_by_job.csv`
- **Five misranked examples:** `reports/task11_five_misranked_resumes.csv`
- **Representative review:** `reports/task11_representative_review.csv`
- **Skill extraction audits:** `reports/task11_skill_extraction_audit.csv`, `reports/task11_skill_extraction_by_layout.csv`

**Implementation:** Built a weighted resume-ranking baseline using required-skill coverage, nice-to-have skill coverage, TF-IDF cosine similarity, and experience fit. Compared candidate rankings against human suitability labels, documented a representative review of five resumes against three job descriptions, and explained five misranked examples.

**Evaluation on 555 human-labeled resume–job pairs:**
- Precision@5: **94.0%**
- Recall@5: **54.9%**
- NDCG@5: **0.960**
- Spearman correlation: **0.828**

**Fairness and limitations:** Name, gender, age, and college tier are excluded from the scoring features. Direct identifiers such as email and location are also excluded. This feature exclusion does not establish the absence of indirect bias. The ranking is intended to support recruiter review, not make automated hiring decisions. The API endpoint is documented as a proposal; the existing FastAPI implementation was not changed in Task 11. Metrics are calculated on the available labeled pairs, not all possible resume–job combinations.

## Task 12 — Resume Screener Fairness Audit

- **Status:** Completed; PR #15 merged into `main`.
- **Pull request:** [#15 — Resume Screener Fairness Audit](https://github.com/ItzKalpesh/employee-ml-project/pull/15).
- **Notebook:** `notebooks/11_resume_fairness_audit.ipynb`
- **Analysis report:** `reports/task12_resume_fairness_report.md`
- **Overall summary:** `reports/task12_fairness_summary.json`
- **Before-fix baseline:** `reports/task12_before_fairness_summary.json`
- **Counterfactual pair scores:** `reports/task12_before_fairness_pair_scores.csv`
- **Before/after gap table:** `reports/task12_before_after_gap_table.csv`
- **Protected-group score summary:** `reports/task12_protected_group_score_summary.csv`
- **Job-family gap analysis:** `reports/task12_group_gaps_by_job_family.csv`
- **Ranking quality comparison:** `reports/task12_ranking_quality_comparison.csv`

**Methodology:**

Reproduced the Task 11 weighted resume-ranking baseline and evaluated 25 counterfactual twin pairs. Gender-coded names and college-tier changes were examined while holding job context constant. Protected attributes were used only for post-scoring fairness analysis, not as model inputs.

**Counterfactual evaluation results:**

- Twin pairs: 25
- Zero-gap pairs: 25
- Mean absolute score gap: 0.000
- Maximum absolute score gap: 0.000
- Nonzero-gap pairs: 0

**Protected-group analysis:**

- Gender mean-score gap: 0.0203
- College-tier mean-score gap: 0.0485

**Fairness limitations:**

The zero score gaps apply only to the 25 supplied counterfactual pairs and do not establish overall fairness. Group-level differences are descriptive and are not proof of discrimination or causal effects. The ranking system supports human review and must not be treated as an automated hiring decision system.

**Data handling:** Protected-attribute validation data remains separate from the public repository and is not included in the merged PR.

## Task 13 — Attrition Model V2: Honest Baseline Comparison

- **Status:** Implementation completed; PR #16 opened for review.
- **Pull request:** [#16 — Task 13: Attrition Model V2: Honest Baseline Comparison](https://github.com/ItzKalpesh/employee-ml-project/pull/16).
- **Notebook:** `notebooks/13_attrition_model_v2.ipynb`
- **Versioned model:** `models/attrition/attrition-v2/model.joblib`
- **Model metadata:** `models/attrition/attrition-v2/metadata.json`
- **Analysis report:** `reports/task13_attrition_model_v2_report.md`
- **Overall summary:** `reports/task13_summary.json`
- **Model comparison:** `reports/task13_model_comparison.csv`
- **Fold metrics:** `reports/task13_fold_metrics.csv`
- **Tuning log:** `reports/task13_tuning_log.csv`
- **Calibration comparison:** `reports/task13_calibration_comparison.csv`
- **Calibration evidence:** `evidence/task13_calibration_comparison.png`

**Methodology:**

Reused the Task 2 feature pipeline and the same stratified five-fold evaluation splits as Task 3. LightGBM and XGBoost were evaluated with nested cross-validation; three-fold stratified tuning was performed inside each outer training fold using average precision. Preprocessing was fitted within each fold. XGBoost was also evaluated with sigmoid probability calibration.

**Pooled out-of-fold results:**

| Model | ROC-AUC | PR-AUC | Precision @ 0.50 | Recall @ 0.50 | F1 @ 0.50 | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Task 3 Logistic Regression | 0.6995 | 0.2971 | 0.2565 | 0.5960 | 0.3586 | 0.2070 |
| LightGBM V2 | 0.7030 | 0.3383 | 0.3015 | 0.5072 | 0.3782 | 0.1730 |
| XGBoost V2 raw | 0.7176 | 0.3405 | 0.2763 | 0.5415 | 0.3659 | 0.1866 |
| XGBoost V2 sigmoid calibrated | 0.7109 | 0.3320 | 0.6667 | 0.0172 | 0.0335 | 0.1136 |

Raw XGBoost improved ROC-AUC by **0.0181** and PR-AUC by **0.0434** over the Task 3 Logistic Regression baseline. It was also slightly above the supplied Random Forest reference (ROC-AUC 0.715; PR-AUC 0.336), which is a reference comparison rather than a same-run evaluation.

**Tuning and calibration:**

The XGBoost grid tested `max_depth` values 2 and 3 and `n_estimators` values 150 and 300. The selected full-data parameters were `max_depth=2` and `n_estimators=150`; the full-data CV score was used for final parameter selection only. Sigmoid calibration reduced Brier score from **0.1866** to **0.1136** and log loss from **0.5544** to **0.3771**. At the 0.50 comparison threshold, calibrated recall was **0.0172**, so 0.50 is not presented as an operational intervention threshold.

**Limitations and responsible use:**

The evaluation is internal cross-validation on one historical dataset, not prospective validation. Calibration improves probability-error measures but does not establish that a particular intervention threshold is appropriate. Benchmark values may differ due to feature and environment differences. Model scores should support voluntary, supportive human review only and must not independently determine hiring, promotion, compensation, discipline, or termination.

## Task 14 — Explain Every Person's Attrition Risk

- **Status:** Completed; PR #17 merged into `main`.
- **Pull request:** [#17 — Explain Every Person's Attrition Risk](https://github.com/ItzKalpesh/employee-ml-project/pull/17).
- **Notebook:** `notebooks/14_attrition_risk_explanations.ipynb`
- **SHAP evidence:** `evidence/task14_shap_summary.png`
- **Analysis report:** `reports/task14_attrition_risk_report.md`
- **Summary:** `reports/task14_summary.json`
- **Full employee-level report:** `reports/task14_attrition_risk_report.csv` (generated locally; excluded from the public PR).
- **Human-review sample:** `reports/task14_review_sample_10.csv` (generated locally; excluded from the public PR).

**Methodology:**

Scored 430 active employees using the versioned `attrition-v2` model. Assigned risk bands and used SHAP contributions from the five XGBoost estimators to identify each employee's top three positive risk contributors. Grouped transformed feature contributions back to original features and translated them into plain-English explanations.

**Validation:**

- 430 employee records and 430 unique employees.
- Risk-band distribution: 43 High, 86 Medium, 301 Low.
- No missing values in the three explanation columns.
- No duplicate employee IDs.
- Ten employee explanations manually reviewed.
- All basic report validation checks passed.

**Limitations:**

The explanations represent model associations, not proven causes. SHAP values explain raw XGBoost estimator outputs before sigmoid calibration and are not an exact additive decomposition of the final calibrated ensemble risk score. Outputs support human review and must not independently determine employment decisions.

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
- **Task 11 — Resume Ranking Against Job Descriptions:** [#14 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/14).
- **Task 12 — Resume Screener Fairness Audit:** [#15 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/15).
- **Task 13 — Attrition Model V2:** [#16 — opened](https://github.com/ItzKalpesh/employee-ml-project/pull/16).
- **Task 14 — Explain Every Person's Attrition Risk:** [#17 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/17).

### Phase Status

- **Phase 1:** Tasks 1–5 completed.
- **Phase 2:** Tasks 6–10 completed.
- **Phase 3 (current):** Tasks 11–14 completed.
- **Final review package:** Prepare after all required tasks and reports are complete.

## Final Review Package

Prepare the final review attachment only after all required tasks and reports are complete. Follow the programme's instructions for dataset inclusion and sensitive files. Keep interim Phase 1 report files local until the final report is approved for submission.

Before final submission:
- Verify that the pull request links and statuses for Tasks 1–13 are correct.
- Verify the `phase-1` tag points to the final completed Phase 1 commit.
- Ensure the root `README.md` and this submission checklist reflect the completed Task 13 work.
- Generate and check the required 2–3 page PDF report under 10 MB.
- Do not include `notebook_changes.txt`, local-only interim reports, secrets, or sensitive/unapproved datasets in a commit.
