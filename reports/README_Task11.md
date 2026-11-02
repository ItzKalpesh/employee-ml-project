# Task 11 — Resume Ranking

## Contents
- `notebooks/10_resume_job_ranking.ipynb` — executed, reproducible analysis notebook.
- `data/task11/` — the three input CSV files.
- `reports/` — ranking output, per-job metrics, five misranked examples, extraction audits, JSON summary and Markdown report.
- `requirements.txt` — project requirements supplied for this task (includes scikit-learn).

## Run
1. Extract this folder into the root of `employee-ml-project` (merge `notebooks/`, `data/`, and `reports/`; do not overwrite existing unrelated files).
2. Open `notebooks/10_resume_job_ranking.ipynb` in VS Code/Jupyter.
3. Select the project virtual environment and run all cells.

The notebook looks for the three CSV files in `data/task11/`, `data/`, or the project root. It writes evidence files into `reports/`.

The notebook does not modify `05_Starter/api_skeleton/app/main.py`. It documents a proposed ranking endpoint only.
