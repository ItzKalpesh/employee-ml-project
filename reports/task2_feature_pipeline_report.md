# Task 2: Reusable Feature Engineering and Pipeline

## 1. Objective

The objective is to build a reusable feature engineering module and a Scikit-learn preprocessing pipeline for employee attrition data.

## 2. Data Sources

The project uses three datasets:

- Employee attrition dataset
- Monthly attendance features
- Monthly payroll features

The employee dataset contains 2,389 rows and 42 original columns. The updated feature engineering function produces a dataset with 2,389 rows and 48 columns.

## 3. Feature Engineering

The reusable feature builder is implemented in `src/features/build_features.py`.

The engineered features include:

- **Attendance rate:** Average recorded attendance rate.
- **Late count:** Total recorded late arrivals.
- **Average overtime:** Average monthly overtime hours.
- **Tenure:** Employee tenure in months.
- **Months since last revision:** Derived from the available source field.

Attendance and payroll records are filtered according to each employee snapshot's observation month. Duplicate payroll records are removed before payroll aggregation. Employee snapshots without matching monthly history are retained.

The salary-to-department-median ratio is calculated by a fitted transformer in `src/features/pipeline.py`. Department medians are learned during fitting and reused during transformation.

## 4. Preprocessing Pipeline

The reusable preprocessing pipeline is implemented in `src/features/pipeline.py`.

**Numerical features:**
- Missing values are imputed using the median.
- Features are scaled using `StandardScaler`.

**Categorical features:**
- Missing values are imputed using the most frequent value.
- Categories are encoded using `OneHotEncoder`.
- Unknown categories are handled using `handle_unknown="ignore"`.

The final preprocessing stage uses six numerical features and five categorical features.

## 5. Saving and Versioning

The fitted preprocessing pipeline is saved using Joblib as:

`models/feature_pipeline.joblib`

Feature metadata is saved as:

`models/metadata.json`

The metadata records the feature version and the numerical and categorical feature lists. The current feature version is `features-1.0.0`.

## 6. Testing and Validation

Automated tests are implemented in `tests/test_pipeline.py`.

Three tests passed:

- Output shape validation
- Missing-value handling after transformation
- Reproducibility of the preprocessing pipeline

The saved pipeline was also loaded and used to transform the engineered dataset.

## 7. Handling Missing Data

Some employee snapshots have no matching monthly attendance or payroll history. Missing values are preserved during feature engineering and handled by the preprocessing pipeline instead of automatically replacing them with zero.

Missing late-arrival values remain missing when all records in a group are missing, allowing the preprocessing pipeline to handle them appropriately.

## 8. Data Leakage Prevention and Limitations

The preprocessing pipeline is fitted on the training split. The department-median transformer learns its medians during fitting and reuses them during transformation.

The current work validates the feature engineering and preprocessing workflow. It does not establish predictive accuracy, model performance, or fairness. Further validation is needed before using these features for employee-related decisions.

## 9. Docker Execution and Final Validation

The command-line pipeline was executed successfully inside Docker using `src/features/run_pipeline.py`.

Results:

- Input employee snapshots: 2,389
- Transformed feature matrix: 2,389 rows × 85 columns
- Feature version: `features-1.0.0`
- Saved Joblib pipeline and metadata loaded successfully
- Automated tests: 3 passed

The successful notebook and Docker executions, together with the passing tests, validate the technical preprocessing workflow. They do not establish predictive model accuracy or fairness.

## 10. Conclusion

A reusable feature engineering module and preprocessing pipeline have been developed for the employee attrition dataset. The workflow supports snapshot-aware monthly feature aggregation, missing-value imputation, numerical scaling, categorical encoding, versioned artifact storage, and reproducible preprocessing.

Automated tests and Docker execution verify that the pipeline operates successfully on the project data. Predictive performance and fairness remain outside the scope of this task.