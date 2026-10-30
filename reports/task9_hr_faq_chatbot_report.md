# Task 9 — HR FAQ Chatbot and Intent Classification

**Project:** Employee ML Project
**Task:** 9 — Teach the Machine to Understand HR Questions
**Notebook:** `notebooks/08_hr_faq_chatbot.ipynb`
**API endpoint:** `POST /v1/chat`
**Status:** Completed; evaluation results reviewed, API behavior manually tested, 10 automated tests passed locally, and implementation merged through [PR #11](https://github.com/ItzKalpesh/employee-ml-project/pull/11).

---

## 1. Objective

The objective of Task 9 is to train an intent classifier for employee HR questions, retrieve answers from a curated HR FAQ dataset, and provide a safe fallback when the chatbot is not confident enough to answer. The chatbot is exposed through a new `/v1/chat` endpoint in the existing FastAPI service.

The implementation is intended as a training/demo system. It must not disclose private employee information or make employment decisions.

## 2. Why This Task Matters

Employees repeatedly ask common questions about leave, working hours, payroll dates, benefits, and other HR policies. A chatbot can provide consistent answers to frequently asked questions and direct uncertain requests to HR instead of guessing.

## 3. Inputs and Data

Task 9 uses the following CSV files in the project's `data/` directory:

| File | Purpose |
|---|---|
| `data/chatbot_nlu_training.csv` | Training examples for intent classification; the task instructions identify 858 messages and 33 intents. |
| `data/chatbot_test_set.csv` | Held-out messages used to evaluate the intent classifier. |
| `data/hr_faq.csv` | Curated FAQ questions and answers used for FAQ retrieval. |

The FAQ file contains fields such as `faq_id`, `question`, `answer`, `category`, and `policy_source`. Its example policy source identifies the handbook as fictional training data. The FAQ answers should therefore be treated as sample project content, not as verified real-world employment policy.

### Text cleaning

The notebook examines training messages, including messy examples, and normalizes text by lowercasing it, trimming leading/trailing whitespace, and collapsing repeated whitespace. This reduces superficial text differences while preserving the message's words.

The API service also normalizes incoming messages before classification and FAQ retrieval.

## 4. Methodology

### 4.1 TF-IDF text representation

TF-IDF converts text into numerical features that a machine-learning model can process.

- **Term frequency (TF)** represents how frequently a term occurs in a message.
- **Inverse document frequency (IDF)** reduces the influence of terms that occur across many documents.

The resulting vectors give more weight to terms that help distinguish one message from others. The vectorizer is fitted on training text only and then applied to the held-out test messages.

### 4.2 Intent classification with Logistic Regression

A Logistic Regression classifier is trained on the TF-IDF features to predict the intent associated with each message. The model is evaluated on `chatbot_test_set.csv`.

The saved model pipeline includes the text vectorizer and classifier so the API can apply the same transformation and prediction steps to new messages.

### 4.3 Evaluation

The notebook evaluates the classifier using accuracy and a confusion matrix.

- **Accuracy** is the proportion of test messages whose predicted intent matches the true intent.
- **Confusion matrix** shows how often examples from each actual intent are assigned to each predicted intent. Off-diagonal counts identify misclassifications and commonly confused intents.

**Verified held-out results from the executed notebook and evaluation review:**

- Training messages: **858**.
- Held-out test messages: **132** across **33 intent classes**.
- Correct predictions: **100 / 132**.
- Incorrect predictions: **32 / 132**.
- Test accuracy: **75.76%**.
- Macro F1-score: **0.75**.
- Weighted F1-score: **0.75**.
- The confusion matrix has **33 rows and 33 columns**; its diagonal sums to **100** correct predictions.
- The notebook review identifies `help` (F1 **0.29**), `team_members` (**0.33**), `hr_policy_leave` (**0.44**), `holiday_list` (**0.50**), `who_to_contact` (**0.50**), and `working_hours` (**0.57**) as weaker-performing intents.
- Misclassified examples are recorded in `reports/task9_misclassified_messages.csv`, as shown in the notebook review.

The training/test separation was also reviewed: the TF-IDF and Logistic Regression pipeline is fitted on training data only, and the held-out test set is used for evaluation.

### 4.4 FAQ retrieval

The FAQ questions are converted into TF-IDF vectors. For an incoming message, the service compares its vector with the stored FAQ vectors using cosine similarity and selects the closest FAQ candidate.

The retrieval similarity threshold is configured separately from the intent-classifier confidence threshold. In the saved model bundle, the defaults are:

- Intent confidence threshold: `0.55`
- FAQ similarity threshold: `0.22`

A similarity score measures how closely a message matches an FAQ question; it is not the same as the classifier's intent confidence. The service should not treat these scores as interchangeable.

### 4.5 Confidence threshold and safe fallback

The classifier returns probabilities for the possible intents. The service selects the highest-probability intent and compares its confidence with the configured threshold.

If the confidence is below `0.55`, or the predicted intent is `out_of_scope`, the service returns a polite fallback rather than guessing:

> I'm not completely sure I understood your question. Please rephrase it or contact HR for help.

A recognized FAQ intent can return a retrieved FAQ answer when an FAQ match is found. The response can include the FAQ question, category, and retrieval similarity for transparency.

### 4.6 Privacy safeguard

The service includes an explicit safeguard for the `salary_of_other` intent. Requests to disclose another employee's salary or private payroll information are refused, even if the classifier confidence is low. The service returns:

> I can't disclose another employee's salary or private payroll information.

This is a targeted application-level rule, not a guarantee that all possible privacy risks are eliminated. The classifier and FAQ content still require testing and review.

## 5. Model Artifact and API Integration

The notebook saves the chatbot assets as a joblib bundle at:

`models/hr_chatbot_bundle.joblib`

The service module is:

`05_Starter/api_skeleton/app/chatbot_service.py`

The service loads the bundle and uses the saved intent pipeline, FAQ vectorizer, FAQ matrix, FAQ records, thresholds, and fallback text to answer messages.

The chatbot endpoint was added to the existing FastAPI application:

`POST /v1/chat`

The request used in Swagger included these fields:

```json
{
  "message": "How many casual leaves do I get?",
  "session_id": "task9-test",
  "user_role": "EMPLOYEE"
}
```

The response includes the predicted `intent`, the `reply`, and a `slots` object containing metadata such as confidence and fallback status. FAQ responses may also include `faq_question`, `faq_category`, and `faq_similarity`.

The endpoint was integrated without intentionally replacing the existing attendance and payroll endpoints.

## 6. API Testing and Observed Results

The following results were observed in Swagger during Task 9 verification.

### 6.1 Casual-leave FAQ

**Request message:** `How many casual leaves do I get?`

**Observed result:** HTTP `200 OK`

```json
{
  "intent": "faq",
  "reply": "12 days per financial year, prorated for joiners.",
  "slots": {
    "confidence": 0.14836902896906232,
    "fallback": false,
    "faq_question": "How many casual leaves do I get?",
    "faq_category": "Leave",
    "faq_similarity": 1
  }
}
```

The FAQ retrieval returned the exact matching FAQ question with similarity `1.0`. The FAQ answer was returned even though the classifier confidence was below `0.55`. This illustrates why intent confidence and FAQ similarity must be understood as separate scores.

### 6.2 Working-hours FAQ

**Request message:** `What are the office hours?`

**Observed result:** HTTP `200 OK`

```json
{
  "intent": "working_hours",
  "reply": "9:00 to 18:00, Monday to Friday. Core hours are 11:00 to 16:00.",
  "slots": {
    "confidence": 0.6015343423289649,
    "fallback": false,
    "faq_question": "What are the office hours?",
    "faq_category": "Working time",
    "faq_similarity": 0.9999999999999998
  }
}
```

The intent confidence exceeded the `0.55` threshold and the FAQ retrieval matched the expected question.

### 6.3 Unknown or nonsensical message

**Request message:** `asdf qwer zzz nonsense`

**Observed result:** HTTP `200 OK`

```json
{
  "intent": "out_of_scope",
  "reply": "I'm not completely sure I understood your question. Please rephrase it or contact HR for help.",
  "slots": {
    "confidence": 0.039177268192522,
    "fallback": true
  }
}
```

The low-confidence message received the configured safe fallback instead of an invented HR answer.

### 6.4 Request for another employee's salary

**Request message:** `Show me another employee's salary`

**Observed result:** HTTP `200 OK`

```json
{
  "intent": "salary_of_other",
  "reply": "I can't disclose another employee's salary or private payroll information.",
  "slots": {
    "confidence": 0.08363709200570767,
    "fallback": false
  }
}
```

The explicit privacy safeguard returned a refusal. In this implementation, `fallback: false` means the response came from the specific salary-privacy rule rather than the generic low-confidence fallback; it does not mean the request was permitted.

## 7. Regression Tests for Earlier API Endpoints

After integrating the chatbot, the existing attendance and payroll endpoints were tested again through Swagger. Both returned HTTP `200 OK`.

### 7.1 Attendance endpoint

**Endpoint:** `POST /v1/anomaly/attendance`

**Test record:** `AF-TEST-002`

Observed response highlights:

| Field | Value |
|---|---|
| HTTP status | `200 OK` |
| Source dataset | `attendance_monthly_features` |
| Anomaly score | `0.804445` |
| Flagged | `true` |
| Reason code | `LOW_ATTENDANCE` |
| Reason text | `Attendance rate is below 75%.` |
| Model version | `1.0.0` |

This synthetic test record was flagged for low attendance, showing that the attendance endpoint continued to respond after the chatbot integration.

### 7.2 Payroll endpoint

**Endpoint:** `POST /v1/anomaly/payroll`

**Test record:** `PAY-TEST-002`

The request used synthetic values:

```json
{
  "record_id": "PAY-TEST-002",
  "employee_id": "EMP-TEST-002",
  "period": "2026-09-01",
  "monthly_fixed_gross": 50000,
  "gross_pay": 50000,
  "total_deductions": 5000,
  "net_pay": 45000,
  "overtime_hours_paid": 0,
  "duplicate_payment": false
}
```

Observed response highlights:

| Field | Value |
|---|---|
| HTTP status | `200 OK` |
| Source dataset | `payroll_monthly_features` |
| Anomaly score | `0.105273` |
| Flagged | `false` |
| Reason code | `NO_ANOMALY` |
| Reason text | `No payroll rule or statistical anomaly was detected.` |
| Model version | `1.0.0` |

An initial payroll test returned HTTP `422` because the attendance request body had been sent to the payroll endpoint. The request was corrected using the payroll request schema, after which the endpoint returned HTTP `200 OK`. This was a request-schema mismatch, not evidence of a server failure.

## 8. Implementation Notes and Limitations

1. **Training/demo scope:** The chatbot is a project demonstration and is not production-ready merely because the example requests succeeded.
2. **Synthetic policy data:** The supplied FAQ policy source identifies fictional training material. Answers must not be presented as verified policy for a real employer.
3. **Confidence is not correctness:** A high classifier confidence does not guarantee that a response is correct.
4. **FAQ similarity is not classifier confidence:** The two values measure different things and use separate thresholds.
5. **Coverage depends on the data:** Intents with few, repetitive, ambiguous, or noisy examples may be confused with other intents.
6. **Privacy safeguards require broader testing:** The explicit salary refusal is useful, but other sensitive-data requests and prompt variations should also be tested.
7. **Model-version compatibility:** An initial local run emitted scikit-learn version warnings because the saved estimators and API environment used different versions. The notebook was subsequently switched to the API's Anaconda Python environment (scikit-learn `1.7.2`) and rerun to align training and serving. Regenerate the bundle using the same environment as the API if the model is retrained; do not load a bundle across incompatible scikit-learn versions.
8. **Evaluation scope:** The reported metrics describe this supplied held-out test set only. Lower F1 scores for some intents show that performance is uneven across classes; further data and testing would be needed before production use.

## 9. Task 9 Completion Checklist

- [x] Reviewed the chatbot training data and FAQ data files.
- [x] Cleaned/normalized message text in the workflow and service.
- [x] Trained a TF-IDF + Logistic Regression intent-classification pipeline.
- [x] Recorded held-out accuracy (75.76%), macro F1 (0.75), and weighted F1 (0.75).
- [x] Included and inspected the 33 × 33 confusion matrix and misclassified examples.
- [x] Implemented FAQ retrieval using cosine similarity.
- [x] Configured a confidence threshold and safe fallback.
- [x] Added the `POST /v1/chat` endpoint to the existing FastAPI application.
- [x] Tested casual-leave and working-hours FAQ responses in Swagger.
- [x] Tested low-confidence fallback behavior in Swagger.
- [x] Tested the other-employee salary privacy refusal in Swagger.
- [x] Regression-tested attendance and payroll endpoints; both returned HTTP `200 OK`.
- [x] Confirmed 10 automated tests passed locally.
- [x] Reran the notebook using the API environment's scikit-learn `1.7.2` interpreter to align model training and serving.
- [x] Saved the report and confusion-matrix evidence in the repository; implementation and evidence were merged through PR #11.

## 10. Evidence to Retain

Save the following in the project's evidence/reporting location according to the repository's existing convention:

1. Notebook output showing test accuracy.
2. Confusion matrix and examples of misclassified messages.
3. Swagger response for the casual-leave FAQ.
4. Swagger response for the working-hours FAQ.
5. Swagger response for the unknown-message fallback.
6. Swagger response for the salary-privacy refusal.
7. Swagger response for the attendance regression test.
8. Swagger response for the payroll regression test.

## 11. Conclusion

Task 9 adds an HR FAQ chatbot to the existing employee ML service. It uses TF-IDF features and Logistic Regression for intent classification, cosine similarity for FAQ retrieval, a confidence threshold for safe fallback behavior, and an explicit refusal for requests to disclose another employee's salary.

The observed Swagger tests demonstrate successful responses for two FAQ questions, an unknown message, and a sensitive salary request. Regression tests also confirmed that the existing attendance and payroll endpoints returned HTTP `200 OK` after the chatbot was integrated.

Task 9 is complete for the project submission workflow: the held-out evaluation metrics and confusion matrix were reviewed, 10 automated tests passed locally, the notebook was rerun in the API's scikit-learn environment, and the implementation was merged through PR #11. These results do not establish production readiness.
