
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODELS = ROOT / "models"

VERSION = "1.0.0"


def save_detector(name, feature_columns, data, detector, metadata):
    """Fit and save preprocessing and anomaly detector together."""
    artifact_dir = MODELS / name / VERSION
    artifact_dir.mkdir(parents=True, exist_ok=True)

    X = data[feature_columns].replace([np.inf, -np.inf], np.nan)

    # Prevent an entirely empty feature from breaking median imputation.
    usable_columns = [
        col for col in feature_columns if X[col].notna().any()
    ]
    if len(usable_columns) != len(feature_columns):
        missing = sorted(set(feature_columns) - set(usable_columns))
        raise ValueError(f"{name}: features contain no usable values: {missing}")

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("detector", detector),
    ])

    pipeline.fit(X[usable_columns])

    joblib.dump(pipeline, artifact_dir / "model.joblib")

    metadata.update({
        "model_name": name,
        "model_version": VERSION,
        "feature_columns": usable_columns,
        "training_rows": int(len(X)),
        "algorithm": "IsolationForest",
    })

    (artifact_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved {name}: {artifact_dir}")
    print(f"Features: {usable_columns}")
    print(f"Training rows: {len(X)}")


def main():
    # ---------------------------------------------------------
    # 1. Attendance anomaly detector
    # ---------------------------------------------------------
    attendance = pd.read_csv(DATA / "attendance_monthly_features.csv")
    baselines = pd.read_csv(DATA / "anomaly_baselines.csv")

    attendance_rows = baselines[
        baselines["task"].astype(str).str.contains(
            "Attendance anomalies", case=False, na=False
        )
    ]

    if attendance_rows.empty:
        raise ValueError(
            "Attendance anomaly definition was not found in anomaly_baselines.csv"
        )

    baseline_feature_text = str(attendance_rows.iloc[0]["features"])
    baseline_features = [
        col.strip()
        for col in baseline_feature_text.split(",")
        if col.strip()
    ]

    feature_columns = [
        col for col in baseline_features
        if col in attendance.columns
        and pd.api.types.is_numeric_dtype(attendance[col])
    ]

    if len(feature_columns) < 2:
        raise ValueError(
            "Could not resolve attendance features.\n"
            f"Parsed: {baseline_features}\n"
            f"Available columns: {attendance.columns.tolist()}"
        )

    print("Attendance features:", feature_columns)

    save_detector(
        name="attendance_anomaly",
        feature_columns=feature_columns,
        data=attendance,
        detector=IsolationForest(
            n_estimators=200,
            contamination=0.03,
            random_state=42,
        ),
        metadata={
            "data_file": "data/attendance_monthly_features.csv",
            "contamination": 0.03,
            "reason_rules": {
                "low_attendance_rate": 0.75,
                "long_unpaid_streak_days": 5,
                "unpaid_absence_days": 5,
                "late_arrivals": 5,
            },
        },
    )

        # ---------------------------------------------------------
    # 2. Payroll anomaly detector
    # ---------------------------------------------------------
    payroll = pd.read_csv(DATA / "payroll_monthly_features.csv")

    numeric_source_columns = [
        "monthly_fixed_gross",
        "gross_pay",
        "total_deductions",
        "net_pay",
        "overtime_hours_paid",
    ]

    for col in numeric_source_columns:
        if col not in payroll.columns:
            raise ValueError(f"Missing payroll source column: {col}")

        payroll[col] = pd.to_numeric(
            payroll[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip(),
            errors="coerce",
        )

    required_columns = [
        "gross_pay",
        "monthly_fixed_gross",
        "total_deductions",
        "net_pay",
        "overtime_hours_paid",
        "employee_id",
        "month",
    ]
    missing = [col for col in required_columns if col not in payroll.columns]
    if missing:
        raise ValueError(f"Payroll data is missing required columns: {missing}")

    # Reproduce the engineered features used in Task 6.
    eps = 1e-6

    payroll["gross_vs_fixed"] = (
        payroll["gross_pay"]
        / payroll["monthly_fixed_gross"].where(
            payroll["monthly_fixed_gross"].abs() > eps
        )
    )

    payroll["deduction_ratio"] = (
        payroll["total_deductions"]
        / payroll["gross_pay"].where(payroll["gross_pay"].abs() > eps)
    )

    payroll["net_ratio"] = (
        payroll["net_pay"]
        / payroll["gross_pay"].where(payroll["gross_pay"].abs() > eps)
    )

    payroll["net_reconciliation_gap"] = (
        payroll["gross_pay"]
        - payroll["total_deductions"]
        - payroll["net_pay"]
    )

    payroll["deductions_over_gross"] = (
        payroll["total_deductions"] > payroll["gross_pay"] + 0.01
    ).astype(int)

    payroll["negative_net_pay"] = (payroll["net_pay"] < 0).astype(int)

    # Use the exact Task 6 model feature schema.
    payroll_features = [
        "gross_vs_fixed",
        "deduction_ratio",
        "net_ratio",
        "overtime_hours_paid",
        "net_reconciliation_gap",
        "deductions_over_gross",
        "negative_net_pay",
    ]

    missing = [col for col in payroll_features if col not in payroll.columns]
    if missing:
        raise ValueError(f"Payroll model features are missing: {missing}")

    payroll_features = [
        col for col in payroll_features
        if pd.api.types.is_numeric_dtype(payroll[col])
    ]

    if len(payroll_features) < 3:
        raise ValueError(
            f"Not enough numeric payroll features: {payroll_features}"
        )

    print("\nPayroll features:", payroll_features)

    save_detector(
        name="payroll_anomaly",
        feature_columns=payroll_features,
        data=payroll,
        detector=IsolationForest(
            n_estimators=300,
            contamination=0.025,
            random_state=42,
            n_jobs=-1,
        ),
        metadata={
            "data_file": "data/payroll_monthly_features.csv",
            "contamination": 0.025,
            "reason_rules": [
                "duplicate_payment_rule",
                "negative_net_pay",
                "deductions_over_gross",
                "reconciliation_rule",
            ],
        },
    )


if __name__ == "__main__":
    main()
