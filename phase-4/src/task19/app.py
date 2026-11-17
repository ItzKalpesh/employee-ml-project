
import streamlit as st

from api_client import APIError, api_request, show_api_error

st.set_page_config(
    page_title="CortexHR Insights Console",
    page_icon="📊",
    layout="wide",
)

st.title("CortexHR Insights Console")
st.caption("Workforce intelligence for informed HR decisions.")

with st.sidebar:
    st.header("Demo Authentication")
    user_id = st.selectbox(
        "Select demo user",
        ["EMP-0011", "EMP-0041", "EMP-0099", "EMP-0107", "EMP-0002"],
    )
    st.caption("HR: EMP-0011 / EMP-0041")
    st.caption("Admin: EMP-0099 / EMP-0107")
    st.caption("Employee: EMP-0002")

risks_tab, anomalies_tab, assistant_tab, resume_tab, forecast_tab = st.tabs(
    ["Risks", "Anomalies", "Assistant", "Resume Screener", "Forecast"]
)

with risks_tab:
    st.header("Employee Attrition Risk")
    st.write("Check the 12-month attrition risk score for an employee.")

    employee_id = st.text_input(
        "Employee ID",
        placeholder="Example: EMP-0002",
        key="risk_employee_id",
    )

    if st.button("Check Attrition Risk", type="primary"):
        if not employee_id.strip():
            st.warning("Please enter an employee ID.")
        else:
            try:
                result = api_request(
                    "GET",
                    f"/v1/attrition/risk/{employee_id.strip()}",
                    user_id=user_id,
                )

                st.subheader("Risk Assessment")
                st.metric(
                    "12-Month Risk Score",
                    f"{result['risk_score_12m'] * 100:.2f}%",
                )
                st.write("Employee ID:", result["employee_id"])
                st.write("Model version:", result["model_version"])
                st.info(result["notice"])
                st.warning("AI-generated — for human review")

            except APIError as error:
                show_api_error(error)


with anomalies_tab:
    st.header("Anomaly Detection")
    st.write("Check attendance and payroll records for unusual patterns.")

    anomaly_type = st.radio(
        "Choose record type",
        ["Attendance", "Payroll"],
        horizontal=True,
    )

    if anomaly_type == "Attendance":
        with st.form("attendance_form"):
            st.subheader("Attendance Record")

            record_id = st.text_input("Record ID", "ATT-DEMO-001")
            attendance_employee = st.text_input("Employee ID", "EMP-0002")
            period = st.text_input("Period", "2026-10")

            col1, col2 = st.columns(2)

            with col1:
                scheduled_days = st.number_input(
                    "Scheduled Days", min_value=0, value=22
                )
                present_days = st.number_input(
                    "Present Days", min_value=0, value=20
                )
                avg_hours = st.number_input(
                    "Average Hours Worked",
                    min_value=0.0,
                    max_value=24.0,
                    value=8.0,
                )

            with col2:
                attendance_rate = st.number_input(
                    "Attendance Rate (0–1)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.91,
                    step=0.01,
                )
                overtime = st.number_input(
                    "Overtime Hours", min_value=0.0, value=0.0
                )
                unpaid_absence = st.number_input(
                    "Unpaid Absence Days", min_value=0, value=0
                )

            submitted = st.form_submit_button("Analyze Attendance")

        if submitted:
            if not record_id.strip() or not attendance_employee.strip() or not period.strip():
                st.warning("Please complete all required fields.")
            elif present_days > scheduled_days:
                st.warning("Present days cannot exceed scheduled days.")
            else:
                payload = {
                    "record_id": record_id.strip(),
                    "employee_id": attendance_employee.strip(),
                    "period": period.strip(),
                    "scheduled_days": scheduled_days,
                    "present_days": present_days,
                    "avg_hours_worked": avg_hours,
                    "attendance_rate": attendance_rate,
                    "overtime_hours": overtime,
                    "unpaid_absence_days": unpaid_absence,
                }

                try:
                    result = api_request(
                        "POST",
                        "/v1/anomaly/attendance",
                        json=payload,
                    )

                    st.subheader("Attendance Analysis")
                    st.metric("Anomaly Score", f"{result['anomaly_score']:.3f}")
                    st.write("Flagged:", result["flagged"])
                    st.write("Reason:", result["reason_text"])
                    st.write("Employee:", result["employee_id"])
                    st.warning("AI-generated — for human review")

                except APIError as error:
                    show_api_error(error)

    else:
        with st.form("payroll_form"):
            st.subheader("Payroll Record")

            record_id = st.text_input("Record ID", "PAY-DEMO-001")
            payroll_employee = st.text_input("Employee ID", "EMP-0002")
            period = st.text_input("Period", "2026-10")

            monthly_fixed_gross = st.number_input(
                "Monthly Fixed Gross", min_value=0.01, value=30000.0
            )
            gross_pay = st.number_input(
                "Gross Pay", min_value=0.0, value=30000.0
            )
            total_deductions = st.number_input(
                "Total Deductions", min_value=0.0, value=3000.0
            )
            net_pay = st.number_input(
                "Net Pay", min_value=0.0, value=27000.0
            )
            overtime_paid = st.number_input(
                "Overtime Hours Paid", min_value=0.0, value=0.0
            )
            duplicate_payment = st.checkbox("Possible duplicate payment")

            submitted = st.form_submit_button("Analyze Payroll")

        if submitted:
            if not record_id.strip() or not payroll_employee.strip() or not period.strip():
                st.warning("Please complete all required fields.")
            else:
                payload = {
                    "record_id": record_id.strip(),
                    "employee_id": payroll_employee.strip(),
                    "period": period.strip(),
                    "monthly_fixed_gross": monthly_fixed_gross,
                    "gross_pay": gross_pay,
                    "total_deductions": total_deductions,
                    "net_pay": net_pay,
                    "overtime_hours_paid": overtime_paid,
                    "duplicate_payment": duplicate_payment,
                }

                try:
                    result = api_request(
                        "POST",
                        "/v1/anomaly/payroll",
                        json=payload,
                    )

                    st.subheader("Payroll Analysis")
                    st.metric("Anomaly Score", f"{result['anomaly_score']:.3f}")
                    st.write("Flagged:", result["flagged"])
                    st.write("Reason:", result["reason_text"])

                    if result.get("money_at_risk") is not None:
                        st.metric(
                            "Money at Risk",
                            f"₹{result['money_at_risk']:,.2f}",
                        )

                    st.warning("AI-generated — for human review")

                except APIError as error:
                    show_api_error(error)


