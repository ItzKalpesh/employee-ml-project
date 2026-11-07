git switch -c task15-fair-pay-band-recommender# Task 15 — Recommend Fair Pay Bands

## Executive summary

Task 15 was completed using 2,934 salary-training records across 47 roles. Three approaches were compared on the same held-out test set: an average-by-role baseline, Linear Regression, and Gradient Boosting. Linear Regression produced the lowest MAE and highest R² in this split and was selected for the illustrative low/mid/high recommendation bands.

The protected-attribute file was opened only after model fitting, held-out evaluation, recommendation-band calibration, and out-of-fold prediction generation were complete. Gender and career-gap duration were not used as model inputs.

## 1. Data and feature selection

- Dataset: `salary_training.csv`
- Records: 2,934
- Distinct roles: 47
- Target: `offered_annual_fixed`

Selected job-related predictors:
- `department_id`
- `role_id`
- `work_location`
- `job_level`
- `prior_experience_years`
- `skills_count`
- `market_index`

Excluded from model predictors:
- Gender and age (protected attributes)
- `career_gap_months` (reserved for audit; prevents direct career-break penalty)
- `highest_education` (excluded to reduce reliance on a potentially inequitable credential proxy)
- Existing 2026 band columns (`band_min_2026`, `band_mid_2026`, `band_max_2026`) to avoid anchoring predictions to the existing pay bands
- Employee identifiers, hire dates/year, and source metadata

No protected-attribute column was passed to the model.

## 2. Experimental design

A role-stratified split with fixed seeds was used:
- Training: 1,994
- Calibration: 353
- Held-out test: 587

The average-by-role baseline used training-set role means, with the overall training mean as a fallback. The two trained models used the same features and training rows. The calibration partition was used only to estimate residual quantiles for recommendation bands. The test partition was used only for final metrics and band-coverage evaluation.

## 3. Model comparison

Metrics are calculated on the same 587-row held-out test set. MAE and R² are in the target's original units; the dataset does not specify a currency code, so values are not labelled as INR or another currency.

| Model | MAE | R² |
|---|---:|---:|
| Average by role baseline | 115,196.32 | 0.9348 |
| Linear Regression | 82,141.38 | 0.9662 |
| Gradient Boosting | 93,211.80 | 0.9431 |

Linear Regression was selected because it had the lowest MAE and highest R² in this experiment. Both trained models outperformed the average-by-role baseline.

## 4. Low / mid / high recommendation bands

The selected Linear Regression model's residuals on the separate calibration set were used to construct a range:
- Low = prediction + 10th-percentile calibration residual
- Mid = prediction + median calibration residual
- High = prediction + 90th-percentile calibration residual

Residual adjustments:
- Low adjustment: -125,975.44
- Mid adjustment: 8,447.57
- High adjustment: 110,630.56

The bands are floored at zero and ordered low ≤ mid ≤ high. On the held-out test set, 78.9% of actual salaries fell within the low-to-high range. This is empirical coverage on one split, not a guaranteed confidence interval or promise of future coverage.

A row-level test recommendation file is generated locally at `reports/task15_salary_recommendations_test.csv`. It contains employee identifiers and salary information and should remain private; it is not intended for public repository submission.

## 5. Fairness audit

After the model and recommendation work was completed, `unlock_CX-15_protected_attributes.csv` was opened solely for auditing. The `salary_hire` records were matched one-to-one to `salary_training.csv` using `person_ref` and `hire_id`. The Vault file contained 5,317 total rows, of which 2,934 were salary-hire audit records. Age was not used.

For the group audit, five-fold stratified out-of-fold predictions were generated for all 2,934 salary records before opening the Vault. Each employee's audit prediction therefore comes from a fold model that did not train on that employee. The `group_gap()` method follows Task 12: maximum group mean minus minimum group mean.

### Gender

| Gender group | Count | Historical mean | OOF predicted mean |
|---|---:|---:|---:|
| Female | 1,222 | 806,183.95 | 811,555.66 |
| Male | 1,652 | 855,125.86 | 851,835.18 |
| Other | 60 | 839,786.40 | 828,559.37 |

- Historical group gap: 48,941.91
- Predicted group gap: 40,279.52

The gender gap is smaller in the OOF predictions than in historical offered salaries in this dataset. This does not establish that the model is fair; other included features may act as proxies, and aggregate gaps do not account for role/level composition.

### Career-gap duration

Career-gap duration was excluded from model predictors and used only to form audit groups.

| Career-gap group | Count | Historical mean | OOF predicted mean |
|---|---:|---:|---:|
| 1-12 months | 246 | 799,482.05 | 819,655.10 |
| 13-24 months | 94 | 806,495.87 | 842,961.01 |
| 25+ months | 45 | 788,979.73 | 768,855.71 |
| No gap | 2,549 | 839,633.04 | 836,874.97 |

- Historical group gap: 50,653.30
- Predicted group gap: 74,105.30

The predicted multi-category career-gap group gap is larger than the historical group gap. Excluding `career_gap_months` prevents a direct penalty for career breaks, but does not remove differences associated with role, experience, skills, and other model inputs. This result is a signal for further review, not proof of discrimination or causation.

## 6. What was changed and what the gaps mean

Changes made before model fitting:
1. Gender and age were not included as predictors.
2. Career-gap duration was excluded from predictors and reserved for post-model auditing.
3. Education was excluded to reduce reliance on a potentially inequitable credential proxy.
4. Existing salary-band columns were excluded to avoid simply reproducing the current band structure.
5. Employee identifiers, hire dates/year, and source metadata were excluded.

No gender-specific salary adjustment or arbitrary parity correction was applied. Such a correction would use a protected attribute to set individual pay and would conceal rather than explain the underlying causes. The measured career-gap gap remains a concern and should prompt a role- and level-adjusted review using consistent job evaluation and market benchmarks.

## 7. Limitations and responsible use

- Historical offered salaries may encode prior inequities, negotiation differences, and time-related effects. A model trained on historical labels cannot guarantee to remove those patterns.
- Group means are descriptive, not causal. This audit does not adjust group means for role, job level, experience, skills, or location.
- Smaller career-gap groups have fewer records (including the 25+ month group), so their averages are less stable.
- A reduced gender group gap does not prove equal treatment or absence of proxy effects.
- The empirical low/mid/high coverage comes from one split and is not a guaranteed interval.
- The dataset does not state a currency code in the supplied CSV; values are reported in the target's original units.
- The model is a decision-support prototype. HR and managers must review role scope, level, market data, internal equity, and applicable compensation policies before making an offer.

## 8. Evidence files

- `notebooks/15_fair_pay_band_recommender.ipynb` — reproducible workflow.
- `reports/task15_model_metrics.csv` — baseline and model comparison.
- `reports/task15_group_gap_analysis.csv` — gender and career-gap group means and gaps.
- `reports/task15_summary.json` — machine-readable summary.
- `reports/task15_salary_recommendations_test.csv` — local test-row recommendations; contains employee identifiers and salary values and should not be publicly committed.
