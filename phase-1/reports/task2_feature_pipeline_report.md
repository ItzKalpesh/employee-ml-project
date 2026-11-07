# Task 2 — Reusable Feature Pipeline

## 1. Objective

Build a reusable feature-engineering and preprocessing pipeline for the CortexHR employee attrition dataset. The pipeline combines employee snapshots with historical attendance and payroll records while preventing identifier and target leakage.

## 2. Inputs

The pipeline uses the following datasets:

- `data/attrition_dataset.csv`
- `data/attendance_monthly_features.csv`
- `data/payroll_monthly_features.csv`

Attendance and payroll records are aggregated separately and joined to the corresponding employee snapshot. Monthly records after the snapshot's observation month are excluded.

## 3. Engineered Features

| Feature | Definition |
|---|---|
| `tenure_years` | `tenure_months / 12` |
| `raise_overdue` | True when months since last raise is greater than 12 |
| `unpaid_per_month` | Six-month unpaid leave days divided by 6 |
| `attendance_gap` | `1 - attendance_rate_3m` |
| `overtime_load` | Average overtime hours per month over the supplied three-month measure |

## 4. Preprocessing

The preprocessing pipeline uses separate branches for numeric, boolean, and categorical input features.

- Numeric features: median imputation followed by standard scaling.
- Boolean feature: most-frequent imputation followed by one-hot encoding.
- Categorical features: most-frequent imputation followed by one-hot encoding.
- Unknown categories: handled using `OneHotEncoder(handle_unknown="ignore")`.
- Leakage validation: rejects known identifier, target, source, date, and post-outcome columns.
- Unused columns: dropped from the transformed model input.

### Separate Attendance and Payroll Transformers

- `AttendanceFeatureTransformer` cleans and aggregates attendance records independently.
- `PayrollFeatureTransformer` cleans and aggregates payroll records independently.
- Their resulting features are joined to the matching employee snapshots before preprocessing.

The resulting employee-level features are passed through the reusable
scikit-learn preprocessing pipeline.

## 5. Training and Held-Out Data

The build process uses a stratified 80/20 split with random seed 42. Preprocessing is fitted on the training portion only. The held-out portion is reserved for the later model evaluation task.

Previously verified split:
- Total labelled rows: 2,389
- Training rows: 1,911
- Held-out rows: 478

## 6. Package and Artifacts

- Package: `cortexhr_features`
- Feature version: `features-1.0.0`
- Build command: `python -m cortexhr_features.build`
- Saved pipeline: `models/feature_pipeline.joblib`
- Metadata: `models/metadata.json`

The saved pipeline is loaded for transformation rather than being refitted on new input.

## 7. Verification

The following command was run in the Docker environment:
`python -m cortexhr_features.build`


The feature pipeline was rebuilt successfully inside Docker, and all
six automated tests passed.

- **Build:** Successful.
- **Feature version:** `features-1.0.0`.
- **Total labelled rows:** 2,389.
- **Training rows:** 1,911.
- **Held-out rows:** 478.
- **Transformed training shape:** `(1911, 92)`.
- **Training-only fitting:** Verified.
- **Automated tests:** 4 passed.

The tests cover output shape, missing-value handling, reproducibility,
and engineered feature values.

Tests were run with:

`python -m pytest -q tests/test_pipeline.py`

**Verified result:** all six tests passed. The tests check transformed output shape, absence of missing values, reproducibility, and required engineered-feature calculations.

## 8. Limitations and Remaining Checks

The implementation uses separate `AttendanceFeatureTransformer` and `PayrollFeatureTransformer` classes. Both transform their source records independently, exclude records after each employee snapshot date, and join the resulting features back to the corresponding employee snapshot.

The Docker build completed successfully, and all six automated tests passed. Remaining work is final repository review and GitHub handoff.
