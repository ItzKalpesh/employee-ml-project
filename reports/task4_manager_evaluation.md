# Task 4 — Manager Evaluation Note

## Purpose
The model ranks historical employee records by their score for `left_within_12m`. It can help HR prioritize supportive human review, but it must not make employment decisions.

## Results
- **ROC-AUC:** 0.699; benchmark: 0.713.
- **PR-AUC:** 0.297; benchmark: 0.332.
- **Observed leaver rate:** 14.61%.
- **High band:** 239 employees, including 83 historical leavers.
- **High-band leaver rate:** 34.73%.
- **Historical leavers captured in High band:** 23.78%.
- **Top-10% lift:** 2.39× the overall leaver base rate.

## Risk bands
High is the top-scoring group, Medium is the next 20%, and Low is the remainder, according to the supplied quantile-based rule. These are relative rankings, not validated business thresholds.

## Limitations and responsible use
Predictions are out-of-fold, but historical patterns may not generalize to future employees. Calibration, data quality, and potential historical bias remain concerns; scores should not be interpreted as verified individual probabilities without adequate calibration.

HR should use scores only as one signal for supportive check-ins, verify the employee's current context, and consider other relevant evidence. Never use scores alone for hiring, promotion, compensation, performance ratings, discipline, or termination. Continue monitoring performance, calibration, and fairness.
