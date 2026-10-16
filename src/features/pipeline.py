import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FEATURE_VERSION = "features-1.0.0"

# Features produced by build_features().
INPUT_FEATURES = [
    "tenure_years",
    "raise_overdue",
    "unpaid_per_month",
    "attendance_gap",
    "overtime_load",
    "attendance_rate",
    "late_count",
    "average_overtime",
    "average_monthly_salary",
    "average_overtime_pay",
    "tenure",
    "months_since_last_revision",
    "department_id",
    "role_id",
    "work_location",
    "work_mode",
    "employment_type",
]

NUMERIC_FEATURES = [
    "tenure_years",
    "unpaid_per_month",
    "attendance_gap",
    "overtime_load",
    "attendance_rate",
    "late_count",
    "average_overtime",
    "average_monthly_salary",
    "average_overtime_pay",
    "tenure",
    "months_since_last_revision",
]

BOOLEAN_FEATURES = ["raise_overdue"]

CATEGORICAL_FEATURES = [
    "department_id",
    "role_id",
    "work_location",
    "work_mode",
    "employment_type",
]

FINAL_FEATURES = INPUT_FEATURES

# Columns that must never be used as model predictors.
FORBIDDEN_FEATURES = {
    "row_id",
    "employee_id",
    "observation_date",
    "left_within_12m",
    "voluntary_left_within_12m",
    "exit_date",
    "resignation_date",
    "exit_reason",
    "exit_interview_done",
    "fnf_settlement_amount",
    "source",
}


def validate_features(X):
    """Validate input columns and reject known leakage columns."""
    if not isinstance(X, pd.DataFrame):
        raise TypeError("Features must be provided as a pandas DataFrame.")

    forbidden = FORBIDDEN_FEATURES.intersection(X.columns)
    if forbidden:
        raise ValueError(
            f"Forbidden identifier or leakage columns found: "
            f"{sorted(forbidden)}"
        )

    missing = [column for column in INPUT_FEATURES
               if column not in X.columns]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

from sklearn.base import BaseEstimator, TransformerMixin

class FeatureValidationTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        validate_features(X)
        return self

    def transform(self, X):
        validate_features(X)
        return X[INPUT_FEATURES].copy()

def create_preprocessing_pipeline():
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    boolean_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("boolean", boolean_pipeline, BOOLEAN_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    return Pipeline([
        ("feature_validation", FeatureValidationTransformer()),
        ("preprocessor", preprocessor),
    ])


def save_pipeline(pipeline, output_dir="models"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        pipeline,
        output_path / "feature_pipeline.joblib",
    )

    metadata = {
        "version": FEATURE_VERSION,
        "input_features": INPUT_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "boolean_features": BOOLEAN_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "forbidden_features": sorted(FORBIDDEN_FEATURES),
    }

    with (output_path / "metadata.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(metadata, file, indent=4)

    print("Pipeline and metadata saved successfully.")