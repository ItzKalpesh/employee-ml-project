
import pandas as pd


def build_features(employee_df, attendance_df, payroll_df):
    employees = employee_df.copy()
    attendance = attendance_df.copy()
    payroll = payroll_df.copy()

    employees["observation_date"] = pd.to_datetime(
        employees["observation_date"]
    )
    attendance["month"] = pd.to_datetime(attendance["month"])
    payroll["month"] = pd.to_datetime(payroll["month"])
    
    # Ensure monthly measurement columns are numeric.
    for column in ["attendance_rate", "late_arrivals", "overtime_hours"]:
        attendance[column] = pd.to_numeric(
            attendance[column], errors="coerce"
        )

    payroll["monthly_fixed_gross"] = pd.to_numeric(
        payroll["monthly_fixed_gross"], errors="coerce"
    )

    
    # Give every employee snapshot a unique identifier.
    employees = employees.reset_index(drop=True)
    employees["_snapshot_id"] = employees.index

    # Attendance: retain records available by each snapshot date.
    attendance_history = employees[
        ["_snapshot_id", "employee_id", "observation_date"]
    ].merge(
        attendance,
        on="employee_id",
        how="left"
    )

    attendance_history = attendance_history[
        attendance_history["month"].isna()
        | (
            attendance_history["month"].dt.to_period("M")
            <= attendance_history["observation_date"].dt.to_period("M")
        )
    ]

    attendance_features = attendance_history.groupby(
        "_snapshot_id"
    ).agg(
        attendance_rate=("attendance_rate", "mean"),
       late_count=("late_arrivals", lambda s: s.sum(min_count=1)),
        average_overtime=("overtime_hours", "mean")
    ).reset_index()

    # Payroll: remove duplicate payroll items before aggregation.
    payroll = payroll.drop_duplicates(
        subset=[
            column for column in payroll.columns
            if column != "payroll_item_id"
        ]
    )

    payroll_history = employees[
        ["_snapshot_id", "employee_id", "observation_date"]
    ].merge(
        payroll,
        on="employee_id",
        how="left"
    )

    payroll_history = payroll_history[
        payroll_history["month"].isna()
        | (
            payroll_history["month"].dt.to_period("M")
            <= payroll_history["observation_date"].dt.to_period("M")
        )
    ]

    payroll_features = payroll_history.groupby(
        "_snapshot_id"
    ).agg(
        average_monthly_salary=("monthly_fixed_gross", "mean")
    ).reset_index()

    # Join features back to the correct employee snapshot.
    result = employees.merge(
        attendance_features,
        on="_snapshot_id",
        how="left",
        validate="one_to_one"
    )

    result = result.merge(
        payroll_features,
        on="_snapshot_id",
        how="left",
        validate="one_to_one"
    )

    result["tenure"] = result["tenure_months"]
    result["months_since_last_revision"] = result[
        "months_since_last_raise"
    ]


    return result.drop(columns=["_snapshot_id"])
    