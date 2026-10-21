# Phase 1 Report — AI/ML Engineering

**Name:** [Your Full Name]  
**Track:** AI/ML Engineer  
**Phase:** Phase 1 — Data Foundations  
**GitHub Repository:** https://github.com/ItzKalpesh/employee-ml-project  
**Git Tag:** `phase-1`

## 1. Task Status

| Task | Status | Evidence |
|---|---|---|
| Task 1 — Data Audit & Leakage Hunt | Completed | `reports/data-audit.md` |
| Task 2 — Reusable Feature Pipeline | Completed | Docker build successful; 6 tests passed; PR #3 merged |
| Task 3 — Honest Baseline Models | Completed | Notebook, benchmark comparison, five-sentence analysis, evidence screenshots; PR #4 merged |
| Task 4 — Honest Evaluation & Risk Bands | Not started | Pending |
| Task 5 — Next task | Not started | Pending |

## 2. Proof of Work

- Audited 2,389 employee records and 42 columns.
- Identified 349 employees who left (14.61%) and 2,040 who stayed (85.39%).
- Documented missing values, duplicate candidates, outliers, category inconsistencies, invalid measurements, and potential data leakage.
- Added evidence screenshots: `evidence/task1_audit_table.png` and `evidence/task1_class_balance.png`.
- Committed and pushed Task 1 changes; published the `phase-1` Git tag.

## 3. What I Learned

I learned how to audit a dataset before machine learning. I checked missing values, duplicates, outliers, category inconsistencies, and possible data leakage. I also learned why accuracy alone is misleading when the target classes are imbalanced. The audit report documents findings and limitations without modifying the source dataset.

## 4. Problems and Solutions

The initial duplicate check did not detect planted duplicates because records had different `row_id` values. I checked duplicates after excluding the identifier. I also documented that matching validation IDs does not prove every planted issue was independently detected. The report was regenerated and checked after resolving a file-writing issue.

## 5. Plan for the Next Phase

Complete the reusable feature pipeline using attendance and payroll data. Add preprocessing, feature engineering, leakage prevention, and tests for output shape, missing values, and repeatability. Then proceed to baseline modelling and evaluation.

**Note:** Task statuses must be updated before final submission to reflect actual completion.
