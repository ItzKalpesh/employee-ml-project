
"""CortexHR anomaly API for Task 8."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

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


@app.post("/v1/chat", response_model=ChatOut)
def chat(msg: ChatIn):
    raise HTTPException(
        status_code=501,
        detail="CX-10: chat implementation is outside Task 8.",
    )
