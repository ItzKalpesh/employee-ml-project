# Task 14 — Explain Every Person's Risk

## 1. Objective
Score all 430 active employees with the Task 13 `attrition-v2` model, assign the company's risk bands, identify the top three SHAP drivers for each employee, translate those drivers into plain English, match the supplied sample output schema, and provide a 10-row human-review sample.

## 2. Inputs and reused project components
- Scoring population: `data/attrition_scoring_2026.csv` — 430 rows and 430 unique employees.
- Monthly attendance: `data/attendance_monthly_features.csv` — 7339 rows.
- Monthly payroll: `data/payroll_monthly_features.csv` — 7355 rows.
- Output schema reference: `data/sample_attrition_risk.csv` — 430 rows and 11 columns.
- Model: `models/attrition/attrition-v2/model.joblib`.
- Model metadata: `models/attrition/attrition-v2/metadata.json`.
- Feature engineering: reused Task 2 `src.features.build_features.build_features`.
- Risk bands: reused Task 4 `cortexhr_helpers.risk_bands`.

The scoring CSV initially contained 34 source columns, whereas the Task 13 model requires 45 predictors. The missing engineered features were created by reusing the existing Task 2 feature builder; no new model predictors or ad-hoc imputation rules were invented for this task.

## 3. Methodology
1. Load the 430 scoring snapshots and supplied attendance/payroll histories.
2. Apply the existing Task 2 feature builder. It aggregates attendance and payroll records for each employee snapshot using records no later than the snapshot month, then computes the established derived fields.
3. Validate all 45 model features against Task 13 metadata.
4. Load the versioned `attrition-v2` calibrated XGBoost model and generate calibrated `predict_proba` scores for `left_within_12m`.
5. Apply the existing Task 4 company risk-band helper. The helper assigns High at or above the 90th percentile, Medium at or above the 70th percentile but below High, and Low otherwise.
6. Calculate TreeSHAP values for each of the five XGBoost estimators inside the calibrated ensemble. Sum one-hot encoded contributions back to the original feature names. Use the three largest positive grouped contributions for each employee.
7. Render cautious plain-English statements and export the 430-row report in the exact sample column order.

## 4. Additional implementation decisions — explicitly disclosed
These choices were needed to implement SHAP explanations and readable reasons; they are not separately stated as mandatory choices in the task instructions:
- **SHAP explainer:** TreeSHAP with interventional feature perturbation on each of the five XGBoost fold estimators.
- **Background sample:** 40 rows sampled from the 430-person scoring cohort using `random_state=42`, because the original model training data is not part of the Task 14 input bundle. Explanations are therefore relative to this scoring cohort.
- **Feature grouping:** one-hot SHAP contributions are summed back to their source feature among the 45 model inputs, so a categorical feature is reported as one reason rather than multiple dummy columns.
- **Reason selection:** choose the three largest positive grouped SHAP contributions, because the task requests drivers that explain higher risk.
- **Wording:** state that a feature contributed to the model estimate; do not claim it caused attrition.
- **Output formatting:** risk scores are rounded to three decimals to match the supplied sample; risk bands are calculated using unrounded scores.

## 5. Important SHAP/calibration limitation
The final risk score is the probability produced by the calibrated ensemble. TreeSHAP was applied to the underlying raw XGBoost estimators before sigmoid calibration. Therefore, SHAP values identify learned drivers in the underlying XGBoost models, but they are **not an exact additive decomposition of the final calibrated probability**. This distinction is included in the notebook and output note.

## 6. Results
- Employees scored: **430**
- Unique employees: **430**
- Risk score minimum: **0.0259**
- Risk score maximum: **0.4244**
- Mean risk score: **0.1209**

| Risk band | Employees |
|---|---:|
| High | 43 |
| Medium | 86 |
| Low | 301 |

The counts match the sample's 43 High, 86 Medium, and 301 Low distribution. This is expected from the supplied Task 4 quantile rule and score distribution; the sample's baseline model scores themselves are not reused.

## 7. Global SHAP summary
Top global drivers by mean absolute grouped SHAP contribution:
- Engagement score: 0.0884
- Manager changes in the last 12 months: 0.0331
- Tenure: 0.0317
- Pay relative to role midpoint: 0.0296
- Work-from-home share: 0.0265
- Commute distance: 0.0233
- Last performance rating: 0.0161
- Historical late arrivals: 0.0161

Chart: `evidence/task14_shap_summary.png`.

## 8. Deliverables
- Notebook: `notebooks/14_attrition_risk_explanations.ipynb`
- Full output: `reports/task14_attrition_risk_report.csv`
- Ten-row review sample: `reports/task14_review_sample_10.csv`
- SHAP summary chart: `evidence/task14_shap_summary.png`
- Machine-readable summary: `reports/task14_summary.json`

## 9. Validation and limitations
- All 430 employee IDs were unique in the scoring input and output.
- All 45 model predictors were present after reusing the Task 2 feature builder.
- The output has exactly the same 11 columns and order as the supplied sample.
- Three positive SHAP reasons were generated for each employee.
- No employee outcome labels are present in the scoring dataset; this is a scoring/explanation task, not an accuracy evaluation.
- SHAP reasons are model associations, not causal explanations or evidence of employee intent.
- Tenure, attendance, overtime, pay, engagement, commute, and manager-change signals can reflect circumstances outside an employee's control. They must be reviewed in context.
- Scores are decision-support signals only. They must not independently determine hiring, promotion, compensation, discipline, or termination.

## 10. Environment compatibility note
The artifact loaded and produced predictions in the analysis environment running scikit-learn **1.8.0**, but joblib emitted compatibility warnings indicating the artifact had been saved with scikit-learn **1.9.1**. Prediction execution succeeded here; however, final acceptance should include rerunning the notebook in the project's matching scikit-learn version to avoid relying on cross-version deserialization behavior.
