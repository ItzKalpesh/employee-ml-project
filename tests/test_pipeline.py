
import numpy as np
import pandas as pd
from scipy import sparse

from src.features.pipeline import (
    INPUT_FEATURES,
    create_preprocessing_pipeline,
)


def sample_data():
    """Create sample data using the current pipeline's input schema."""
    data = pd.DataFrame({
        "tenure_years": [2.0, 5.0, 1.5, np.nan, 8.0, 3.0],
        "raise_overdue": [False, True, False, True, None, False],
        "unpaid_per_month": [1.0, 0.0, 2.0, np.nan, 0.5, 1.5],
        "attendance_gap": [0.05, 0.10, 0.02, 0.20, np.nan, 0.08],
        "overtime_load": [4.0, 8.0, 2.0, np.nan, 6.0, 3.0],
        "attendance_rate": [0.95, 0.90, 0.98, np.nan, 0.92, 0.96],
        "late_count": [2.0, 5.0, 1.0, np.nan, 3.0, 0.0],
        "average_overtime": [4.0, 8.0, 2.0, np.nan, 6.0, 3.0],
        "average_monthly_salary": [
            40000.0, 55000.0, 35000.0, np.nan, 80000.0, 45000.0
        ],
        "average_overtime_pay": [
            1000.0, 2000.0, 500.0, np.nan, 1800.0, 700.0
        ],
        "tenure": [24.0, 60.0, 18.0, np.nan, 96.0, 36.0],
        "months_since_last_revision": [
            6.0, 18.0, 9.0, np.nan, 24.0, 12.0
        ],
        "department_id": ["D01", "D02", "D01", None, "D03", "D02"],
        "role_id": ["R01", "R02", "R03", "R01", None, "R02"],
        "work_location": [
            "Pune", "Mumbai", "Pune", "Delhi", "Mumbai", "Pune"
        ],
        "work_mode": [
            "Hybrid", "Remote", "Onsite", "Hybrid", None, "Remote"
        ],
        "employment_type": [
            "Permanent", "Permanent", "Contract",
            "Permanent", "Contract", "Permanent"
        ],
    })

    return data[INPUT_FEATURES]


def test_pipeline_output_shape():
    X = sample_data()
    pipeline = create_preprocessing_pipeline()
    transformed = pipeline.fit_transform(X)

    assert transformed.shape[0] == len(X)
    assert transformed.shape[1] > 0


def test_pipeline_has_no_missing_values_after_transform():
    X = sample_data()
    pipeline = create_preprocessing_pipeline()
    transformed = pipeline.fit_transform(X)

    values = (
        transformed.data
        if sparse.issparse(transformed)
        else np.asarray(transformed)
    )

    assert np.isfinite(values).all()


def test_pipeline_is_reproducible():
    X = sample_data()

    first_pipeline = create_preprocessing_pipeline()
    second_pipeline = create_preprocessing_pipeline()

    first = first_pipeline.fit_transform(X)
    second = second_pipeline.fit_transform(X)

    if sparse.issparse(first) and sparse.issparse(second):
        difference = first - second
        assert difference.nnz == 0
    else:
        np.testing.assert_allclose(
            np.asarray(first),
            np.asarray(second),
        )


def test_required_engineered_features():
    from src.features.build_features import build_features

    employees = pd.DataFrame({
        "employee_id": ["E001", "E002"],
        "observation_date": ["2025-06-30", "2025-06-30"],
        "tenure_months": [24, 36],
        "months_since_last_raise": [18, 6],
        "unpaid_leave_days_6m": [12, 6],
        "attendance_rate_3m": [0.90, 0.95],
        "avg_overtime_hours_per_month_3m": [8.0, 4.0],
    })

    attendance = pd.DataFrame({
        "employee_id": ["E001", "E002"],
        "month": ["2025-05-01", "2025-05-01"],
        "attendance_rate": [0.90, 0.95],
        "unpaid_absence_days": [2, 1],
        "late_arrivals": [3, 1],
        "avg_hours_worked": [8.0, 8.0],
        "overtime_hours": [8.0, 4.0],
    })

    payroll = pd.DataFrame({
        "employee_id": ["E001", "E002"],
        "month": ["2025-05-01", "2025-05-01"],
        "monthly_fixed_gross": [40000.0, 50000.0],
        "overtime_hours_paid": [8.0, 4.0],
        "overtime_pay": [1000.0, 500.0],
        "gross_pay": [41000.0, 50500.0],
        "total_deductions": [5000.0, 6000.0],
        "net_pay": [36000.0, 44500.0],
        "lop_days": [0, 0],
    })

    result = build_features(employees, attendance, payroll)

    required = [
        "tenure_years",
        "raise_overdue",
        "unpaid_per_month",
        "attendance_gap",
        "overtime_load",
    ]

    assert all(column in result.columns for column in required)
    assert result["tenure_years"].tolist() == [2.0, 3.0]
    assert result["raise_overdue"].tolist() == [True, False]
    assert result["unpaid_per_month"].tolist() == [2.0, 1.0]
    np.testing.assert_allclose(
    result["attendance_gap"].tolist(),
    [0.10, 0.05],
)
    assert result["overtime_load"].tolist() == [8.0, 4.0]

def test_pipeline_with_three_raw_rows():
    X = sample_data().iloc[:3].copy()
    pipeline = create_preprocessing_pipeline()

    transformed = pipeline.fit_transform(X)

    assert transformed.shape[0] == 3
    assert transformed.shape[1] > 0
    assert np.isfinite(transformed.data).all()


def test_target_is_never_used_as_input():
    X = sample_data().copy()
    X["left_within_12m"] = [0, 1, 0, 1, 0, 1]

    pipeline = create_preprocessing_pipeline()

    try:
        pipeline.fit_transform(X)
        assert False, "Target column should be rejected"
    except ValueError as error:
        assert "Forbidden" in str(error)