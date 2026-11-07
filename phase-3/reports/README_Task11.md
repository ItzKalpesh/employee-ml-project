# Task 11 — Resume Ranking Against Job Descriptions

## Contents in the project repository
- `notebooks/10_resume_job_ranking.ipynb` — executed notebook for skill extraction, TF-IDF/cosine similarity, weighted ranking, human-label evaluation, five misranking explanations, fairness checks, and a focused review of five resumes against three job descriptions.
- `data/job_descriptions.csv`, `data/resumes.csv`, `data/resume_job_labels.csv` — supplied input datasets.
- `reports/task11_resume_rankings.csv` — ranked resume/job pairs.
- `reports/task11_ranking_quality_by_job.csv` — per-job ranking metrics.
- `reports/task11_five_misranked_resumes.csv` — five explained ranking disagreements.
- `reports/task11_representative_review.csv` — five-resume / three-job close review.
- `reports/task11_skill_extraction_audit.csv` and `reports/task11_skill_extraction_by_layout.csv` — extraction audit evidence.
- `reports/task11_ranking_summary.json` and `reports/task11_resume_ranking_report.md` — summary and written analysis.

## Run
Run `notebooks/10_resume_job_ranking.ipynb` from the project root using the project's existing virtual environment and `05_Starter/requirements.txt`. The notebook searches `data/task11/`, `data/`, and the project root for the three input CSVs and writes evidence to `reports/`.

## Scope and limitations
The ranking is an explainable baseline, not an automated hiring decision. Evaluation uses the 555 human-labeled pairs; it does not treat the other possible pairs as labeled. The notebook proposes an API endpoint but does not change the existing FastAPI `main.py`.
