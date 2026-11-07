# Task 5 — Missed Anomaly Analysis

The combined detector caught 119 of 150 injected anomalies (recall 79.33%) and flagged 646 records (precision 18.42%).

It missed 31 injected anomalies. The observed missed types are:

- **IMPOSSIBLE_HOURS**: 31 missed.

## Interpretation

The rules explicitly check low attendance, long unpaid-absence streaks, high unpaid-absence counts, and frequent lateness. Anomaly types that do not strongly affect these measurements may be missed. Isolation Forest detects unusual feature combinations, but it does not guarantee detection of every injected anomaly.

These are plausible explanations based on the detector design, not verified causes for each missed row. Use the missed-anomalies CSV and the data dictionary to inspect the relevant features. The unlocked labels were used only for evaluation, not for model fitting or threshold tuning.

This detector should support data-quality checks and human review, not automated employment decisions.