with assistant_tab:
    st.header("CortexHR HR Assistant")
    st.write(
        "Ask questions about HR policies, attendance, working hours, "
        "leave and other supported HR topics."
    )

    if "chat_session_id" not in st.session_state:
        import uuid
        st.session_state.chat_session_id = str(uuid.uuid4())

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input("Ask your HR question...")

    if user_message:
        with st.chat_message("user"):
            st.markdown(user_message)

        st.session_state.chat_history.append(
            {"role": "user", "content": user_message}
        )

        try:
            result = api_request(
                "POST",
                "/v1/chat",
                user_id=user_id,
                json={
                    "message": user_message,
                    "session_id": st.session_state.chat_session_id,
                },
            )

            reply = result["reply"]

            with st.chat_message("assistant"):
                st.markdown(reply)
                st.caption("AI-generated — for human review")

            st.session_state.chat_history.append(
                {"role": "assistant", "content": reply}
            )

        except APIError as error:
            show_api_error(error)


with resume_tab:
    st.header("Resume Screener")
    st.write(
        "Rank resumes against a selected job description "
        "to support recruiter review."
    )

    job_options = {
        "J01 - Software Engineer": "J01",
        "J02 - Senior Software Engineer": "J02",
        "J03 - Data Analyst": "J03",
        "J04 - ML Engineer": "J04",
        "J05 - Product Manager": "J05",
        "J06 - Customer Support Executive": "J06",
        "J07 - HR Executive": "J07",
        "J08 - Accountant": "J08",
        "J09 - Account Executive": "J09",
        "J10 - Digital Marketing Executive": "J10",
    }

    with st.form("resume_rank_form"):
        selected_job = st.selectbox(
            "Select Job Position",
            list(job_options.keys()),
        )

        top_n = st.slider(
            "Number of candidates to display",
            min_value=1,
            max_value=100,
            value=10,
        )

        submitted = st.form_submit_button(
            "Rank Resumes",
            type="primary",
        )

    if submitted:
        if not user_id.startswith(("EMP-0011", "EMP-0041", "EMP-0099", "EMP-0107")):
            st.error(
                "Access denied. Resume screening is available "
                "only to HR and Admin demo users."
            )
        else:
            try:
                result = api_request(
                    "POST",
                    "/v1/resume/rank",
                    user_id=user_id,
                    json={
                        "job_id": job_options[selected_job],
                        "top_n": top_n,
                    },
                )

                st.subheader(result["job_title"])
                st.write("Job ID:", result["job_id"])

                rankings = result.get("rankings", [])

                if rankings:
                    st.dataframe(
                        rankings[:top_n],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No resume rankings were returned.")

                if result.get("notice"):
                    st.info(result["notice"])

                st.warning("AI-generated — for human review")

            except APIError as error:
                show_api_error(error)


with forecast_tab:
    st.header("Workforce Forecast")
    st.write(
        "Explore workforce headcount, exits and attrition forecasts "
        "for workforce planning."
    )

    st.info(
        "Forecasts are planning estimates, not guaranteed outcomes "
        "or automated employment decisions."
    )

    metric_options = {
        "Headcount": "headcount_end",
        "Employee Exits": "exits",
        "Monthly Attrition Rate": "attrition_rate_monthly_pct",
    }

    department_options = ["ALL"] + [
        f"D{i:02d}" for i in range(1, 11)
    ]

    with st.form("forecast_form"):
        selected_metric = st.selectbox(
            "Forecast Metric",
            list(metric_options.keys()),
        )

        selected_department = st.selectbox(
            "Department",
            department_options,
        )

        submitted = st.form_submit_button(
            "Load Forecast",
            type="primary",
        )

    if submitted:
        try:
            result = api_request(
                "GET",
                "/v1/forecast",
                user_id=user_id,
                params={
                    "metric": metric_options[selected_metric],
                    "department_id": selected_department,
                },
            )

            st.subheader("Forecast Results")

            st.write("Trained through:", result["trained_through"])
            st.write("Model version:", result["model_version"])

            forecasts = result.get("forecasts", [])

            if forecasts:
                import pandas as pd

                forecast_df = pd.DataFrame(forecasts)

                st.dataframe(
                    forecast_df,
                    use_container_width=True,
                    hide_index=True,
                )

                if "forecast_value" in forecast_df.columns:
                    chart_df = forecast_df[
                        ["forecast_month", "forecast_value"]
                    ].set_index("forecast_month")

                    st.line_chart(chart_df)

            else:
                st.info("No forecast records were returned.")

            st.info(result["notice"])
            st.warning("AI-generated — for human review")

        except APIError as error:
            show_api_error(error)
