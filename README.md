# CortexHR — Employee Analytics Project

## Project Overview

This project implements employee attrition data auditing and a reusable feature preprocessing pipeline.

## Project Structure

- `data/` — Input datasets and data dictionary
- `notebooks/` — Task 1 audit and Task 2 pipeline notebooks
- `src/features/` — Original feature engineering and preprocessing implementation
- `src/cortexhr_features/` — Packaged command-line entry point
- `tests/` — Automated pipeline tests
- `models/` — Saved preprocessing pipeline and version metadata
- `reports/` — Task reports and audit figures

## Task 1 — Data Audit

- Notebook: `notebooks/01_data_audit.ipynb`
- Report: `reports/data-audit.md`

The audit covers dataset structure, missing values, duplicate records, attrition distribution, outliers and potential data leakage.

## Task 2 — Reusable Feature Pipeline

- Notebook: `notebooks/02_feature_pipeline.ipynb`
- Report: `reports/task2_feature_pipeline_report.md`
- Saved pipeline: `models/feature_pipeline.joblib`
- Metadata: `models/metadata.json`
- Package configuration: `pyproject.toml`

### Install and execute in Docker

From the project root, run:

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace employee-ml-audit sh -c "pip install -e . && python -m cortexhr_features.build"
```

### Run tests in Docker

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace employee-ml-audit sh -c "pip install -e . && python -m pytest -q tests/test_pipeline.py"
```

Verified result: 3 tests passed. The pipeline transformed 2,389 rows into 85 features with feature version `features-1.0.0`.

## Remaining Tasks

Tasks 3 and 4 will be documented here after implementation and verification.

## Submission

The final review package will include the completed task reports, notebooks, source code, tests, Docker configuration and other required deliverables. Repository and pull-request links will be added after they are created.

## Data and Security

Do not commit credentials, secrets or private environment files. Follow the programme's instructions for handling supplied datasets and model artifacts.
