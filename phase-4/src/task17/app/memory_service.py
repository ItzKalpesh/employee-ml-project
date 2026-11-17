
from pathlib import Path
from threading import RLock
import csv
import re


APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[2]

EMPLOYEES_FILE = (
    REPO_ROOT
    / "05_Starter"
    / "mock_services"
    / "mock_data"
    / "employees.csv"
)

# Entities explicitly used in the supplied Task 10 dialogues.
KNOWN_DEPARTMENTS = [
    "Sales",
    "Engineering",
    "Support",
]

KNOWN_JOB_TITLES = [
    "Data Analyst",
    "Software Engineer",
]

_session_memory = {}
_memory_lock = RLock()


def _load_employee_names():
    """Load employee names from the actual employees.csv schema."""
    names = []

    if not EMPLOYEES_FILE.exists():
        return names

    try:
        with EMPLOYEES_FILE.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                name = (row.get("full_name") or "").strip()
                if name:
                    names.append(name)

    except (OSError, csv.Error):
        pass

    return list(dict.fromkeys(names))


_EMPLOYEE_NAMES = _load_employee_names()


def _match_entity(message, values):
    """Match a known entity without depending on letter casing."""
    text = message.lower()

    for value in sorted(values, key=len, reverse=True):
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(value.lower())
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, text):
            return value

    return None


def extract_slots(message):
    """Extract month, employee, department and job title."""
    if not isinstance(message, str):
        return {}

    slots = {}
    text = message.strip()

    # Match numeric month format, e.g. 2026-03.
    match = re.search(
        r"\b20\d{2}-(?:0[1-9]|1[0-2])\b",
        text,
    )

    if match:
        slots["month"] = match.group(0)

    else:
        month_names = (
            "january|february|march|april|may|june|"
            "july|august|september|october|november|december"
        )

        match = re.search(
            rf"\b({month_names})(?:\s+(20\d{{2}}))?\b",
            text,
            re.IGNORECASE,
        )

        if match:
            month = match.group(1).capitalize()
            year = match.group(2)
            slots["month"] = (
                f"{month} {year}" if year else month
            )

        else:
            match = re.search(
                r"\b(last month|this month|next month)\b",
                text,
                re.IGNORECASE,
            )

            if match:
                slots["month"] = match.group(1).lower()

    employee = _match_entity(text, _EMPLOYEE_NAMES)
    department = _match_entity(text, KNOWN_DEPARTMENTS)
    job_title = _match_entity(text, KNOWN_JOB_TITLES)

    if employee:
        slots["employee"] = employee

    if department:
        slots["department"] = department

    if job_title:
        slots["job_title"] = job_title

    return slots


def get_session_slots(session_id, employee_id):
    """Return remembered slots for one authenticated session."""
    if not session_id or not employee_id:
        return {}

    key = (session_id, employee_id)

    with _memory_lock:
        return dict(_session_memory.get(key, {}))


def update_session_memory(session_id, employee_id, message, intent=None):
    """Extract new slots and merge them into session memory."""
    if not session_id or not employee_id:
        raise ValueError(
            "session_id and authenticated employee_id are required"
        )

    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must not be empty")

    key = (session_id, employee_id)
    new_slots = extract_slots(message)

    with _memory_lock:
        current_slots = _session_memory.setdefault(key, {})

        # Keep authenticated identity separate and immutable.
        current_slots.setdefault("authenticated_employee_id", employee_id)

        # Update conversation entities without changing authenticated identity.
        current_slots.update(new_slots)
        if intent:
            current_slots["previous_intent"] = intent

        return dict(current_slots)


def clear_session_memory(session_id, employee_id):
    """Clear only the specified employee's session memory."""
    if not session_id or not employee_id:
        return

    key = (session_id, employee_id)

    with _memory_lock:
        _session_memory.pop(key, None)
