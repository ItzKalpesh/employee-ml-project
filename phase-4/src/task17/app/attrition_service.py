
import json
import sys
from pathlib import Path

import joblib
import pandas as pd


def load_attrition_service(repo_root):
    """Load the attrition model and prepare employee features once."""

    repo_root = Path(repo_root)

    model_dir = (
        repo_root / "models" / "attrition" / "attrition-v2"
    )

    model_path = model_dir / "model.joblib"
    metadata_path = model_dir / "metadata.json"

    if not model_path.exists() or not metadata_path.exists():
        raise FileNotFoundError("Attrition model artifacts are missing.")

    model = joblib.load(model_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    # Import the original, validated feature engineering function.
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from src.features.build_features import build_features

    employees = pd.read_csv(
        repo_root / "data" / "attrition_scoring_2026.csv"
    )
    attendance = pd.read_csv(
        repo_root / "data" / "attendance_monthly_features.csv"
    )
    payroll = pd.read_csv(
        repo_root / "data" / "payroll_monthly_features.csv"
    )

    engineered = build_features(employees, attendance, payroll)

    if engineered["employee_id"].duplicated().any():
        raise ValueError("Duplicate employee IDs in attrition scoring data.")

    feature_columns = metadata["features"]

    missing = [
        column for column in feature_columns
        if column not in engineered.columns
    ]

    if missing:
        raise ValueError(
            f"Missing attrition model features: {missing}"
        )

    engineered = engineered.set_index("employee_id")

    return model, metadata, engineered


def predict_attrition(model, metadata, employee_features):
    """Return the calibrated 12-month attrition probability."""

    feature_columns = metadata["features"]
    X = employee_features[feature_columns].to_frame().T

    probability = float(model.predict_proba(X)[0][1])

    return {
        "risk_score_12m": round(probability, 4),
        "model_version": metadata["version"],
    }
