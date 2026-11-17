import requests

BASE_URL = "http://localhost:8000"
HEADERS = {"X-Demo-User": "EMP-0011"}

tests = [
    (
        "Health",
        "GET",
        "/v1/health",
        None,
        {},
        200,
    ),
    (
        "Attrition Risk",
        "GET",
        "/v1/attrition/risk/EMP-0002",
        None,
        HEADERS,
        200,
    ),
    (
        "Attendance Anomaly",
        "POST",
        "/v1/anomaly/attendance",
        {
            "record_id": "SMOKE-ATT-001",
            "employee_id": "EMP-0002",
            "period": "2026-10",
            "scheduled_days": 22,
            "present_days": 20,
            "half_days_unpaid": 0,
            "paid_leave_days": 1,
            "unpaid_absence_days": 1,
            "longest_unpaid_streak_days": 1,
            "late_arrivals": 1,
            "avg_hours_worked": 8.0,
            "overtime_hours": 2.0,
            "attendance_rate": 0.91,
            "wfh_days": 5
        },
        {},
        200,
    ),
    (
        "Payroll Anomaly",
        "POST",
        "/v1/anomaly/payroll",
        {
            "record_id": "SMOKE-PAY-001",
            "employee_id": "EMP-0002",
            "period": "2026-10",
            "monthly_fixed_gross": 50000,
            "gross_pay": 50000,
            "total_deductions": 5000,
            "net_pay": 45000,
            "overtime_hours_paid": 0,
            "duplicate_payment": False
        },
        {},
        200,
    ),
    (
        "Resume Ranking",
        "POST",
        "/v1/resume/rank",
        {"job_id": "J01", "top_n": 5},
        HEADERS,
        200,
    ),
    (
        "Chatbot",
        "POST",
        "/v1/chat",
        {
            "message": "What are the working hours?",
            "session_id": "task17-smoke-test"
        },
        HEADERS,
        200,
    ),
]

print("\nCortexHR API Smoke Test")
print("=" * 55)

passed = 0

for name, method, path, payload, headers, expected in tests:
    try:
        response = requests.request(
            method,
            BASE_URL + path,
            json=payload,
            headers=headers,
            timeout=30,
        )

        success = response.status_code == expected

        if success:
            passed += 1

        print(f"\n{'PASS' if success else 'FAIL'}: {name}")
        print(f"HTTP Status: {response.status_code}")

        if not success:
            print("Response:", response.text[:500])

    except requests.RequestException as exc:
        print(f"\nFAIL: {name}")
        print("Error:", exc)

print("\n" + "=" * 55)
print(f"Results: {passed}/{len(tests)} tests passed")

if passed != len(tests):
    raise SystemExit(1)