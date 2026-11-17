
from pathlib import Path
import csv

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[3]

DEMO_USERS_PATH = (
    REPO_ROOT
    / "05_Starter"
    / "mock_services"
    / "mock_data"
    / "demo_users.csv"
)

RESPONSES_PATH = REPO_ROOT / "data" / "chatbot_responses.csv"


def load_csv_lookup(path, key):
    if not path.exists():
        raise FileNotFoundError(f"Required configuration not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    return {
        row[key].strip(): row
        for row in rows
        if row.get(key)
    }


DEMO_USERS = load_csv_lookup(DEMO_USERS_PATH, "employee_id")
INTENT_RULES = load_csv_lookup(RESPONSES_PATH, "intent")


def resolve_demo_user(employee_id):
    """Validate demo identity using the local demo-user registry."""

    if not employee_id:
        return None

    employee_id = employee_id.strip()
    user = DEMO_USERS.get(employee_id)

    if user is None:
        return None

    return {
        "employee_id": employee_id,
        "role": user["role"].strip().upper(),
        "profile": {
            "employee_id": employee_id,
            "username": user.get("username", ""),
            "role": user["role"].strip().upper(),
        },
    }


def authorize_intent(intent, user=None):
    """Apply login and role requirements from chatbot_responses.csv."""

    rule = INTENT_RULES.get(intent)

    if rule is None:
        return False, "Unknown chatbot intent."

    service_call = (rule.get("backend_or_service_call") or "").strip()

    # Privacy refusal always takes precedence over role permissions.
    if service_call.upper() == "REFUSE":
        return False, "This request is not permitted."

    requires_login = (
        (rule.get("requires_login") or "N").strip().upper() == "Y"
    )

    if requires_login and user is None:
        return False, "Please authenticate before accessing this information."

    allowed_roles = {
        role.strip().upper()
        for role in (rule.get("allowed_roles") or "ALL").split(",")
    }

    if "ALL" not in allowed_roles:
        if user is None:
            return False, "Authentication is required."

        if user["role"] not in allowed_roles:
            return False, "You do not have permission to access this information."

    return True, None
