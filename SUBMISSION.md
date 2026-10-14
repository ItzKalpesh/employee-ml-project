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
