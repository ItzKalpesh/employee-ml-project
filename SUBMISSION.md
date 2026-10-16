# CortexHR — Submission Checklist

## Task 1: Employee Attrition Data Audit

- Notebook: `notebooks/01_data_audit.ipynb`
- Report: `reports/data-audit.md`
- Supporting figures:
  - `reports/attrition_distribution.png`
  - `reports/missing_values_top10.png`
- Status: Audit analysis and report created. Answer-key comparison remains to be verified if required by the guide.

## Task 2: Reusable Feature Pipeline

- Notebook: `notebooks/02_feature_pipeline.ipynb`
- Report: `reports/task2_feature_pipeline_report.md`
- Feature-building package: `src/cortexhr_features/`
- Package configuration: `pyproject.toml`
- Saved pipeline: `models/feature_pipeline.joblib`
- Version metadata: `models/metadata.json`
- Tests: `tests/test_pipeline.py`
- Status: Docker execution verified; 3 automated tests passed.

### Verified execution command

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace employee-ml-audit sh -c "pip install -e . && python -m cortexhr_features.build"
```

### Verified test command

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace employee-ml-audit sh -c "pip install -e . && python -m pytest -q tests/test_pipeline.py"
```

## Tasks 3 and 4

- Status: Pending completion and verification.
- Add each task's report, source files, tests and execution instructions after implementation.

## GitHub Handoff

- Repository URL: To be added.
- Task 1 pull request: To be added.
- Task 2 pull request: To be added.
- Task 3 pull request: To be added.
- Task 4 pull request: To be added.

## Final Review Package

Prepare the review attachment only after the required tasks and reports have been completed. Follow the programme's instructions for dataset inclusion and sensitive files.


# CortexHR — Task Submission Tracker

## GitHub Repository

Repository: https://github.com/ItzKalpesh/employee-ml-project

All task code, reports, tests, and model artifacts are maintained
in this repository. Each task will have its own pull request.

## Task 1 — Data Audit

- Status: Completed; committed to `main`. Retrospective review PR opened; do not merge.
- Report: [Data Audit](reports/data-audit.md)
- Notebook: [01 Data Audit](notebooks/01_data_audit.ipynb)
- Pull Request: [Task 1 PR #2](https://github.com/ItzKalpesh/employee-ml-project/pull/2)

## Task 2 — Reusable Feature Pipeline

- Status: Implementation and four tests passing; final requirement review pending.
- Report: [Feature Pipeline Report](reports/task2_feature_pipeline_report.md)
- Package: `cortexhr_features`
- Version: `features-1.0.0`
- Build command: `python -m cortexhr_features.build`
- Tests: `tests/test_pipeline.py` — 4 passed.
- Pull Request: [Task 2 PR #1](https://github.com/ItzKalpesh/employee-ml-project/pull/1)

## Task 3 — Attrition Baseline Models

- Status: Not started.
- Planned report: `reports/baseline-report.md`
- Pull Request: Not created yet.