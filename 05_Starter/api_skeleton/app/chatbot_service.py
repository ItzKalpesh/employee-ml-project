from pathlib import Path
import csv
import re

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[2]

BUNDLE_PATH = REPO_ROOT / "models" / "hr_chatbot_bundle.joblib"

EMPLOYEES_FILE = (
    REPO_ROOT
    / "05_Starter"
    / "mock_services"
    / "mock_data"
    / "employees.csv"
)


def _load_employee_names():
    """Load employee names for salary privacy checks."""
    if not EMPLOYEES_FILE.exists():
        return []

    try:
        with EMPLOYEES_FILE.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            return [
                row["full_name"].strip().lower()
                for row in csv.DictReader(file)
                if row.get("full_name")
            ]
    except (OSError, csv.Error, KeyError):
        return []


EMPLOYEE_NAMES = _load_employee_names()


def normalize_text(text):
    if text is None:
        return ""

    return re.sub(r"\s+", " ", str(text).lower()).strip()


def _load_bundle():
    if not BUNDLE_PATH.exists():
        raise FileNotFoundError(
            f"Chatbot model bundle not found at {BUNDLE_PATH}. "
            "Run notebooks/08_hr_faq_chatbot.ipynb first."
        )

    return joblib.load(BUNDLE_PATH)


BUNDLE = _load_bundle()

PIPELINE = BUNDLE["intent_pipeline"]
FAQ_VECTORIZER = BUNDLE["faq_vectorizer"]
FAQ_MATRIX = BUNDLE["faq_matrix"]
FAQ_RECORDS = BUNDLE["faq_records"]

CONFIDENCE_THRESHOLD = float(
    BUNDLE.get("confidence_threshold", 0.55)
)

FAQ_SIMILARITY_THRESHOLD = float(
    BUNDLE.get("faq_similarity_threshold", 0.22)
)

FAQ_INTENTS = set(BUNDLE.get("faq_intents", []))

SAFE_FALLBACK = BUNDLE.get(
    "safe_fallback",
    "I'm not completely sure I understood. "
    "Please rephrase or contact HR."
)


def _faq_answer(message):
    cleaned = normalize_text(message)

    if not cleaned or not FAQ_RECORDS:
        return None

    similarities = cosine_similarity(
        FAQ_VECTORIZER.transform([cleaned]),
        FAQ_MATRIX,
    ).ravel()

    index = int(np.argmax(similarities))
    score = float(similarities[index])

    if score < FAQ_SIMILARITY_THRESHOLD:
        return None

    return {
        **FAQ_RECORDS[index],
        "similarity": score,
    }


def _resolve_task10_intent(text):
    """Resolve selected Task 10 intents using explicit patterns."""
        # Handle short follow-ups about a specific leave type.
    if re.search(
        r"\b(?:and|what about)\s+(?:my\s+)?"
        r"(?:casual|sick|earned|annual)\s+leaves?\b",
        text,
    ):
        return "leave_balance"

    # Leave request status must be checked before leave balance.
    if (
        re.search(r"\b(leave request|leave requests|leave application|leave applications)\b", text)
        and re.search(r"\b(status|show|check|pending|approved|rejected|my)\b", text)
    ):
        return "leave_request_status"

    # Personal leave balance, not general leave policy.
    if (
        re.search(
            r"\b(leave|leaves|casual leave|sick leave)\b",
            text,
        )
        and re.search(
            r"\b(my|i have|do i have|balance|left|remaining)\b",
            text,
        )
        and not re.search(
            r"\b(policy|entitlement|allowed per year|carry forward)\b",
            text,
        )
    ):
        return "leave_balance"

    # HR salary-band requests.
    if (
        re.search(
            r"\b(salary band|pay band|pay range|salary range|fair pay)\b",
            text,
        )
        and re.search(
            r"\b(suggest|recommend|what should we pay|what is|show)\b",
            text,
        )
    ):
        return "salary_band_query"

    # Attrition-risk requests.
    if re.search(
        r"\b(attrition risk|risk of leaving|at risk of leaving|"
        r"highest attrition|high risk employees)\b",
        text,
    ):
        return "attrition_risk_query"

        # Employee payslip requests.
    if (
        re.search(r"\b(payslip|pay slip|salary slip)\b", text)
        and re.search(
            r"\b(my|show|check|ready|status|download|is)\b",
            text,
        )
    ):
        return "payslip_status"

    # Employee attendance requests.
    if (
        re.search(r"\battendance\b", text)
        and re.search(
            r"\b(my|show|check|summary|last|this|previous|month)\b",
            text,
        )
    ):
        return "attendance_summary"


    # Employee manager queries.
    if re.search(
        r"\b(my manager|who is my manager|manager details)\b",
        text,
    ):
        return "my_manager"

    # Employee department queries.
    if (
        re.search(r"\b(department|which department)\b", text)
        and re.search(r"\b(my|i work|work in|belong)\b", text)
    ):
        return "my_department"

    # Employee team queries.
    if re.search(
        r"\b(my team|team members|show my team|who is in my team)\b",
        text,
    ):
        return "team_members"

        # Greetings and general chatbot interactions.
    if re.fullmatch(r"(hi|hello|hey|good morning|good afternoon)", text):
        return "greet"

    if re.search(r"\b(what can you do|what do you do)\b", text):
        return "chitchat"

    if re.fullmatch(r"(help|help me)", text):
        return "help"

    if re.fullmatch(r"(bye|goodbye|ok bye)", text):
        return "goodbye"

    if re.fullmatch(r"(thanks|thank you|thank you so much)", text):
        return "thanks"

    # Payroll anomaly requests must take priority over unusual attendance.
    if re.search(
        r"\b(payroll|payroll flags|payroll anomaly)\b",
        text,
    ):
        return "payroll_flags"

    # Unusual attendance requests.
    if re.search(
        r"\b(unusual days|unusual attendance|any unusual)\b",
        text,
    ):
        return "unusual_attendance"

    # HR analytics requests.
    if re.search(r"\b(payroll flags|unusual payroll|payroll anomaly)\b", text):
        return "payroll_flags"

    if re.search(r"\b(headcount forecast|forecast headcount)\b", text):
        return "headcount_forecast"

    return None


