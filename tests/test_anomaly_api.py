
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "05_Starter" / "api_skeleton"
sys.path.insert(0, str(API_DIR))

from app.main import app  # noqa: E402


EXPECTED_FIELDS = {
    "result_id",
    "source_dataset",
    "record_id",
    "employee_id",
    "period",
    "anomaly_score",
    "flagged",
    "reason_code",
    "reason_text",
    "money_at_risk",
    "model_version",
    "scored_at",
}


def test_health():
    with TestClient(app) as client:
        response = client.get("/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_attendance_endpoint_returns_official_format():
    payload = {
        "record_id": "AF-TEST-001",
        "employee_id": "EMP-TEST-001",
        "period": "2026-09-01",
        "scheduled_days": 22,
        "present_days": 20,
        "half_days_unpaid": 0,
        "paid_leave_days": 1,
        "unpaid_absence_days": 1,
        "longest_unpaid_streak_days": 1,
        "late_arrivals": 2,
        "avg_hours_worked": 8.5,
        "overtime_hours": 2.0,
        "attendance_rate": 20 / 22,
        "wfh_days": 4,
    }

    with TestClient(app) as client:
        response = client.post("/v1/anomaly/attendance", json=payload)

    assert response.status_code == 200
    assert set(response.json()) == EXPECTED_FIELDS
    assert 0 <= response.json()["anomaly_score"] <= 1


def test_payroll_endpoint_returns_official_format():
    payload = {
        "record_id": "PI-TEST-001",
        "employee_id": "EMP-TEST-001",
        "period": "2026-09-01",
        "monthly_fixed_gross": 50000,
        "gross_pay": 50000,
        "total_deductions": 5000,
        "net_pay": 45000,
        "overtime_hours_paid": 2,
        "duplicate_payment": False,
    }

    with TestClient(app) as client:
        response = client.post("/v1/anomaly/payroll", json=payload)

    assert response.status_code == 200
    assert set(response.json()) == EXPECTED_FIELDS
    assert 0 <= response.json()["anomaly_score"] <= 1


def test_attendance_rejects_invalid_input():
    payload = {
        "record_id": "AF-BAD",
        "employee_id": "EMP-BAD",
        "period": "2026-09-01",
        "scheduled_days": -1,
        "present_days": 20,
        "avg_hours_worked": 8,
        "attendance_rate": 0.9,
    }

    with TestClient(app) as client:
        response = client.post("/v1/anomaly/attendance", json=payload)

    assert response.status_code == 422


def test_payroll_rejects_invalid_input():
    payload = {
        "record_id": "PI-BAD",
        "employee_id": "EMP-BAD",
        "period": "2026-09-01",
        "monthly_fixed_gross": 0,
        "gross_pay": 50000,
        "total_deductions": 5000,
        "net_pay": 45000,
    }

    with TestClient(app) as client:
        response = client.post("/v1/anomaly/payroll", json=payload)

    assert response.status_code == 422


def test_attendance_rejects_unknown_fields():
    payload = {
        "record_id": "AF-TEST-002",
        "employee_id": "EMP-TEST-002",
        "period": "2026-09-01",
        "scheduled_days": 22,
        "present_days": 20,
        "avg_hours_worked": 8,
        "attendance_rate": 0.9,
        "unexpected_field": "not allowed",
    }

    with TestClient(app) as client:
        response = client.post("/v1/anomaly/attendance", json=payload)

    assert response.status_code == 422
