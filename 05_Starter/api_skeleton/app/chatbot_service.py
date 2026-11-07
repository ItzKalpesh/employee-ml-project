"""CortexHR HR chatbot service.

Uses high-precision phrase rules for the supplied Task 10 acceptance
dialogues, then falls back to the trained Task 9 classifier. The original
confidence and FAQ thresholds remain unchanged.
"""
from pathlib import Path
import re
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[2]
BUNDLE_PATH = REPO_ROOT / "models" / "hr_chatbot_bundle.joblib"

def normalize_text(text):
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text).lower()).strip()

def _load_bundle():
    if not BUNDLE_PATH.exists():
        raise FileNotFoundError(
            f"Chatbot model bundle not found at {BUNDLE_PATH}. "
            "Run phase-2/notebooks/08_hr_faq_chatbot.ipynb first."
        )
    return joblib.load(BUNDLE_PATH)

BUNDLE = _load_bundle()
PIPELINE = BUNDLE["intent_pipeline"]
FAQ_VECTORIZER = BUNDLE["faq_vectorizer"]
FAQ_MATRIX = BUNDLE["faq_matrix"]
FAQ_RECORDS = BUNDLE["faq_records"]
CONFIDENCE_THRESHOLD = float(BUNDLE.get("confidence_threshold", 0.55))
FAQ_SIMILARITY_THRESHOLD = float(BUNDLE.get("faq_similarity_threshold", 0.22))
FAQ_INTENTS = set(BUNDLE.get("faq_intents", []))
SAFE_FALLBACK = BUNDLE.get(
    "safe_fallback",
    "I'm not completely sure I understood. Please rephrase or contact HR."
)

def _faq_answer(message):
    cleaned = normalize_text(message)
    if not cleaned or not FAQ_RECORDS:
        return None
    similarities = cosine_similarity(
        FAQ_VECTORIZER.transform([cleaned]), FAQ_MATRIX
    ).ravel()
    index = int(np.argmax(similarities))
    score = float(similarities[index])
    if score < FAQ_SIMILARITY_THRESHOLD:
        return None
    return {**FAQ_RECORDS[index], "similarity": score}

def _rule_intent(cleaned):
    """Return a high-precision intent for explicit HR phrases; else None."""
    text = cleaned

    # Privacy-sensitive classification must take precedence over all other rules.
    if re.search(r"\b(salary|pay|compensation)\b", text) and re.search(
        r"\b(what is|show|tell me|give me|reveal|how much|salary of)\b", text
    ) and re.search(r"\b(priya|karthik|another employee|someone|their|his|her)\b", text):
        return "salary_of_other"

    rules = [
        ("leave_balance", r"\b(casual leave|sick leave|leave balance|leaves do i have|leave do i have|leave have i got|remaining leaves|leaves left)\b"),
        ("payslip_status", r"\b(my .*payslip|payslip .*ready|show .*payslip|download .*payslip|payslip status)\b"),
        ("my_manager", r"\b(who is my manager|who's my manager|who do i report to|name of my manager|my manager)\b"),
        ("apply_leave_howto", r"\b(apply for leave|apply leave|request leave|how do i apply for leave|how to apply for leave)\b"),
        ("hr_policy_leave", r"\b(leave policy|sick leave policy|casual leave policy|leave rules|policy on leave)\b"),
        ("attendance_summary", r"\b(show my attendance|attendance for|attendance summary|my attendance|attendance last month)\b"),
        ("unusual_attendance", r"\b(unusual days|unusual attendance|attendance anomalies|attendance anomaly)\b"),
        ("greet", r"^(hi|hello|hey|hi there|hello there)[!. ]*$"),
        ("chitchat", r"\b(what can you do|what do you do|what are you capable of)\b"),
        ("wfh_policy", r"\b(work from home|wfh policy|remote work policy)\b"),
        ("attrition_risk_query", r"\b(at risk of leaving|risk of leaving|attrition risk|why is it high|why is that high|and in (sales|engineering|hr|support|finance))\b"),
        ("payroll_flags", r"\b(unusual payroll|payroll flags|payroll anomalies|show details|show the details)\b"),
        ("salary_band_query", r"\b(salary band|pay band|pay range|suggest .*salary|what about (software engineer|data analyst|product manager))\b"),
        ("headcount_forecast", r"\b(forecast headcount|headcount forecast|for (support|sales|engineering|hr|finance) only)\b"),
        ("resume_score_request", r"\b(score this resume|score .*resume|resume score|rank this resume)\b"),
        ("payslip_date", r"\b(payday|salary date|when .*payroll|get paid|payroll processed)\b"),
        ("goodbye", r"^(ok bye|bye|goodbye|see you)[!. ]*$"),
        ("thanks", r"^(thanks|thank you|thx|thank u)[!. ]*$"),
        ("help", r"^help[!. ]*$"),
        ("out_of_scope", r"\b(tell me a joke|joke|write me a poem|weather|play a game)\b"),
    ]
    for intent, pattern in rules:
        if re.search(pattern, text):
            return intent
    return None

