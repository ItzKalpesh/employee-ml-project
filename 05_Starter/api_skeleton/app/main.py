
"""CortexHR anomaly API for Task 8."""
import re
import httpx
from .memory_service import get_session_slots
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Header
from .permission_service import resolve_demo_user, authorize_intent
from .memory_service import update_session_memory, get_session_slots
from pydantic import BaseModel, ConfigDict, Field
from .chatbot_service import answer_message

ROOT = Path(__file__).resolve().parents[3]
MODEL_VERSION = "1.0.0"


def load_artifact(name):
    folder = ROOT / "models" / name / MODEL_VERSION
    model_path = folder / "model.joblib"
    metadata_path = folder / "metadata.json"

    if not model_path.exists() or not metadata_path.exists():
        raise RuntimeError(f"Model artifacts missing for {name}: {folder}")

    model = joblib.load(model_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return model, metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load both detectors once when the API starts.
    app.state.attendance_model, app.state.attendance_meta = load_artifact(
        "attendance_anomaly"
    )
    app.state.payroll_model, app.state.payroll_meta = load_artifact(
        "payroll_anomaly"
    )
    yield


app = FastAPI(
    title="CortexHR API",
    version="0.2.0",
    lifespan=lifespan,
)


class RiskOut(BaseModel):
    employee_id: str
    risk_score_12m: float = Field(ge=0, le=1)
    risk_band: str
    top_reason_1: str
    top_reason_2: str
    top_reason_3: str
    model_version: str


class AnomalyBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(min_length=1)
    employee_id: str = Field(min_length=1)
    period: str = Field(min_length=1)


class AttendanceIn(AnomalyBase):
    scheduled_days: int = Field(ge=0)
    present_days: int = Field(ge=0)
    half_days_unpaid: int = Field(default=0, ge=0)
    paid_leave_days: int = Field(default=0, ge=0)
    unpaid_absence_days: int = Field(default=0, ge=0)
    longest_unpaid_streak_days: int = Field(default=0, ge=0)
    late_arrivals: int = Field(default=0, ge=0)
    avg_hours_worked: float = Field(ge=0, le=24)
    overtime_hours: float = Field(default=0, ge=0)
    attendance_rate: float = Field(ge=0, le=1)
    wfh_days: int = Field(default=0, ge=0)


class PayrollIn(AnomalyBase):
    monthly_fixed_gross: float = Field(gt=0)
    gross_pay: float = Field(ge=0)
    total_deductions: float = Field(ge=0)
    net_pay: float
    overtime_hours_paid: float = Field(default=0, ge=0)
    duplicate_payment: bool = False


class AnomalyOut(BaseModel):
    result_id: str
    source_dataset: str
    record_id: str
    employee_id: str
    period: str
    anomaly_score: float = Field(ge=0, le=1)
    flagged: bool
    reason_code: str
    reason_text: str
    money_at_risk: float | None = None
    model_version: str
    scored_at: str


class ChatIn(BaseModel):
    message: str
    session_id: str
    user_role: str = "EMPLOYEE"


class ChatOut(BaseModel):
    intent: str
    reply: str
    slots: dict = {}


def score_to_unit_interval(decision_value):
    """Convert lower Isolation Forest decision values to higher anomaly scores."""
    value = float(decision_value)
    score = 1.0 / (1.0 + np.exp(np.clip(10.0 * value, -60, 60)))
    return float(np.clip(score, 0.0, 1.0))


def make_output(
    row, source, score, flagged, reason_code, reason_text,
    money_at_risk, model_version,
):
    return AnomalyOut(
        result_id=f"AN-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        source_dataset=source,
        record_id=row.record_id,
        employee_id=row.employee_id,
        period=row.period,
        anomaly_score=round(float(score), 6),
        flagged=bool(flagged),
        reason_code=reason_code,
        reason_text=reason_text,
        money_at_risk=(
            round(float(money_at_risk), 2)
            if money_at_risk is not None and np.isfinite(money_at_risk)
            else None
        ),
        model_version=model_version,
        scored_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/v1/health")
def health():
    return {"status": "ok", "service": "cortexhr"}


@app.get("/v1/attrition/risk/{employee_id}", response_model=RiskOut)
def attrition(employee_id: str):
    raise HTTPException(
        status_code=501,
        detail="CX-14: attrition scoring is not part of Task 8.",
    )


@app.post("/v1/anomaly/attendance", response_model=AnomalyOut)
def anomaly_attendance(row: AttendanceIn):
    model = app.state.attendance_model
    metadata = app.state.attendance_meta
    features = metadata["feature_columns"]

    values = row.model_dump()
    missing = [name for name in features if name not in values]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing attendance model features: {missing}",
        )

    X = pd.DataFrame([[values[name] for name in features]], columns=features)
    prediction = int(model.predict(X)[0])
    decision = float(model.decision_function(X)[0])
    score = score_to_unit_interval(decision)

    # Preserve the attendance rules from Task 5.
    rules = []
    if row.attendance_rate < 0.75:
        rules.append(("LOW_ATTENDANCE", "Attendance rate is below 75%."))
    if row.longest_unpaid_streak_days >= 5:
        rules.append((
            "LONG_UNPAID_STREAK",
            "Unpaid absence streak is at least five days.",
        ))
    if row.unpaid_absence_days >= 5:
        rules.append((
            "HIGH_UNPAID_ABSENCE",
            "Unpaid absence days are at least five.",
        ))
    if row.late_arrivals >= 5:
        rules.append((
            "FREQUENT_LATENESS",
            "Late arrivals are at least five.",
        ))
    if row.present_days == 0 and row.scheduled_days > 0:
        rules.insert(
            0,
            ("NO_ATTENDANCE", "No presence recorded for the period."),
        )

    flagged = prediction == -1 or bool(rules)
    if rules:
        reason_code, reason_text = rules[0]
    elif prediction == -1:
        reason_code = "STATISTICAL_OUTLIER"
        reason_text = "Attendance pattern was flagged by the anomaly detector."
    else:
        reason_code = "NO_ATTENDANCE"
        reason_text = "No attendance rule or statistical anomaly was detected."

    return make_output(
        row,
        "attendance_monthly_features",
        score,
        flagged,
        reason_code,
        reason_text,
        None,
        metadata["model_version"],
    )


@app.post("/v1/anomaly/payroll", response_model=AnomalyOut)
def anomaly_payroll(row: PayrollIn):
    model = app.state.payroll_model
    metadata = app.state.payroll_meta

    eps = 1e-6
    gross = row.gross_pay
    deductions = row.total_deductions
    net = row.net_pay

    values = {
        "gross_vs_fixed": gross / row.monthly_fixed_gross,
        "deduction_ratio": deductions / gross if abs(gross) > eps else np.nan,
        "net_ratio": net / gross if abs(gross) > eps else np.nan,
        "overtime_hours_paid": row.overtime_hours_paid,
        "net_reconciliation_gap": gross - deductions - net,
        "deductions_over_gross": int(deductions > gross + 0.01),
        "negative_net_pay": int(net < 0),
    }

    features = metadata["feature_columns"]
    missing = [name for name in features if name not in values]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Payroll model metadata has unsupported features: {missing}",
        )

    X = pd.DataFrame([[values[name] for name in features]], columns=features)
    prediction = int(model.predict(X)[0])
    decision = float(model.decision_function(X)[0])
    score = score_to_unit_interval(decision)

    # Preserve the Task 6 payroll business rules.
    rules = []
    if row.duplicate_payment:
        rules.append((
            "DOUBLE_PAYMENT",
            "Duplicate payment was reported for this record.",
        ))
    if net < 0:
        rules.append(("NEGATIVE_NET_PAY", "Net pay is negative."))
    if deductions > gross + 0.01:
        rules.append((
            "DEDUCTIONS_EXCEED_GROSS",
            "Total deductions exceed gross pay.",
        ))

    gap = gross - deductions - net
    if abs(gap) > 1.0:
        rules.append((
            "PAYROLL_RECONCILIATION",
            "Gross pay minus deductions does not reconcile to net pay.",
        ))

    flagged = prediction == -1 or bool(rules)
    if rules:
        reason_code, reason_text = rules[0]
    elif prediction == -1:
        reason_code = "STATISTICAL_OUTLIER"
        reason_text = "Payroll pattern was flagged by the anomaly detector."
    else:
        reason_code = "NO_ANOMALY"
        reason_text = "No payroll rule or statistical anomaly was detected."

    # A reconciliation gap is a useful review estimate, not confirmed loss.
    money_at_risk = abs(gap) if abs(gap) > 1.0 else None

    return make_output(
        row,
        "payroll_monthly_features",
        score,
        flagged,
        reason_code,
        reason_text,
        money_at_risk,
        metadata["model_version"],
    )


