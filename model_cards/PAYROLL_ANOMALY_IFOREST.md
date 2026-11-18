# Model Card — Payroll Anomaly Detector

## Purpose
Flag unusual payroll calculations or records for payroll-team verification. A flag is not proof of fraud, employee wrongdoing, or intentional overpayment.

## Data
- Source file in metadata: `data/payroll_monthly_features.csv`.
- Training rows: 7,355.
- Features: gross-to-fixed ratio, deduction ratio, net ratio, paid overtime hours, net reconciliation gap, deductions-over-gross indicator, negative-net-pay indicator.
- Dataset date range and exact labelled evaluation sample: not present in the supplied metadata excerpt.

## Method
- Algorithm: Isolation Forest.
- Version: `1.0.0`.
- Contamination parameter: 0.025.
- Companion reason rules: duplicate payment, negative net pay, deductions over gross, reconciliation rule.

## Evaluation Results

Evaluation dataset: 7,355 payroll records containing 100 injected/reference anomalies.

### Standalone Isolation Forest

- Precision: 0.2011 (20.11%)
- Recall: 0.3700 (37.00%)
- F1-score: 0.2606 (26.06%)
- Flagged records: 184
- True positives: 37
- False positives: 147
- False negatives: 63
- True negatives: 7,108

The supplied payroll baseline achieved 21.70% precision and 40.00% recall.

### Detector comparison

- Rules-only detector: precision 81.25%, recall 65.00%, F1 72.22%.
- Combined Rules + Isolation Forest: precision 32.78%, recall 79.00%, F1 46.33%.

The combined detector improves recall but produces substantially more false positives. The rules-only detector has the strongest precision and F1-score in this evaluation.

### Limitations and intended use

The standalone Isolation Forest has low precision and recall. It should be used only as a human-review and investigation aid, not as an automatic payroll correction or enforcement mechanism. The combined detector also requires human review because of its high false-positive volume.

## Explanations
Rule reasons identify possible duplicate payment, negative net pay, deductions exceeding gross, or reconciliation mismatch. These are investigation cues, not conclusions.

## Fairness
No protected-group fairness analysis was supplied for payroll anomaly flags. Audit flag rates and error rates across relevant employee groups where lawful and appropriate, while protecting payroll confidentiality.

## Limits and risks
- Precision of 0.217 indicates a substantial false-alert burden.
- Legitimate adjustments, retroactive pay, benefits, tax changes, and corrections can appear unusual.
- Contamination is a configuration choice, not an estimate of actual fraud prevalence.
- Human payroll review and reconciliation against source records are mandatory.

## Version and owner
- Artifact: `models/payroll_anomaly/1.0.0/model.joblib`
- Metadata: `models/payroll_anomaly/1.0.0/metadata.json`
- Version: `1.0.0`; algorithm: IsolationForest.
- Owner: CortexHR project team; named operational owner not recorded.
