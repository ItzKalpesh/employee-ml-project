# Model Card — Attendance Anomaly Detector

## Purpose
Flag unusual monthly attendance patterns for investigation and data-quality review. A flag is not proof of misconduct, absenteeism abuse, or poor performance.

## Data
- Source file in metadata: `data/attendance_monthly_features.csv`.
- Training rows: 7,339.
- Features: scheduled days, present days, half days unpaid, paid leave, unpaid absence, longest unpaid streak, late arrivals, average hours, overtime hours, attendance rate.
- Dataset date range and exact labelled evaluation sample: not present in the supplied metadata excerpt.

## Method
- Algorithm: Isolation Forest.
- Version: `1.0.0`.
- Contamination parameter: 0.03.
- Additional reason rules: attendance rate below 0.75; unpaid streak at least 5 days; unpaid absence at least 5 days; late arrivals at least 5.

## Metrics
The supplied anomaly baseline comparison reports:
- Precision: 0.403
- Recall: 0.593
- Flagged: 221
- Injected/reference anomalies: 150

These are anomaly-detection results, not ROC-AUC/PR-AUC. The exact evaluation protocol and whether the injected anomalies fully represent production anomalies should be confirmed from the Task 5 report before external claims.

## Explanations
Rule reasons can include low attendance rate, long unpaid streak, unpaid absence, and repeated late arrivals. These rules provide review context, not causal explanations.

## Fairness
No subgroup fairness metrics for attendance were supplied in the current audit extract. Attendance patterns can be affected by disability, caregiving, approved leave, work arrangements, and data-capture quality; review these contexts before action.

## Limits and risks
- Unsupervised anomaly flags can include legitimate rare cases.
- Contamination controls the expected flagged proportion and may not match future prevalence.
- Missing or inaccurate attendance records can create false positives.
- Require HR verification against approved leave, schedule changes, and source-system records.

## Version and owner
- Artifact: `models/attendance_anomaly/1.0.0/model.joblib`
- Metadata: `models/attendance_anomaly/1.0.0/metadata.json`
- Version: `1.0.0`; algorithm: IsolationForest.
- Owner: CortexHR project team; named operational owner not recorded.
