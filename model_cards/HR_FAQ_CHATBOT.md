# Model Card — HR FAQ Chatbot

## Purpose
Classify employee HR questions into supported intents and retrieve relevant FAQ answers. It is an informational assistant, not a source of authoritative legal, payroll, employment, or policy determinations.

## Data
- Training file: `data/chatbot_nlu_training.csv`.
- FAQ source: `data/hr_faq.csv`.
- Other available sources: `data/chatbot_dialogues.csv`, `data/chatbot_responses.csv`, `data/chatbot_test_set.csv`.
- Bundle contains intent pipeline, FAQ vectorizer/matrix/records, classes, safe fallback, confidence threshold, FAQ similarity threshold, and test accuracy.
- Exact row counts/date range and data governance review are not confirmed by the supplied bundle summary.

## Method
- Intent pipeline plus TF-IDF FAQ similarity retrieval.
- Confidence threshold: 0.55.
- FAQ similarity threshold: 0.22.
- Safe fallback is included.
- Test accuracy recorded in bundle: 0.7575757575757576 (75.76%).

## Metrics

Held-out evaluation:
- Training messages: 858.
- Test messages: 132 across 33 intent classes.
- Correct predictions: 100 / 132.
- Test accuracy: 75.76%.
- Macro F1-score: 0.75.
- Weighted F1-score: 0.75.

Weaker-performing intents:
| Intent | F1-score |
|---|---:|
| help | 0.29 |
| team_members | 0.33 |
| hr_policy_leave | 0.44 |
| holiday_list | 0.50 |
| who_to_contact | 0.50 |
| working_hours | 0.57 |

The confusion matrix contains 33 rows and 33 columns, with 100 correct predictions on its diagonal. Misclassified examples are recorded in `reports/task9_misclassified_messages.csv`.

Accuracy alone does not establish reliable performance across every HR intent. The weaker classes require additional training examples and evaluation.

## Explanations
The predicted intent and retrieved FAQ similarity provide limited traceability. The chatbot should show a fallback when confidence/similarity is insufficient. A complete per-intent explanation example was not included in the supplied metadata excerpt.

## Fairness
No demographic subgroup evaluation was supplied. Review intent performance across language styles, spelling variation, accessibility needs, and employee populations where appropriate.

## Limits and risks
- May misunderstand ambiguous, multilingual, misspelled, or novel questions.
- FAQ content can become stale when policy changes.
- Never disclose another employee's salary or private payroll information.
- Sensitive or high-impact questions must be escalated to HR.
- Verify policy answers against the current approved HR source.

## Version and owner
- Artifact: `models/hr_chatbot_bundle.joblib`.
- Version: not stated in the supplied bundle summary.
- Owner: CortexHR project team; named operational owner not recorded.
