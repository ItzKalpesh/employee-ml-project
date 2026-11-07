# Task 13 — Attrition Model V2: Honest Baseline Comparison

## Dataset
- Labelled snapshots: **2,389**
- Leavers: **349 (14.61%)**
- Stayers: **2,040 (85.39%)**
- Predictors: **45** (39 numeric, 6 categorical)

## Evaluation protocol
The outer evaluation uses the Task 3 folds: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`. Hyperparameters are tuned only inside each outer training partition using 3-fold stratified CV and average precision. Preprocessing is fitted inside each fold.

## Pooled out-of-fold results
| Model | ROC-AUC | PR-AUC | Precision @ 0.50 | Recall @ 0.50 | F1 @ 0.50 | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Task 3 Logistic Regression | 0.6995 | 0.2971 | 0.2565 | 0.5960 | 0.3586 | 0.2070 |
| LightGBM V2 | 0.7030 | 0.3383 | 0.3015 | 0.5072 | 0.3782 | 0.1730 |
| XGBoost V2 raw | 0.7176 | 0.3405 | 0.2763 | 0.5415 | 0.3659 | 0.1866 |
| XGBoost V2 sigmoid calibrated | 0.7109 | 0.3320 | 0.6667 | 0.0172 | 0.0335 | 0.1136 |

## Improvement and benchmark context
Raw XGBoost improved ROC-AUC by **+0.0181** and PR-AUC by **+0.0434** over the Task 3 Logistic Regression baseline. The supplied Random Forest reference is ROC-AUC **0.715** and PR-AUC **0.336**. The XGBoost result is above that reference by **+0.0026** ROC-AUC and **+0.0045** PR-AUC. This is a reference comparison, not a same-run Random Forest evaluation.

## Tuning
The XGBoost grid tested `max_depth` {2, 3} and `n_estimators` {150, 300}. Learning rate was fixed at 0.05; subsample and column sample at 0.8; L2 regularization at 1.0. The final full-data selection chose `{'model__max_depth': 2, 'model__n_estimators': 150}`. The full-data CV score is for final parameter selection only, not an unbiased performance estimate. See `task13_tuning_log.csv`.

## Calibration
Raw XGBoost Brier score: **0.1866**; sigmoid-calibrated Brier score: **0.1136**. Raw log loss: **0.5544**; calibrated log loss: **0.3771**. Calibration improved these probability-error measures in the nested OOF check. The 0.50 threshold is not an operational intervention threshold; calibration shifts the probability scale and very few calibrated predictions exceed 0.50.

## Versioned artifact
- Version: `attrition-v2`
- Artifact: `models/attrition/attrition-v2/model.joblib`
- Metadata: `models/attrition/attrition-v2/metadata.json`
- Calibration: sigmoid using 5-fold `CalibratedClassifierCV`.

## Limitations and responsible use
This is internal validation on one historical dataset, not prospective validation. Benchmark values may differ due to feature and environment differences. Model scores should support voluntary, supportive human review only and must not independently determine hiring, promotion, compensation, discipline, or termination.
