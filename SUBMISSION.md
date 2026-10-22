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

- **Status:** Evaluation notebook executed; output checks passed. Task 4 Git branch/PR handoff is still to be completed.
- **Notebook:** `notebooks/04_model_evaluation.ipynb`
- **Helper:** `cortexhr_helpers.py`
- **Metrics:** `reports/task4_metrics.csv`
- **Benchmark comparison:** `reports/task4_benchmark_comparison.csv`
- **Calibration values:** `reports/task4_calibration_values.csv`
- **Risk-band counts:** `reports/task4_risk_band_counts.csv`
- **High-band capture:** `reports/task4_high_band_capture.csv`
- **Manager note:** `reports/task4_manager_evaluation.md` (shortened version verified to fit on one page when exported to PDF)
- **Evidence images:**
  - `evidence/task4_metrics_table.png`
  - `evidence/task4_calibration_curve.png`
  - `evidence/task4_lift_chart.png`
- **Measured results:** Out-of-fold ROC-AUC 0.699 and PR-AUC 0.297; supplied benchmark ROC-AUC 0.713 and PR-AUC 0.332.
- **Risk-band results:** High — 239 employees, 83 historical leavers (34.73% observed leaver rate); Medium — 478 employees, 112 historical leavers (23.43%); Low — 1,672 employees, 154 historical leavers (9.21%).
- **High-band capture:** 83 of 349 historical leavers, or 23.78%; top-10% lift is approximately 2.39× the overall leaver base rate.
- **Limitations:** The measured model is below the supplied benchmark on ROC-AUC and PR-AUC. Scores are ranking signals for supportive human review only, not verified individual probabilities or automated employment decisions.
- **Pull request:** Not created yet.

## Task 5 — Pending

- **Status:** Not started; confirm the official task title and requirements before adding deliverables.
- **Notebook/report/evidence:** To be added after reviewing the Task 5 instructions.
- **Pull request:** Not created yet.

## GitHub Handoff

- **Repository:** https://github.com/ItzKalpesh/employee-ml-project
- **Task 1 retrospective review PR:** #2 — do not merge.
- **Task 2 PR:** #3 — merged.
- **Task 3 PR:** #4 — merged.
- **Task 4 PR:** Not created yet.
- **Task 5 PR:** Pending implementation.

## Final Review Package

Prepare the final review attachment only after all required tasks and reports are complete. Follow the programme's instructions for dataset inclusion and sensitive files. Keep interim Phase 1 report files local until the final report is approved for submission.

Before final submission:
- Update this checklist with the final Task 4 and Task 5 pull request links and statuses.
- Verify the `phase-1` tag points to the final completed Phase 1 commit.
- Update the root `README.md` so its task links and status match the final repository.
- Generate and check the required 2–3 page PDF report under 10 MB.
- Do not include `notebook_changes.txt`, local-only interim reports, secrets, or sensitive/unapproved datasets in a commit.