HR_SERVICE_URL = "http://127.0.0.1:9000"
HR_SERVICE_FAILURE = (
    "Sorry, I could not fetch that right now. "
    "Please try again or contact HR."
)


def _hr_get(path, employee_id, params=None):
    """Call the mock HR service using the authenticated employee identity."""
    response = httpx.get(
        f"{HR_SERVICE_URL}{path}",
        headers={"X-Demo-User": employee_id},
        params=params,
        timeout=8.0,
    )
    response.raise_for_status()
    return response.json()


def _resolve_month(slots):
    """Convert remembered month values into the YYYY-MM API format."""
    value = slots.get("month")
    if not value:
        return None

    value = str(value).strip()

    for fmt in ("%Y-%m", "%B %Y", "%b %Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m")
        except ValueError:
            pass

    today = datetime.now()
    if value.lower() == "last month":
        month = today.month - 1 or 12
        year = today.year - (1 if today.month == 1 else 0)
        return f"{year:04d}-{month:02d}"

    if value.lower() == "this month":
        return today.strftime("%Y-%m")

    if value.lower() == "next month":
        month = today.month + 1
        year = today.year
        if month == 13:
            month, year = 1, year + 1
        return f"{year:04d}-{month:02d}"

    for fmt in ("%B", "%b"):
        try:
            month = datetime.strptime(value, fmt).month
            return f"{today.year:04d}-{month:02d}"
        except ValueError:
            pass

    return None


