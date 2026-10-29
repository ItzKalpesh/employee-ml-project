# Task 9 â€” HR FAQ Chatbot and Intent Classification

**Project:** Employee ML Project
**Task:** 9 â€” Teach the Machine to Understand HR Questions
**Notebook:** `notebooks/08_hr_faq_chatbot.ipynb`
**API endpoint:** `POST /v1/chat`
**Status:** Core notebook and API behavior tested; final evaluation metrics and automated-test status must be confirmed from the repository before submission.

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

### 4.3 Intent Classification Evaluation

The intent classification pipeline was evaluated on the untouched test set using accuracy, precision, recall, F1-score, and a confusion matrix.

- **Test accuracy:** 75.76% (0.7576)
- **Number of intent classes:** 33
- **Test samples:** 132
- **Correct predictions:** 100
- **Incorrect predictions:** 32

The confusion matrix indicates that the model correctly classifies many intents, including `apply_leave_howto`, `attrition_risk_query`, `goodbye`, `greet`, `payroll_flags`, `salary_band_query`, `salary_of_other`, `unusual_attendance`, and `wfh_policy`.

Some misclassifications occur between semantically related or overlapping intents. These should be reviewed to identify opportunities to improve the training examples and distinguish similar intents.

The classification report is saved as `reports/task9_classification_report.csv`. The confusion matrix is saved as `reports/task9_confusion_matrix.csv`.

**Evaluation note:** Although the model achieves 75.76% test accuracy, its performance should be assessed alongside per-intent precision, recall, F1-score, and misclassification patterns before production use.

**Before final submission, copy the exact measured values from the executed notebook:**

- Test accuracy: **[Insert exact notebook result]**
- Confusion matrix: **[Insert or attach the matrix produced by the notebook]**
- Most-confused intent pairs: **[Identify from the matrix and error inspection]**

These values are not estimated here because the exact notebook metric output is not present in the available conversation evidence.

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
7. **Model-version compatibility:** During local API startup, scikit-learn emitted warnings because the saved estimators were created with scikit-learn `1.9.1` while the Windows API environment used `1.7.2`. The notebook environment reported Python `3.12` and scikit-learn `1.9.1`; the Windows API environment reported Anaconda Python and scikit-learn `1.7.2`. The API eventually returned successful responses, but the version mismatch should be resolved by aligning training and serving environments and regenerating the bundle if necessary. Successful requests alone do not remove this compatibility risk.
8. **No unsupported metric claims:** Exact test accuracy, confusion-matrix values, and most-confused intent pairs must be copied from the executed notebook output. They are not inferred from the API examples.

## 9. Task 9 Completion Checklist

- [x] Reviewed the chatbot training data and FAQ data files.
- [x] Cleaned/normalized message text in the workflow and service.
- [x] Trained a TF-IDF + Logistic Regression intent-classification pipeline.
- [ ] Recorded the exact held-out test accuracy from the notebook.
- [ ] Included and inspected the confusion matrix and misclassified examples.
- [x] Implemented FAQ retrieval using cosine similarity.
- [x] Configured a confidence threshold and safe fallback.
- [x] Added the `POST /v1/chat` endpoint to the existing FastAPI application.
- [x] Tested casual-leave and working-hours FAQ responses in Swagger.
- [x] Tested low-confidence fallback behavior in Swagger.
- [x] Tested the other-employee salary privacy refusal in Swagger.
- [x] Regression-tested attendance and payroll endpoints; both returned HTTP `200 OK`.
- [ ] Run or confirm automated tests for the chatbot service and endpoint.
- [ ] Resolve the scikit-learn training/serving version mismatch before treating the artifact as production-ready.
- [ ] Save the final report and supporting screenshots/evidence in the repository.

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

Before reporting the task as fully complete, record the exact notebook evaluation metrics, inspect the confusion matrix and errors, run the automated tests, and align the scikit-learn versions used to train and serve the saved model.
