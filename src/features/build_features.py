import pandas as pd


def _to_numeric(series):
    """Convert numeric strings, including formatted currency, to numbers."""
    return pd.to_numeric(
        series.astype("string")
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.strip(),
        errors="coerce",
    )


class AttendanceFeatureTransformer:
    """Clean and aggregate attendance records for each employee snapshot."""

    NUMERIC_COLUMNS = [
        "attendance_rate",
        "unpaid_absence_days",
        "late_arrivals",
        "avg_hours_worked",
        "overtime_hours",
    ]

    def transform(self, snapshots, attendance_df):
        attendance = attendance_df.copy()
        attendance["month"] = pd.to_datetime(
            attendance["month"], errors="coerce"
        )

        for column in self.NUMERIC_COLUMNS:
            if column in attendance.columns:
                attendance[column] = _to_numeric(attendance[column])

        history = snapshots.merge(
            attendance,
            on="employee_id",
            how="left",
        )

        snapshot_month = history["observation_date"].dt.to_period("M")
        record_month = history["month"].dt.to_period("M")

        history = history[
            history["month"].isna()
            | (record_month <= snapshot_month)
        ]

        return (
            history.groupby("_snapshot_id")
            .agg(
                attendance_rate=("attendance_rate", "mean"),
                late_count=(
                    "late_arrivals",
                    lambda series: series.sum(min_count=1),
                ),
                average_overtime=("overtime_hours", "mean"),
                unpaid_absence_days=("unpaid_absence_days", "sum"),
            )
            .reset_index()
        )


class PayrollFeatureTransformer:
    """Clean and aggregate payroll records for each employee snapshot."""

    NUMERIC_COLUMNS = [
        "monthly_fixed_gross",
        "overtime_hours_paid",
        "overtime_pay",
        "gross_pay",
        "total_deductions",
        "net_pay",
        "lop_days",
    ]

    def transform(self, snapshots, payroll_df):
        payroll = payroll_df.copy()
        payroll["month"] = pd.to_datetime(
            payroll["month"], errors="coerce"
        )

        for column in self.NUMERIC_COLUMNS:
            if column in payroll.columns:
                payroll[column] = _to_numeric(payroll[column])

        history = snapshots.merge(
            payroll,
            on="employee_id",
            how="left",
        )

        snapshot_month = history["observation_date"].dt.to_period("M")
        record_month = history["month"].dt.to_period("M")

        history = history[
            history["month"].isna()
            | (record_month <= snapshot_month)
        ]

        return (
            history.groupby("_snapshot_id")
            .agg(
                average_monthly_salary=("monthly_fixed_gross", "mean"),
                unpaid_payroll_days=("lop_days", "sum"),
                average_overtime_pay=("overtime_pay", "mean"),
            )
            .reset_index()
        )


def build_features(employee_df, attendance_df, payroll_df):
    """Build employee-level features using separate source transformers."""
    employees = employee_df.copy()

    employees["observation_date"] = pd.to_datetime(
        employees["observation_date"], errors="coerce"
    )

    employees = employees.reset_index(drop=True)
    employees["_snapshot_id"] = employees.index

    snapshots = employees[
        ["_snapshot_id", "employee_id", "observation_date"]
    ].copy()

    # Transform attendance and payroll independently.
    attendance_features = AttendanceFeatureTransformer().transform(
        snapshots, attendance_df
    )

    payroll_features = PayrollFeatureTransformer().transform(
        snapshots, payroll_df
    )

    # Join the aggregated features back to the matching employee snapshot.
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
    result["raise_overdue"] = (
        months_since_raise > 12
    ).astype("boolean")
    result["unpaid_per_month"] = unpaid_leave_days / 6
    result["attendance_gap"] = 1 - attendance_rate_3m
    result["overtime_load"] = overtime_hours_3m

    result["tenure"] = tenure_months
    result["months_since_last_revision"] = months_since_raise

    return result.drop(columns=["_snapshot_id"])