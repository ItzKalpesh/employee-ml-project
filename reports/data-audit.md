# Task 1: Employee Attrition Data Audit

## 1. Objective

Audit the employee attrition dataset before feature engineering and model development. The audit covers structure, missing values, duplicates, outliers, categories, invalid measurements, class imbalance and potential data leakage.

## 2. Dataset Overview

- Rows: 2389
- Columns: 42
- Numeric columns: 28
- Exact duplicate rows: 0

### Column data types

| Column                          | Data type   |   Missing count |
|:--------------------------------|:------------|----------------:|
| row_id                          | int64       |               0 |
| employee_id                     | str         |               0 |
| observation_date                | str         |               0 |
| department_id                   | str         |               0 |
| role_id                         | str         |               0 |
| job_level                       | int64       |               0 |
| work_location                   | str         |               0 |
| work_mode                       | str         |               0 |
| employment_type                 | str         |               0 |
| highest_education               | str         |              15 |
| tenure_months                   | int64       |               0 |
| total_experience_years          | float64     |               0 |
| previous_employers_count        | int64       |               0 |
| commute_distance_km             | float64     |              55 |
| annual_fixed_pay                | int64       |               0 |
| comp_ratio                      | float64     |               0 |
| raises_received                 | int64       |               0 |
| last_raise_pct                  | float64     |             202 |
| months_since_last_raise         | int64       |               0 |
| promotions_received             | int64       |               0 |
| months_since_last_promotion     | float64     |            1459 |
| internal_transfers              | int64       |               0 |
| last_performance_rating         | float64     |             182 |
| last_engagement_score           | float64     |             528 |
| manager_changes_12m             | int64       |               0 |
| training_hours_12m              | float64     |               0 |
| attendance_rate_3m              | float64     |               0 |
| late_arrivals_3m                | int64       |               0 |
| avg_overtime_hours_per_month_3m | float64     |               0 |
| avg_hours_worked_3m             | float64     |               0 |
| wfh_share_3m                    | float64     |               0 |
| unpaid_leave_days_6m            | float64     |               0 |
| paid_leave_days_6m              | int64       |               0 |
| dept_attrition_rate_prior_12m   | float64     |               0 |
| left_within_12m                 | int64       |               0 |
| voluntary_left_within_12m       | int64       |               0 |
| source                          | str         |               0 |
| exit_date                       | str         |            2040 |
| resignation_date                | str         |            2068 |
| exit_reason                     | str         |            2040 |
| exit_interview_done             | str         |            2040 |
| fnf_settlement_amount           | str         |            2040 |

## 3. Missing-Value Analysis

Columns containing missing values: 11 out of 42.

| Column                      |   Missing Count |   Missing Percentage |
|:----------------------------|----------------:|---------------------:|
| resignation_date            |            2068 |                86.56 |
| exit_date                   |            2040 |                85.39 |
| exit_reason                 |            2040 |                85.39 |
| fnf_settlement_amount       |            2040 |                85.39 |
| exit_interview_done         |            2040 |                85.39 |
| months_since_last_promotion |            1459 |                61.07 |
| last_engagement_score       |             528 |                22.1  |
| last_raise_pct              |             202 |                 8.46 |
| last_performance_rating     |             182 |                 7.62 |
| commute_distance_km         |              55 |                 2.3  |
| highest_education           |              15 |                 0.63 |

## 4. Duplicate Record Analysis

- Exact duplicate rows: 0
- Duplicate row IDs: 0
- Repeated employee ID occurrences: 6
- Duplicate rows after excluding `row_id`: 6

The six repeated employee records differ only by `row_id` in the notebook inspection. Investigate the source and intended meaning of these records before deciding whether to remove them.

## 5. Attrition Distribution

| Outcome   |   Records |   Percentage |
|:----------|----------:|-------------:|
| Stayed    |      2040 |        85.39 |
| Left      |       349 |        14.61 |

The target is imbalanced. Evaluate future models with precision, recall, F1-score and suitable threshold-independent metrics in addition to accuracy.

## 6. Outlier Detection

