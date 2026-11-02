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

## Representative review: five resumes and three job descriptions
The focused manual review uses three supplied job descriptions: **J04 ML Engineer**, **J08 Accountant**, and **J09 Account Executive**. The five selected resumes include strong human-rated matches and layout-related ranking disagreements.

A good match should show evidence of the role's required skills, relevant preferred skills where available, and experience meeting the stated minimum. Preferred skills should not fully compensate for missing essential requirements. Name, gender, age, location, employer identity, and college tier are not match criteria.

| Resume | Job | Experience | Layout | Model rank (185) | Model required-skill coverage | Human score | Shortlist |
|---|---|---:|---|---:|---:|---:|---|
| RES-0031 | ML Engineer | 4.3 years | Clean PDF | 2 | 100% | 5/5 | Y |
| RES-0130 | ML Engineer | 6.9 years | Missing sections | 25 | 40% | 4/5 | Y |
| RES-0010 | Accountant | 3.4 years | Clean DOCX | 7 | 80% | 4/5 | Y |
| RES-0007 | Account Executive | 2.8 years | Two-column PDF | 4 | 100% | 5/5 | Y |
| RES-0012 | Account Executive | 3.7 years | Missing sections | 19 | 40% | 5/5 | Y |

The strong examples (RES-0031, RES-0010, RES-0007) provide positive comparisons. RES-0130 and RES-0012 show that missing resume sections can lead to skill under-extraction and low model ranks even when human reviewers consider the candidates strong. This is an illustrative, targeted review, not a statistically random sample.

## Five misranking examples

- **J02 Senior Software Engineer — RES-0129 (model rank 5/185; score 0.596; human score 3/5, shortlist N):** The model detects 80% of nice-to-have skills and full experience fit, but only 60% of required skills. System Design and REST APIs are not detected. Preferred skills and experience partly compensate for missing core requirements.
- **J03 Data Analyst — RES-0101 (model rank 11/185; score 0.607; human score 3/5, shortlist N):** The model detects 80% of required skills and full experience fit, but Statistics is missing. Exact phrase coverage does not assess depth of evidence, and the experience component helps offset the missing requirement.
- **J08 Accountant — RES-0087 (model rank 8/185; score 0.647; human score 3/5, shortlist N):** The model detects all five required skill phrases, but the candidate has 1.2 years against the 2-year minimum (experience fit 0.60). The human reviewer assessed required-skill coverage at 60%. This highlights the difference between literal phrase detection and human assessment of demonstrated competence.
- **J04 ML Engineer — RES-0130 (model rank 25/185; human score 4/5, shortlist Y):** The resume has missing sections and no explicit Skills section in its text. The text-only extractor detects 40% of required skills, despite 6.9 years of experience. The separate structured skills column contains additional relevant terms but is intentionally excluded from the ranking score.
- **J09 Account Executive — RES-0012 (model rank 19/185; human score 5/5, shortlist Y):** The resume has missing sections and no explicit Skills section in its text. Text extraction detects 40% of required skills and 25% of preferred skills. Relevant terms in the separate structured skills column are not used by the text-only scoring pipeline.


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
- `reports/task11_representative_review.csv` — five-resume review against three job descriptions.
- `notebooks/10_resume_job_ranking.ipynb` — reproducible notebook.

---
These results are a first transparent baseline. Weights are fixed before evaluation; they were not tuned against the 555 human labels.