def _mentions_known_employee(text):
    """Check whether a message mentions a name in employees.csv."""

    for name in EMPLOYEE_NAMES:
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(name)
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, text):
            return True

    return False


def answer_message(message):
    cleaned = normalize_text(message)

    if not cleaned:
        return {
            "intent": "out_of_scope",
            "confidence": 0.0,
            "fallback": True,
            "reply": SAFE_FALLBACK,
        }

    # Existing Task 9 classifier.
    probabilities = PIPELINE.predict_proba([cleaned])[0]

    best_index = int(np.argmax(probabilities))
    intent = str(PIPELINE.classes_[best_index])
    confidence = float(probabilities[best_index])

    # Task 10 intent improvements.
    rule_intent = _resolve_task10_intent(cleaned)

    if rule_intent:
        intent = rule_intent

    # Salary privacy protection.
    other_person_terms = (
        r"\b(other|another|someone|somebody|colleague|"
        r"coworker|co-worker|teammate|manager|supervisor|"
        r"employee|person|staff member|my boss)\b"
    )

    salary_terms = (
        r"\b(salary|payroll|compensation|pay|earnings|"
        r"wage|wages|income|paid)\b"
    )

    asks_about_other_person = (
        re.search(other_person_terms, cleaned)
        and re.search(salary_terms, cleaned)
    )

    asks_about_named_person = (
        re.search(
            r"\b(what does|how much does|tell me|show me)\b",
            cleaned,
        )
        and re.search(
            r"\b(earn|earns|make|makes|salary|pay|"
            r"compensation|income|wage|paid)\b",
            cleaned,
        )
    )

    asks_about_known_employee = (
        re.search(salary_terms, cleaned)
        and _mentions_known_employee(cleaned)
    )

    # Privacy refusal always takes precedence over FAQ retrieval.
    if (
        intent == "salary_of_other"
        or asks_about_other_person
        or asks_about_named_person
        or asks_about_known_employee
    ):
        return {
            "intent": "salary_of_other",
            "confidence": confidence,
            "fallback": False,
            "reply": (
                "I can't disclose another employee's salary "
                "or private payroll information."
            ),
        }

    # FAQ retrieval only for configured FAQ intents.
    faq = (
        _faq_answer(cleaned)
        if intent in FAQ_INTENTS
        else None
    )

    if faq is not None:
        return {
            "intent": intent,
            "confidence": confidence,
            "fallback": False,
            "reply": faq["answer"],
            "faq_question": faq["question"],
            "faq_category": faq.get("category"),
            "faq_similarity": faq["similarity"],
        }

    # Confidence fallback.
    if (
        (confidence < CONFIDENCE_THRESHOLD and rule_intent is None)
        or intent == "out_of_scope"
    ):
        return {
            "intent": "out_of_scope",
            "confidence": confidence,
            "fallback": True,
            "reply": SAFE_FALLBACK,
        }

    # Standard conversational responses.
    generic_replies = {
        "greet": (
            "Hello! I can help with HR policy FAQs and "
            "common HR questions. What would you like to know?"
        ),
        "goodbye": (
            "Goodbye! Feel free to ask if you need help "
            "with an HR question."
        ),
        "thanks": "You're welcome!",
        "chitchat": (
            "I'm here to help with HR-related questions. "
            "What would you like to know?"
        ),
        "help": (
            "You can ask about leave policies, working hours, "
            "benefits, payroll dates, or other HR topics."
        ),
    }

    reply = generic_replies.get(
        intent,
        (
            f"I identified your question as "
            f"'{intent.replace('_', ' ')}', but I don't have "
            "a verified answer for that request in this FAQ "
            "chatbot. Please contact HR."
        ),
    )

    return {
        "intent": intent,
        "confidence": confidence,
        "fallback": False,
        "reply": reply,
    }