def dispatch_hr_service(intent, message, user, memory):
    """Dispatch only to routes verified in the supplied mock HR service."""
    if user is None:
        return None, "Authentication is required."

    employee_id = user["employee_id"]
    text = message.lower()

    try:
        if intent == "leave_balance":
            data = _hr_get(
                "/api/v1/leave/balance",
                employee_id,
                params={"employee": "me"},
            )

            if "sick" in text:
                key, label = "sl_balance", "Sick leave"
            elif "casual" in text:
                key, label = "cl_balance", "Casual leave"
            elif "earned" in text or "el " in f" {text}":
                key, label = "el_balance", "Earned leave"
            else:
                return data, (
                    f"Your leave balances are: "
                    f"Casual: {data.get('cl_balance', 'N/A')}, "
                    f"Sick: {data.get('sl_balance', 'N/A')}, "
                    f"Earned: {data.get('el_balance', 'N/A')} days."
                )

            if key not in data:
                return data, HR_SERVICE_FAILURE

            return data, f"Your {label.lower()} balance is {data[key]} days."

        if intent == "leave_request_status":
            data = _hr_get(
                "/api/v1/leave/requests",
                employee_id,
                params={"employee": "me", "limit": 5},
            )
            return data, f"Here are your leave request records: {data}"

        if intent == "payslip_status":
            month = _resolve_month(memory)
            if not month:
                return None, "Which monthâ€™s payslip would you like to check?"

            data = _hr_get(
                f"/api/v1/payslips/me/{month}",
                employee_id,
            )
            return data, f"Your payslip information for {month}: {data}"

        if intent in ("my_manager", "my_department"):
            data = _hr_get("/api/v1/employees/me", employee_id)

            if intent == "my_manager":
                return data, (
                    f"Your manager's employee ID is "
                    f"{data.get('manager_id', 'not available')}."
                )

            return data, (
                f"Your department ID is "
                f"{data.get('department_id', 'not available')}."
            )

        if intent == "team_members":
            data = _hr_get("/api/v1/employees/me/team", employee_id)
            return data, f"Your team information: {data}"

        if intent == "holiday_list":
            data = _hr_get("/api/v1/holidays", employee_id)
            return data, f"Here is the holiday list: {data}"

        if intent == "attendance_summary":
            month = _resolve_month(memory)
            if not month:
                return None, "Which monthâ€™s attendance would you like to check?"

            data = _hr_get(
                "/api/v1/attendance/summary",
                employee_id,
                params={"employee": "me", "month": month},
            )
            return data, f"Your attendance summary for {month}: {data}"

    except (httpx.HTTPError, ValueError, KeyError):
        return None, HR_SERVICE_FAILURE
        # These intents require service functionality that is not yet available.
    unsupported_service_intents = {
        "unusual_attendance",
        "salary_band_query",
        "attrition_risk_query",
        "headcount_forecast",
        "payroll_flags",
        "resume_score_request",
    }

    if intent in unsupported_service_intents:
        return None, HR_SERVICE_FAILURE

    # FAQ, greetings, chitchat and out-of-scope messages
    # should use the existing chatbot response.
    return None, None


