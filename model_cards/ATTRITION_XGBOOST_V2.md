# Model Card — Employee Attrition Risk (XGBoost v2)

## Purpose
Estimate the likelihood that an employee leaves within 12 months, to support voluntary, supportive HR review. It must not independently determine hiring, promotion, compensation, discipline, termination, or access to opportunities.

## Data
- Target: `left_within_12m`.
- Historical labelled snapshots reported in Task 13: 2,389 rows; 349 leavers (14.61%), 2,040 stayers (85.39%).
- Features: 45 predictors, including role/department, work arrangement, tenure/experience, compensation-related, performance/engagement, attendance and workload features.
- Excluded: employee identifiers, exit dates/reasons/interview status, F&F settlement amount, observation/resignation dates, source/row IDs, and target-derived voluntary-exit fields.
- Exact dataset date range and row-level data lineage: **not stated in the available metadata/report; verify from source data dictionary before publication.**

## Method
- Algorithm: XGBoost classifier.
- Outer evaluation: 5-fold `StratifiedKFold(shuffle=True, random_state=42)`.
- Hyperparameter tuning: 3-fold stratified CV inside each outer training fold, average-precision scoring.
- Preprocessing is fitted inside each fold.
- Calibration: sigmoid, `CalibratedClassifierCV` with 5-fold stratified CV.
- Selected full-data parameters: `max_depth=2`, `n_estimators=150`; this full-data CV score is for selection, not unbiased performance estimation.

## Metrics
Nested out-of-fold results:

| Metric | Raw XGBoost | Sigmoid-calibrated XGBoost |
|---|---:|---:|
| ROC-AUC | 0.7176 | 0.7109 |
| PR-AUC | 0.3405 | 0.3320 |
| Precision at 0.50 | 0.2763 | 0.6667 |
| Recall at 0.50 | 0.5415 | 0.0172 |
| F1 at 0.50 | 0.3659 | 0.0335 |
| Accuracy at 0.50 | 0.7258 | 0.8552 |
| Brier | 0.1866 | 0.1136 |

Reference benchmarks: balanced Logistic Regression ROC-AUC 0.713 / PR-AUC 0.332; Random Forest reference ROC-AUC 0.715 / PR-AUC 0.336. Raw XGBoost exceeds the supplied Random Forest reference slightly, but this is not a same-run comparison. Dummy always-stays baseline has 85.4% accuracy while catching no leavers.

**High-band precision/recall:** a separate top-X%/High-band evaluation is not present in the supplied evidence. The 0.50-threshold figures above must not be relabelled as High-band metrics.

## Explanations
Feature-level global importance and a verified worked individual example were not included in the supplied metadata excerpt. Add these from the model explanation report before claiming particular drivers or presenting an employee-specific explanation.

## Fairness
The available Task 12 resume-screening twin-score audit is not an attrition fairness audit. Attrition subgroup fairness results were not supplied here. Do not claim attrition fairness has been established.

## Limits and risks
- Calibrated recall at 0.50 is only 1.72%; the high accuracy is misleading under class imbalance.
- Calibration improves Brier score but changes the operating point substantially.
- Internal validation on one historical dataset is not prospective validation.
- Feature proxies and temporal drift may affect results.
- Use only as a supportive review signal; human review and employee context are required.

## Version and owner
- Artifact: `models/attrition/attrition-v2/model.joblib`
- Metadata: `models/attrition/attrition-v2/metadata.json`
- Version: `attrition-v2`
- Owner: CortexHR project team; named operational owner not recorded.
- Evaluation source: `reports/task13_attrition_model_v2_report.md`.