| Feature             |   IQR Outliers |   Z-score Outliers |
|:--------------------|---------------:|-------------------:|
| annual_fixed_pay    |             94 |                 26 |
| avg_hours_worked_3m |             48 |                 15 |
| tenure_months       |             74 |                 42 |

IQR and Z-score methods flag potential outliers using different criteria. A flagged observation is not automatically an error; investigate plausible extreme values before excluding them.

## 7. Category Consistency Checks

The following columns have category values that collapse to fewer unique values after trimming whitespace and ignoring case. Review them before normalizing categories.

| Column        |   Raw unique values |   Normalized unique values |
|:--------------|--------------------:|---------------------------:|
| work_location |                  16 |                         12 |

## 8. Invalid Measurement Checks

These checks flag values outside the stated bounds or negative values in fields expected to be non-negative. Confirm each rule against the data dictionary before correcting any record.

| Column                          | Validation rule   |   Invalid non-missing values |
|:--------------------------------|:------------------|-----------------------------:|
| attendance_rate_3m              | 0 to 1            |                            2 |
| wfh_share_3m                    | 0 to 1            |                          213 |
| last_performance_rating         | 1 to 5            |                            0 |
| last_engagement_score           | 1 to 5            |                            0 |
| tenure_months                   | Non-negative      |                            4 |
| total_experience_years          | Non-negative      |                           10 |
| previous_employers_count        | Non-negative      |                            0 |
| commute_distance_km             | Non-negative      |                            0 |
| annual_fixed_pay                | Non-negative      |                            0 |
| raises_received                 | Non-negative      |                            0 |
| promotions_received             | Non-negative      |                            0 |
| late_arrivals_3m                | Non-negative      |                            0 |
| avg_overtime_hours_per_month_3m | Non-negative      |                            0 |
| avg_hours_worked_3m             | Non-negative      |                            0 |
| unpaid_leave_days_6m            | Non-negative      |                            0 |
| paid_leave_days_6m              | Non-negative      |                            0 |

## 9. Data Leakage Review

| Column                    | Decision                                             |
|:--------------------------|:-----------------------------------------------------|
| row_id                    | Exclude from model inputs                            |
| employee_id               | Exclude from model inputs                            |
| observation_date          | Use to enforce the prediction-time boundary          |
| left_within_12m           | Target label; never use as an input feature          |
| voluntary_left_within_12m | Outcome-related label; never use as an input feature |
| exit_date                 | Exclude: exit outcome information                    |
| resignation_date          | Exclude: resignation outcome information             |
| exit_reason               | Exclude: post-outcome information                    |
| exit_interview_done       | Exclude: post-outcome information                    |
| fnf_settlement_amount     | Exclude: post-outcome information                    |

Monthly attendance and payroll features must not use records after the relevant observation date. The target is `left_within_12m`.

## 10. Data-Quality Decisions

| Issue                          | Decision                                                          |
|:-------------------------------|:------------------------------------------------------------------|
| Missing numeric values         | Use training-fitted imputation where appropriate.                 |
| Missing categorical values     | Use training-fitted categorical imputation where appropriate.     |
| Repeated employee IDs          | Investigate record meaning before removing records.               |
| Potential outliers             | Investigate; do not automatically delete plausible extremes.      |
| Category inconsistencies       | Review and normalize equivalent values consistently.              |
| Invalid measurements           | Validate against the data dictionary and document any correction. |
| Target and post-outcome fields | Exclude from predictive input features.                           |
| Employee identifiers           | Exclude from predictive input features.                           |
| Class imbalance                | Use appropriate classification metrics during model evaluation.   |

## 11. Answer-Key Comparison

Pending: compare these findings with the supplied answer-key notes and planted-issue material. Record which issues were initially missed and what decisions changed. This comparison has not been verified from the uploaded notebook alone.

## 12. Conclusion

The audit documents dataset structure, missingness, repeated records, class imbalance, outlier counts, category consistency checks, bounded/non-negative measurement checks and leakage decisions. These findings provide the basis for consistent preprocessing and feature engineering. The answer-key comparison must be completed before claiming the audit is fully reconciled.
