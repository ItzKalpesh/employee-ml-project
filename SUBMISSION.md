# CortexHR — Submission Checklist

## GitHub Repository

Repository: https://github.com/ItzKalpesh/employee-ml-project

Task code, notebooks, reports, tests, and supporting evidence are maintained in this repository. Each task is tracked through its own pull request where applicable.

## Task 1 — Employee Attrition Data Audit

- **Status:** Completed; changes committed and pushed. Retrospective review PR #2 was opened; do not merge it.
- **Notebook:** `notebooks/01_data_audit.ipynb`
- **Report:** `reports/data-audit.md`
- **Supporting figures:**
  - `evidence/task1_audit_table.png`
  - `evidence/task1_class_balance.png`
  - `reports/attrition_distribution.png`
  - `reports/missing_values_top10.png`
- **Key findings:** Audited 2,389 records and 42 columns; 349 records are leavers (14.61%) and 2,040 are stayers (85.39%).
- **Review note:** The report documents the limits of the validation-ID comparison; do not claim complete independent detection of every planted issue unless separately verified.
- **Pull request:** https://github.com/ItzKalpesh/employee-ml-project/pull/2

## Task 2 — Reusable Feature Pipeline

- **Status:** Completed; Docker build successful and 6 automated tests passed.
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

- **Pull request:** https://github.com/ItzKalpesh/employee-ml-project/pull/3

## Task 3 — Honest Baseline Models

- **Status:** Completed; implementation PR #4 merged.
- **Notebook:** `notebooks/02_baselines.ipynb`
- **Evidence:**
  - `evidence/task3_baseline_comparison.png`
  - `evidence/task3_benchmark_analysis.png`
- **Results:** The balanced Logistic Regression baseline achieved ROC-AUC 0.699 and PR-AUC 0.297. The supplied benchmark reported ROC-AUC 0.713 and PR-AUC 0.332.
- **Review note:** Report the benchmark comparison honestly; the measured baseline is below the supplied benchmark on both metrics.
- **Pull request:** https://github.com/ItzKalpesh/employee-ml-project/pull/4

## Task 4 — Honest Evaluation & Risk Bands

- **Status:** Completed; PR #5 merged into main.
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
- **Pull request:** [PR #5](https://github.com/ItzKalpesh/employee-ml-project/pull/5) — merged.

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
- **Pull request:** [#7 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/7)

**Data handling:** Keep `unlock_CX-06_payroll_anomaly_labels.csv` out of Git commits and pushes. The labels were used only for post-development evaluation, not for model training or tuning.

## GitHub Handoff

- **Repository:** [employee-ml-project](https://github.com/ItzKalpesh/employee-ml-project)
- **Task 1 retrospective review PR:** #2 — do not merge.
- **Task 2 PR:** [#3 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/3).
- **Task 3 PR:** [#4 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/4).
- **Task 4 PR:** [#5 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/5).
- **Task 5 — Attendance Anomaly Detection (Phase 1):** [#6 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/6).
- **Task 6 — Payroll Anomaly Detection (Phase 2):** [#7 — merged](https://github.com/ItzKalpesh/employee-ml-project/pull/7).

### Phase Status

- **Phase 1:** Tasks 1–5 completed.
- **Phase 2:** Task 6 completed; continue with the remaining required Phase 2 tasks.
- **Final review package:** Prepare after all required tasks and reports are complete.

## Final Review Package

Prepare the final review attachment only after all required tasks and reports are complete. Follow the programme's instructions for dataset inclusion and sensitive files. Keep interim Phase 1 report files local until the final report is approved for submission.

Before final submission:
- Update this checklist with the final Task 4 and Task 5 pull request links and statuses.
- Verify the `phase-1` tag points to the final completed Phase 1 commit.
- Update the root `README.md` so its task links and status match the final repository.
- Generate and check the required 2–3 page PDF report under 10 MB.
- Do not include `notebook_changes.txt`, local-only interim reports, secrets, or sensitive/unapproved datasets in a commit.
