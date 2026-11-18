# Model Card — Fair Pay Band Recommender

## Purpose
Estimate an illustrative salary reference and low/mid/high recommendation range from job-related attributes to support compensation review. It must not set or automatically approve employee pay.

## Data
- Dataset: `salary_training.csv`.
- Rows: 2,934; distinct roles: 47.
- Target: `offered_annual_fixed`.
- Predictors: department, role, work location, job level, prior experience, skills count, market index.
- Excluded: gender, age, career-gap duration, highest education, existing 2026 pay bands, employee identifiers, hire dates/year, and source metadata.
- Currency code is not specified in the source dataset; metrics are in original target units.

## Method
- Selected model: Linear Regression.
- Role-stratified fixed-seed split: 1,994 training / 353 calibration / 587 held-out test.
- Separate calibration partition used for residual quantiles.
- Recommendation bands use 10th, 50th, and 90th percentile calibration residuals.

## Metrics
All models were evaluated on the same 587-row held-out test set.

| Model | MAE | R² |
|---|---:|---:|
| Average-by-role baseline | 115,196.32 | 0.9348 |
| Linear Regression | 82,141.38 | 0.9662 |
| Gradient Boosting | 93,211.80 | 0.9431 |

Linear Regression was selected because it achieved the lowest MAE and highest R² in this experiment.

The low/mid/high recommendation bands were calibrated using a separate 353-row calibration partition. On the held-out test set, 78.9% of actual salaries fell within the low-to-high range. This is empirical coverage from one split, not a guaranteed prediction interval.

## Explanations
Inputs are job-related predictors listed above. A worked prediction example should be copied from a sanitized test example; no employee-level salary example is included in the supplied audit extract.

## Fairness
Protected attributes were not used as model predictors. Gender and career-gap duration were used only for post-model auditing.

| Group comparison | Historical gap | OOF predicted gap |
|---|---:|---:|
| Gender | 48,941.91 | 40,279.52 |
| Career-gap duration | 50,653.30 | 74,105.30 |

The predicted gender group gap was smaller than the historical gap. However, the predicted career-gap group gap was larger than the historical gap.

These are descriptive aggregate differences, not causal evidence. The analysis does not adjust for role, job level, experience, skills or location. The larger predicted career-gap difference requires further investigation.

## Limits and risks
- Historical offered salaries may encode prior inequities and negotiation effects.
- Aggregate group gaps are not adjusted for role, level, experience, skills, or location.
- Smaller groups have unstable estimates.
- 78.9% range coverage comes from one split and is not guaranteed.
- Human review of role scope, level, market data, internal equity, and policy is mandatory.

## Version and owner
- Evidence: `reports/task15_model_metrics.csv`, `reports/task15_fair_pay_report.md`.
- Model artifact/version: not identified in supplied inventory; confirm exact saved estimator path and version before release.
- Owner: CortexHR project team; named operational owner not recorded.
