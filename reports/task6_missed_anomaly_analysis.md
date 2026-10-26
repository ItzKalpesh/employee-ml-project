# Task 6 — Payroll Anomaly Detector Evaluation

## Overall results

| detector                 |   flagged |   caught |   false_positives |   missed |   precision |   recall |     f1 |
|:-------------------------|----------:|---------:|------------------:|---------:|------------:|---------:|-------:|
| Isolation Forest only    |       184 |       37 |               147 |       63 |      0.2011 |     0.37 | 0.2606 |
| Rules only               |        80 |       65 |                15 |       35 |      0.8125 |     0.65 | 0.7222 |
| Rules + Isolation Forest |       241 |       79 |               162 |       21 |      0.3278 |     0.79 | 0.4633 |

## Results by anomaly type

| detector                 | anomaly_type     |   actual_rows_of_type |   caught_rows_of_type |   missed_rows_of_type |   type_precision_contribution |   type_recall |
|:-------------------------|:-----------------|----------------------:|----------------------:|----------------------:|------------------------------:|--------------:|
| Isolation Forest only    | DOUBLE_PAYMENT   |                    15 |                     0 |                    15 |                        0      |        0      |
| Isolation Forest only    | MISSED_DEDUCTION |                    15 |                     1 |                    14 |                        0.0054 |        0.0667 |
| Isolation Forest only    | NEGATIVE_NET     |                     8 |                     8 |                     0 |                        0.0435 |        1      |
| Isolation Forest only    | OVERTIME_SPIKE   |                    15 |                    13 |                     2 |                        0.0707 |        0.8667 |
| Isolation Forest only    | ROLE_MISMATCH    |                    15 |                     0 |                    15 |                        0      |        0      |
| Isolation Forest only    | STALE_SALARY     |                    12 |                     0 |                    12 |                        0      |        0      |
| Isolation Forest only    | WRONG_DECIMAL    |                    15 |                    15 |                     0 |                        0.0815 |        1      |
| Isolation Forest only    | ZERO_PAY         |                     5 |                     0 |                     5 |                        0      |        0      |
| Rules only               | DOUBLE_PAYMENT   |                    15 |                    15 |                     0 |                        0.1875 |        1      |
| Rules only               | MISSED_DEDUCTION |                    15 |                     0 |                    15 |                        0      |        0      |
| Rules only               | NEGATIVE_NET     |                     8 |                     8 |                     0 |                        0.1    |        1      |
| Rules only               | OVERTIME_SPIKE   |                    15 |                     0 |                    15 |                        0      |        0      |
| Rules only               | ROLE_MISMATCH    |                    15 |                    15 |                     0 |                        0.1875 |        1      |
| Rules only               | STALE_SALARY     |                    12 |                    12 |                     0 |                        0.15   |        1      |
| Rules only               | WRONG_DECIMAL    |                    15 |                    15 |                     0 |                        0.1875 |        1      |
| Rules only               | ZERO_PAY         |                     5 |                     0 |                     5 |                        0      |        0      |
| Rules + Isolation Forest | DOUBLE_PAYMENT   |                    15 |                    15 |                     0 |                        0.0622 |        1      |
| Rules + Isolation Forest | MISSED_DEDUCTION |                    15 |                     1 |                    14 |                        0.0041 |        0.0667 |
| Rules + Isolation Forest | NEGATIVE_NET     |                     8 |                     8 |                     0 |                        0.0332 |        1      |
| Rules + Isolation Forest | OVERTIME_SPIKE   |                    15 |                    13 |                     2 |                        0.0539 |        0.8667 |
| Rules + Isolation Forest | ROLE_MISMATCH    |                    15 |                    15 |                     0 |                        0.0622 |        1      |
| Rules + Isolation Forest | STALE_SALARY     |                    12 |                    12 |                     0 |                        0.0498 |        1      |
| Rules + Isolation Forest | WRONG_DECIMAL    |                    15 |                    15 |                     0 |                        0.0622 |        1      |
| Rules + Isolation Forest | ZERO_PAY         |                     5 |                     0 |                     5 |                        0      |        0      |

## Missed anomalies — combined detector

| anomaly_type     |   missed_rows |
|:-----------------|--------------:|
| MISSED_DEDUCTION |            14 |
| ZERO_PAY         |             5 |
| OVERTIME_SPIKE   |             2 |

## Rules caught, Isolation Forest missed

| anomaly_type   |   rows_rules_caught_model_missed |
|:---------------|---------------------------------:|
| DOUBLE_PAYMENT |                               15 |
| ROLE_MISMATCH  |                               15 |
| STALE_SALARY   |                               12 |

## Interpretation and limitations

- The detector predictions were frozen before this evaluation.
- Unlock labels were used only to calculate evaluation metrics.
- Evaluation results were not used to retrain or tune the detector.
- Precision measures how many flagged records were actual anomalies.
- Recall measures how many actual anomalies were detected.
- False positives and missed anomalies represent different operational trade-offs.
- These results alone do not establish production readiness.

### Key findings

The combined detector achieved 79% recall, detecting 79 of the 100 labelled anomalies. However, its precision was 32.78%, with 162 false positives among 241 flagged records. The rules-only detector achieved higher precision (81.25%) and an F1-score of 0.7222, but detected only 65% of the anomalies. Therefore, combining Isolation Forest with domain rules improved anomaly coverage but increased false alarms. The appropriate detector depends on whether the priority is catching more payroll errors or reducing unnecessary manual reviews.

### Per-error-type findings

The combined detector missed 21 anomalies: 14 MISSED_DEDUCTION, 5 ZERO_PAY, and 2 OVERTIME_SPIKE. The largest observed weakness was missed deductions. The rules also caught 42 labelled anomalies that Isolation Forest missed: 15 DOUBLE_PAYMENT, 15 ROLE_MISMATCH, and 12 STALE_SALARY. This demonstrates the value of combining interpretable payroll rules with an unsupervised model.

The `type_precision_contribution` column represents the share of all detector flags that were correctly associated with a particular anomaly type; it is not conventional per-class precision. `type_recall` represents the fraction of labelled examples of that type detected by the detector.

### Limitations

These results were measured against the authorized evaluation labels after predictions were frozen. They were not used to retrain or tune the detector. The results depend on the supplied dataset and evaluation labels and do not establish production readiness. False positives require human review, and missed anomalies indicate that the detector cannot replace payroll reconciliation and other controls.