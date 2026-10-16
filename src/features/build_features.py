
import pandas as pd


def build_features(employee_df, attendance_df, payroll_df):
    employees = employee_df.copy()
    attendance = attendance_df.copy()
    payroll = payroll_df.copy()

    employees["observation_date"] = pd.to_datetime(
        employees["observation_date"], errors="coerce"
    )
    attendance["month"] = pd.to_datetime(
        attendance["month"], errors="coerce"
    )
    payroll["month"] = pd.to_datetime(
        payroll["month"], errors="coerce"
    )

    def to_numeric(series):
        return pd.to_numeric(
            series.astype("string")
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.strip(),
            errors="coerce",
        )

    # Attendance source columns.
    for column in [
        "attendance_rate",
        "unpaid_absence_days",
        "late_arrivals",
        "avg_hours_worked",
        "overtime_hours",
    ]:
        if column in attendance.columns:
            attendance[column] = to_numeric(attendance[column])

    # Payroll source columns.
    for column in [
        "monthly_fixed_gross",
        "overtime_hours_paid",
        "overtime_pay",
        "gross_pay",
        "total_deductions",
        "net_pay",
        "lop_days",
    ]:
        if column in payroll.columns:
            payroll[column] = to_numeric(payroll[column])


    employees = employees.reset_index(drop=True)
    employees["_snapshot_id"] = employees.index

    snapshots = employees[
        ["_snapshot_id", "employee_id", "observation_date"]
    ]

    # Attendance records available on or before each snapshot month.
    attendance_history = snapshots.merge(
        attendance,
        on="employee_id",
        how="left",
    )

    attendance_history = attendance_history[
        attendance_history["month"].isna()
        | (
            attendance_history["month"].dt.to_period("M")
            <= attendance_history["observation_date"].dt.to_period("M")
        )
    ]

    attendance_features = (
        attendance_history.groupby("_snapshot_id")
        .agg(
            attendance_rate=("attendance_rate", "mean"),
            late_count=("late_arrivals", lambda s: s.sum(min_count=1)),
            average_overtime=("overtime_hours", "mean"),
            unpaid_absence_days=("unpaid_absence_days", "sum"),
        )
        .reset_index()
    )

    # Payroll records available on or before each snapshot month.
    payroll_history = snapshots.merge(
        payroll,
        on="employee_id",
        how="left",
    )

    payroll_history = payroll_history[
        payroll_history["month"].isna()
        | (
            payroll_history["month"].dt.to_period("M")
            <= payroll_history["observation_date"].dt.to_period("M")
        )
    ]

    payroll_features = (
        payroll_history.groupby("_snapshot_id")
        .agg(
            average_monthly_salary=("monthly_fixed_gross", "mean"),
            unpaid_payroll_days=("lop_days", "sum"),
            average_overtime_pay=("overtime_pay", "mean"),
        )
        .reset_index()
    )

    result = employees.merge(
        attendance_features,
        on="_snapshot_id",
        how="left",
        validate="one_to_one",
    )

    result = result.merge(
        payroll_features,
        on="_snapshot_id",
        how="left",
        validate="one_to_one",
    )

    # Required engineered features.
    tenure_months = pd.to_numeric(
        result["tenure_months"], errors="coerce"
    )
    months_since_raise = pd.to_numeric(
        result["months_since_last_raise"], errors="coerce"
    )
    unpaid_leave_days = pd.to_numeric(
        result["unpaid_leave_days_6m"], errors="coerce"
    )
    attendance_rate_3m = pd.to_numeric(
        result["attendance_rate_3m"], errors="coerce"
    )
    overtime_hours_3m = pd.to_numeric(
        result["avg_overtime_hours_per_month_3m"], errors="coerce"
    )

    result["tenure_years"] = tenure_months / 12
    result["raise_overdue"] = (months_since_raise > 12).astype("boolean")
    result["unpaid_per_month"] = unpaid_leave_days / 6
    result["attendance_gap"] = 1 - attendance_rate_3m
    result["overtime_load"] = overtime_hours_3m

    result["tenure"] = tenure_months
    result["months_since_last_revision"] = months_since_raise

    return result.drop(columns=["_snapshot_id"])
