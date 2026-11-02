# Task 11 — Resume Ranking Against Job Descriptions

## Dataset and evaluation scope
- 10 job descriptions, 185 resumes, and 555 human-labeled resume–job pairs.
- Each resume has three human-labeled job pairs; the ranking engine scores all 1,850 possible resume–job pairs.
- Ranking metrics are calculated on the 555 labeled pairs only. Within each job, the labeled candidates are ranked for evaluation; the full 185-candidate ranking is retained separately.
- Human suitability scores are 1–5. In this dataset, scores 4–5 correspond to shortlist Y, and scores 1–3 correspond to shortlist N.

## Ranking method
The system is a transparent weighted scoring baseline, not a supervised model trained on the human labels.

| Component | Weight |
|---|---:|
| Required-skill coverage | 50% |
| Nice-to-have skill coverage | 15% |
| TF-IDF cosine similarity | 20% |
| Experience fit (capped at the stated minimum) | 15% |

The skill dictionary is built from the job descriptions. Skills are detected in cleaned resume text. TF-IDF uses sanitized resume text and job-description text. Human labels are joined only after scoring for evaluation.

## Fairness and feature exclusions
The ranking score does not use candidate name, email, city, company names, education details, college tier, target_job_family, reviewer notes, suitability labels, or shortlist labels. The resume text is cleaned to remove identity/contact lines, employer names, and education sections before text similarity is calculated. Years of experience is used only as a capped fit against the job minimum; exceeding the minimum gives no extra bonus.

### Why not rank on years of experience alone?
Years alone can disadvantage early-career candidates, career changers, and people returning to work whose skills may still match the role. It can also reward tenure without measuring relevant skills. Experience therefore contributes only 15% and is capped once the stated minimum is met.

### Resume-layout risk
The skill extractor recovered about 62.2% of listed skills from resumes marked as missing sections, compared with about 79–81% across the other layout groups. This shows a format-related false-negative risk; parsing quality should be improved before operational use.

## Results
- Macro Precision@5: **0.940** (94.0%).
- Macro Recall@5: **0.549** (54.9%).
- Macro NDCG@5: **0.960**.
- Mean per-job Spearman correlation with human suitability: **0.828**.
- Skill extraction audit against the structured skills reference: precision **0.937**, recall **0.781**, F1 **0.852**.

### Ranking quality by job
| Job | Labeled pairs | Shortlisted | Precision@5 | Recall@5 | NDCG@5 | Spearman |
|---|---:|---:|---:|---:|---:|---:|
| J01 — Software Engineer | 64 | 7 | 1.000 | 0.714 | 1.000 | 0.835 |
| J02 — Senior Software Engineer | 47 | 3 | 0.400 | 0.667 | 0.894 | 0.865 |
| J03 — Data Analyst | 60 | 12 | 1.000 | 0.417 | 1.000 | 0.831 |
| J04 — ML Engineer | 62 | 16 | 1.000 | 0.312 | 0.825 | 0.934 |
| J05 — Product Manager | 57 | 9 | 1.000 | 0.556 | 1.000 | 0.805 |
| J06 — Customer Support Executive | 49 | 6 | 1.000 | 0.833 | 1.000 | 0.616 |
| J07 — HR Executive | 49 | 8 | 1.000 | 0.625 | 1.000 | 0.822 |
| J08 — Accountant | 55 | 9 | 1.000 | 0.556 | 1.000 | 0.833 |
| J09 — Account Executive | 57 | 14 | 1.000 | 0.357 | 0.890 | 0.907 |
| J10 — Digital Marketing Executive | 55 | 11 | 1.000 | 0.455 | 0.992 | 0.830 |

## Five misranking examples

- **J02 Senior Software Engineer — RES-0129 (model rank 5/185; human score 3/5, shortlist N):** False positive: 80% nice-to-have coverage and sufficient experience lift the score, but the human reviewer marked only a partial match; key required skills such as System Design and REST APIs are not detected.
- **J03 Data Analyst — RES-0101 (model rank 11/185; human score 3/5, shortlist N):** False positive: 80% required-skill coverage and sufficient experience produce a high score, but the reviewer marked a partial match; the missing required skill is Statistics.
- **J08 Accountant — RES-0087 (model rank 8/185; human score 3/5, shortlist N):** False positive: all required skills are detected, but experience is only 1.2 years against the 2-year minimum; the experience component is 0.60.
- **J04 ML Engineer — RES-0130 (model rank 25/185; human score 4/5, shortlist Y):** False negative: the resume text has a missing Skills section. The text extractor therefore misses several skills that appear in the separate structured skills field, pushing a human-strong candidate down the ranking.
- **J09 Account Executive — RES-0012 (model rank 19/185; human score 5/5, shortlist Y):** False negative: the resume text has a missing Skills section. Several sales skills present in the structured skills field are not visible to the text extractor, so the human-strong candidate is ranked too low.

## Limitations and next improvements
- Labels cover 555 of 1,850 possible pairs, so evaluation does not establish quality for every candidate–job combination.
- Dictionary matching misses synonyms and skills expressed indirectly; missing or unusual resume layouts can cause false negatives.
- TF-IDF is lexical rather than semantic and can reward related wording without verifying depth or recency of experience.
- The current experience feature is deliberately simple. It should not dominate skills, and years alone are not a reliable ranking rule.
- A human reviewer must make final decisions. This prototype should support, not automate, hiring decisions.

## API endpoint proposal (design note only)
- `POST /v1/resume-ranking/rank`
- Input: `job_id` plus a list of candidate `resume_id` values (or parsed resume text in a later upload workflow).
- Output: ordered candidate IDs, rank, total match score, and component breakdown (required skills, nice-to-have skills, TF-IDF similarity, experience fit). Do not return names or contact details in ranking output.
- This is an API design proposal; this Task 11 notebook does not modify the existing `main.py` endpoint implementation.

## Evidence files
- `reports/task11_resume_rankings.csv` — full 1,850-pair ranking.
- `reports/task11_ranking_quality_by_job.csv` — per-job evaluation metrics.
- `reports/task11_five_misranked_resumes.csv` — five explained ranking disagreements.
- `reports/task11_skill_extraction_audit.csv` — per-resume skill extraction audit.
- `reports/task11_skill_extraction_by_layout.csv` — extraction performance by layout difficulty.
- `notebooks/10_resume_job_ranking.ipynb` — reproducible notebook.

---
These results are a first transparent baseline. Weights are fixed before evaluation; they were not tuned against the 555 human labels.