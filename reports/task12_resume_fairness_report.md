# Task 12 — Resume Screener Fairness Audit

## Executive summary

The Task 11 resume screener was tested using 25 counterfactual twin-resume pairs. Each pair was scored against the same designated job family using the original Task 11 scoring pipeline. The average absolute score gap was **0.000**, the maximum gap was **0.000**, and **0 of 25** pairs had a non-zero gap.

Because the baseline twin-pair gap was already zero, no scoring feature was removed and no weights were changed. This is the appropriate outcome: changing the model solely to force a gap reduction when the controlled test shows no gap would be unjustified.

The Validation Vault attributes were opened only after the baseline pair scores were saved. They were used only for post-score auditing, never as scoring inputs.

## 1. Method

The Task 11 weighted scoring implementation was reproduced:

| Component | Weight |
|---|---:|
| Required-skill coverage | 50% |
| Nice-to-have skill coverage | 15% |
| TF-IDF cosine similarity | 20% |
| Capped experience fit | 15% |

The same text cleaning, phrase-based skill extraction, TF-IDF settings (`ngram_range=(1, 2)`, `sublinear_tf=True`, English stop words), and weighted formula were retained.

Each twin pair was scored against the shared `target_job_family` of its two resumes. The twin pair file confirms identical skills and experience for all 25 pairs.

## 2. Counterfactual twin-resume results

| Pair type | Pair count | Mean absolute gap | Maximum gap | Non-zero gaps |
|---|---:|---:|---:|---:|
| Gender-coded name only | 12 | 0.000 | 0.000 | 0 |
| Gender-coded name + college tier | 13 | 0.000 | 0.000 | 0 |
| **Overall** | **25** | **0.000** | **0.000** | **0** |

**Before vs after:** the same scores are retained after the audit. No model change was made because the initial counterfactual gap was already zero.

## 3. Protected-group score comparison

The protected-attribute file contains 185 resume records with `inferred_gender` and `college_tier`. Each resume was scored against its designated `target_job_family`; group means were calculated only after scoring.

| Attribute | Group | Count | Mean score |
| inferred_gender | Female | 74 | 0.5438 |\n| inferred_gender | Male | 111 | 0.5235 |\n| college_tier | Tier 1 | 49 | 0.5525 |\n| college_tier | Tier 2 | 71 | 0.5040 |\n| college_tier | Tier 3 | 65 | 0.5461 |\n
The maximum difference between the observed group means was **0.0203** for inferred gender and **0.0485** for college tier.

These are descriptive gaps, not causal estimates or proof of discrimination. The groups may differ in job-family composition and job-relevant qualifications. In particular, a global group mean can reflect different distributions of skills, experience, and target roles. The per-job-family breakdown is supplied separately to make this limitation more visible.

The `inferred_gender` field is an inferred audit attribute, not verified self-reported identity. Small group sizes within individual job families also make subgroup comparisons unstable.

## 4. Ranking quality

No scoring features, weights, or ranking logic were changed. Therefore, Task 11 ranking quality remains as reported on its 555 human-labeled resume–job pairs:

| Metric | Task 11 baseline | Task 12 after audit |
|---|---:|---:|
| Precision@5 | 94.0% | 94.0% |
| Recall@5 | 54.9% | 54.9% |
| NDCG@5 | 0.960 | 0.960 |
| Mean per-job Spearman correlation | 0.828 | 0.828 |

The Task 11 metrics are retained from the completed Task 11 evaluation report. They are not recomputed from the protected-attribute file. The 555 labels cover only a subset of all 1,850 possible resume–job pairs.

## 5. Fairness statement

> We tested the resume screener using 25 counterfactual twin pairs whose skills and experience were identical while gender-coded names and, in some pairs, college tier differed. All 25 pairs received identical scores; the mean and maximum absolute score gaps were both zero. We then used the separately unlocked inferred-gender and college-tier fields only for post-scoring group analysis. The observed mean-score gaps were 0.0203 for inferred gender and 0.0485 for college tier when resumes were scored against their designated job family. These group differences are descriptive and may reflect differences in job-family mix and job-relevant qualifications; they do not by themselves establish unfair treatment. No model change was made because the controlled twin test showed no direct score sensitivity to the changed attributes. The system remains a decision-support prototype, not an automated hiring decision-maker. Further monitoring, representative subgroup samples, and human review are required before operational use.

## 6. Limitations and next steps

- The twin-pair test covers 25 constructed pairs, not every possible name, identity, education, or resume format.
- A zero counterfactual gap on these pairs does not prove that all proxy effects have been removed.
- Aggregate group means are not adjusted for job family, experience, or skills; interpret them as screening signals for further investigation, not as causal fairness measurements.
- Some job-family subgroup sizes are small.
- Task 11 already identified resume-layout-related skill extraction errors. Those can disadvantage candidates whose experience is not parsed consistently, even if protected attributes are excluded.
- A recruiter must review evidence and make final decisions. Do not use this score as the sole basis for rejection.

## Evidence files

- `task12_before_after_gap_table.csv` — all 25 pair-level before/after results.
- `task12_protected_group_score_summary.csv` — protected-group means and counts.
- `task12_group_gaps_by_job_family.csv` — subgroup breakdown by designated job family.
- `task12_ranking_quality_comparison.csv` — unchanged Task 11 ranking metrics.
- `task12_before_fairness_pair_scores.csv` — original baseline component scores for each twin.
- `task12_fairness_summary.json` — machine-readable summary.
- `10_resume_job_ranking.ipynb` — Task 11 scorer used as the basis for this audit.
- `11_resume_fairness_audit.ipynb` — reproducible Task 12 audit workflow.