@app.post("/v1/chat", response_model=ChatOut)
def chat(
    msg: ChatIn,
    x_demo_user: str | None = Header(
        default=None,
        alias="X-Demo-User",
    ),
):
    # 1. Authenticate using the trusted header.
    user = None

    if x_demo_user:
        user = resolve_demo_user(x_demo_user)

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid demo user or HR service unavailable.",
            )

    # 2. Retrieve previous session memory.
    memory = {}
    if user is not None:
        memory = get_session_slots(
            msg.session_id,
            user["employee_id"],
        )

    previous_intent = memory.get("previous_intent")

    # 3. Classify the current message.
    result = answer_message(msg.message)
    intent = result["intent"]

    # 4. Resolve short conversational follow-ups.
    follow_up_rules = {
        "attrition_risk_query": (
            r"\b(and in|what about|why is it high|"
            r"why is that high|why)\b"
        ),
        "payroll_flags": (
            r"\b(show details|details|more details|"
            r"explain those|explain)\b"
        ),
        "salary_band_query": (
            r"\b(what about|and for|and)\b"
        ),
        "headcount_forecast": (
            r"\b(for|what about|and for|only)\b"
        ),
        "attendance_summary": (
            r"\b(any unusual days|unusual days|"
            r"any unusual attendance)\b"
        ),
    }

    pattern = follow_up_rules.get(previous_intent)

    if (
    pattern
    and re.search(pattern, msg.message.lower())
    and intent != "unusual_attendance"
    ):
        intent = previous_intent
        result["intent"] = intent
        result["fallback"] = False

    # 5. Enforce permissions on the resolved intent.
    allowed, denial_reason = authorize_intent(intent, user)

    if not allowed:
        return ChatOut(
            intent=intent,
            reply=denial_reason,
            slots={
                "authenticated": user is not None,
                "role": user["role"] if user else None,
            },
        )

    # 6. Update session memory only after authorization.
    if user is not None:
        update_session_memory(
            msg.session_id,
            user["employee_id"],
            msg.message,
            intent=intent,
        )

        memory = get_session_slots(
            msg.session_id,
            user["employee_id"],
        )

    # 7. Preserve Task 9 response metadata.
    slots = {
        key: result[key]
        for key in (
            "confidence",
            "fallback",
            "faq_question",
            "faq_category",
            "faq_similarity",
        )
        if key in result
    }

    if user is not None:
        slots["memory"] = memory

    # 8. Dispatch to verified HR services.
    service_data, service_reply = dispatch_hr_service(
        intent,
        msg.message,
        user,
        memory,
    )

    if service_reply is not None:
        slots["service_data"] = service_data

        return ChatOut(
            intent=intent,
            reply=service_reply,
            slots=slots,
        )

    # 9. Return existing FAQ or conversational response.
    return ChatOut(
        intent=intent,
        reply=result["reply"],
        slots=slots,
    )