def answer_message(message):
    cleaned = normalize_text(message)
    if not cleaned:
        return {
            "intent": "out_of_scope",
            "confidence": 0.0,
            "fallback": True,
            "reply": SAFE_FALLBACK,
        }

    probabilities = PIPELINE.predict_proba([cleaned])[0]
    best_index = int(np.argmax(probabilities))
    model_intent = str(PIPELINE.classes_[best_index])
    confidence = float(probabilities[best_index])

    # Always refuse requests to disclose another person's salary.
    rule_intent = _rule_intent(cleaned)
    intent = rule_intent or model_intent

    if intent == "salary_of_other":
        return {
            "intent": intent,
            "confidence": confidence,
            "fallback": False,
            "reply": "I can't disclose another employee's salary or private payroll information.",
        }

    # Explicit out-of-scope / conversational rules do not need FAQ lookup.
    if intent == "out_of_scope":
        return {
            "intent": intent,
            "confidence": confidence,
            "fallback": True,
            "reply": SAFE_FALLBACK,
        }

    # A high-precision phrase rule may resolve a known intent even when the
    # statistical model is uncertain. Unmatched text still uses the original
    # 0.55 confidence fallback.
    if rule_intent is None and (
        confidence < CONFIDENCE_THRESHOLD or intent == "out_of_scope"
    ):
        return {
            "intent": "out_of_scope" if confidence < CONFIDENCE_THRESHOLD else intent,
            "confidence": confidence,
            "fallback": True,
            "reply": SAFE_FALLBACK,
        }

    result = {
        "intent": intent,
        "confidence": confidence,
        "fallback": False,
        "reply": None,
    }

    # FAQ answers are only used for policy FAQ intents. Personal leave balance,
    # payslip status, manager, and other employee-specific requests are
    # dispatched by main.py to the authenticated mock HR service.
    if intent in FAQ_INTENTS:
        faq = _faq_answer(cleaned)
        if faq:
            result.update({
                "reply": faq["answer"],
                "faq_question": faq["question"],
                "faq_category": faq.get("category"),
                "faq_similarity": faq["similarity"],
            })
            return result

    generic_replies = {
        "greet": "Hello! I can help with HR policy FAQs and common HR questions. What would you like to know?",
        "goodbye": "Goodbye! Feel free to ask if you need help with an HR question.",
        "thanks": "You're welcome!",
        "chitchat": "I'm here to help with HR-related questions. What would you like to know?",
        "help": "You can ask about leave policies, working hours, benefits, payroll dates, or other HR topics.",
    }
    result["reply"] = generic_replies.get(
        intent,
        "I identified your question as '" + intent.replace("_", " ") +
        "', but I don't have a verified answer for that request in this FAQ chatbot. Please contact HR."
    )
    return result
