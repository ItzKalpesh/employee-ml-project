# Model Card — Resume / Job Ranking Screener

## Purpose
Rank submitted resumes against a selected job description to help a recruiter organize manual review. It must not automatically reject candidates or make hiring decisions.

## Data
- Resume source: `data/resumes.csv`.
- Job source: `data/job_descriptions.csv`.
- Related labels: `data/resume_job_labels.csv`.
- Fairness pair data: `data/resume_bias_pairs.csv`.
- Exact source row counts/date range should be confirmed from the current notebook before release.

## Method
The available implementation evidence describes:
- Text cleaning and normalization.
- TF-IDF vectorization with unigram/bigram features and sublinear term frequency.
- Cosine similarity between job descriptions and resume text.
- Explicit skill extraction from job-required and nice-to-have skill terms.
- Experience fit capped at 1.0.
- Composite score: 50% required-skill coverage + 15% nice-skill coverage + 20% TF-IDF similarity + 15% experience fit.

## Metrics

Evaluation uses 555 human-labelled resume-job pairs across 10 job descriptions. The system scores 1,850 possible resume-job pairs, but evaluation metrics are calculated only on the 555 labelled pairs.

| Metric | Result |
|---|---:|
| Macro Precision@5 | 0.940 |
| Macro Recall@5 | 0.549 |
| Macro NDCG@5 | 0.960 |
| Mean per-job Spearman correlation | 0.828 |
| Skill extraction precision | 0.937 |
| Skill extraction recall | 0.781 |
| Skill extraction F1 | 0.852 |

The ranking method is a transparent weighted scoring baseline, not a supervised model trained on the human labels.

Resume-layout limitations were observed: skill extraction recovered approximately 62.2% of listed skills from resumes marked as missing sections, compared with approximately 79–81% across other layout groups.

These results are a baseline on the available labelled sample and do not establish ranking quality for every candidate-job combination.

## Explanations
The score decomposes into required-skill coverage, nice-to-have coverage, TF-IDF similarity, and experience fit. This is a useful component-level explanation but does not explain all semantic relevance or candidate potential.

## Fairness
Task 12 tested 25 counterfactual pairs:
- Mean and maximum absolute twin score gap before: 0.0.
- Mean and maximum absolute twin score gap after: 0.0.
- Nonzero twin gaps: 0 before and after.
- Gender designated-job group mean gap: 0.020338.
- College-tier designated-job group mean gap: 0.048542.
- No model change was made because counterfactual twin gaps were already zero.
These results are limited to the tested pairs and designated job; they do not prove overall fairness.

## Limits and risks
- TF-IDF lexical similarity may miss equivalent skills expressed differently.
- Resume formatting, language, and extraction quality affect scores.
- Experience fit can disadvantage non-linear career paths.
- Group gaps may reflect job/experience composition and are not causal evidence.
- Recruiters must inspect full applications and provide accommodations.

## Version and owner
- Implementation: `phase-3/notebooks/10_resume_job_ranking.ipynb` and `phase-4/src/task17/app/resume_service.py` (verify current paths before release).
- Packaged model artifact/version: not identified in supplied inventory; this is a ranking pipeline rather than a separately listed `.joblib` model.
- Owner: CortexHR project team; named operational owner not recorded.
