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
            "Run notebooks/08_hr_faq_chatbot.ipynb first."
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
    intent = str(PIPELINE.classes_[best_index])
    confidence = float(probabilities[best_index])

    # Safety guard: refuse requests for another person's salary.
    other_person_terms = (
        r"\b(other|another|someone|somebody|colleague|"
        r"coworker|co-worker|teammate)\b"
    )
    salary_terms = r"\b(salary|payroll|compensation|pay)\b"

    asks_about_other_person = (
        re.search(other_person_terms, cleaned)
        and re.search(salary_terms, cleaned)
    )

    if intent == "salary_of_other" or asks_about_other_person:
        return {
            "intent": "salary_of_other",
            "confidence": confidence,
            "fallback": False,
            "reply": (
                "I can't disclose another employee's salary "
                "or private payroll information."
            ),
        }

    # Search known FAQs before applying the intent-confidence threshold.
    faq = _faq_answer(cleaned)

    if faq is not None:
        faq_intent = (
            intent
            if confidence >= CONFIDENCE_THRESHOLD
            and intent in FAQ_INTENTS
            else "faq"
        )

        return {
            "intent": faq_intent,
            "confidence": confidence,
            "fallback": False,
            "reply": faq["answer"],
            "faq_question": faq["question"],
            "faq_category": faq.get("category"),
            "faq_similarity": faq["similarity"],
        }

    # Use a safe fallback if the classifier is uncertain.
    if confidence < CONFIDENCE_THRESHOLD or intent == "out_of_scope":
        return {
            "intent": "out_of_scope",
            "confidence": confidence,
            "fallback": True,
            "reply": SAFE_FALLBACK,
        }

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
