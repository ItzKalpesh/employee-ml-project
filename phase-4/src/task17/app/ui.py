import json
import httpx
import gradio as gr

API_URL = "http://127.0.0.1:8000"


def predict_attendance(payload):
    try:
        response = httpx.post(
            f"{API_URL}/v1/anomaly/attendance",
            json=payload,
            timeout=30,
        )
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


def predict_payroll(payload):
    try:
        response = httpx.post(
            f"{API_URL}/v1/anomaly/payroll",
            json=payload,
            timeout=30,
        )
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


with gr.Blocks(title="CortexHR Prediction Dashboard") as demo:
    gr.Markdown("# CortexHR Prediction Dashboard")
    gr.Markdown("Submit attendance or payroll records to the CortexHR API.")

    with gr.Tab("Attendance Anomaly"):
        attendance_input = gr.JSON(
            label="Attendance Input",
            value={
                "record_id": "UI-ATT-001",
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
        )
        attendance_button = gr.Button("Predict Attendance Anomaly")
        attendance_output = gr.JSON(label="Prediction Result")
        attendance_button.click(
            predict_attendance,
            inputs=attendance_input,
            outputs=attendance_output,
        )

    with gr.Tab("Payroll Anomaly"):
        payroll_input = gr.JSON(
            label="Payroll Input",
            value={
                "record_id": "UI-PAY-001",
                "employee_id": "EMP-0002",
                "period": "2026-10",
                "monthly_fixed_gross": 50000,
                "gross_pay": 50000,
                "total_deductions": 5000,
                "net_pay": 45000,
                "overtime_hours_paid": 0,
                "duplicate_payment": False
            },
        )
        payroll_button = gr.Button("Predict Payroll Anomaly")
        payroll_output = gr.JSON(label="Prediction Result")
        payroll_button.click(
            predict_payroll,
            inputs=payroll_input,
            outputs=payroll_output,
        )


def create_ui():
    return demo