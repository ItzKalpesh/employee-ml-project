# Task 1 revision notes

- Expanded `notebooks/01_data_audit.ipynb` with a final reproducible, read-only audit-check section.
- Updated `reports/data-audit.md` with explicit duplicate interpretation, invalid-value decisions, leakage decisions, class-imbalance interpretation, and a transparent validation-vault limitation.
- Kept the source CSV unchanged.
- Important: record-level reconciliation of every one of the 98 planted validation items is not claimed complete in this revision; do not mark the audit fully reconciled until that separate match is completed.
- Run the notebook from top to bottom in the project's Docker/Jupyter environment and review the generated report before committing.
