# CortexHR — Employee Analytics Project

## Project Overview

CortexHR is an employee analytics project developed as part of the Aura Workforce AI/ML track. Phase 1 focuses on auditing employee attrition data, building a reusable feature pipeline, and evaluating honest baseline models.

**Repository:** [employee-ml-project](https://github.com/ItzKalpesh/employee-ml-project)

## Project Workflow

Raw Data → Data Audit → Feature Engineering → Baseline Models → Model Evaluation → API and Monitoring

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

## Upcoming Tasks

- **Task 4:** Honest evaluation and risk bands.
- **Task 5:** Further project implementation, following the supplied task requirements.

These sections will be updated as the remaining tasks are completed.

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