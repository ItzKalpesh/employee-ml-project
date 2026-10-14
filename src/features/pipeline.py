
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


FEATURE_VERSION = "features-1.0.0"

# Features required as input to the pipeline
INPUT_FEATURES = [
    "attendance_rate",
    "late_count",
    "average_overtime",
    "tenure",
    "annual_fixed_pay",
    "months_since_last_revision",
    "department_id",
    "role_id",
    "work_location",
    "work_mode",
    "employment_type",
]

# Keep this name for compatibility with the notebook and runner.
FINAL_FEATURES = INPUT_FEATURES

NUMERIC_FEATURES = [
    "attendance_rate",
    "late_count",
    "average_overtime",
    "tenure",
    "salary_vs_department_median",
    "months_since_last_revision",
]

CATEGORICAL_FEATURES = [
    "department_id",
    "role_id",
    "work_location",
    "work_mode",
    "employment_type",
]


class DepartmentMedianRatioAdder(BaseEstimator, TransformerMixin):
    """Calculate salary ratio using department medians learned during fit."""

    def fit(self, X, y=None):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")

        required = ["department_id", "annual_fixed_pay"]
        missing = [col for col in required if col not in X.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        salary = pd.to_numeric(
            X["annual_fixed_pay"].astype(str).str.replace(
                ",", "", regex=False
            ),
            errors="coerce",
        )

        salary_data = pd.DataFrame({
            "department_id": X["department_id"],
            "salary": salary,
        })

        self.department_medians_ = (
            salary_data.groupby("department_id")["salary"].median()
        )
        self.global_median_ = salary.median()

        return self

    def transform(self, X):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")

        result = X.copy()

        salary = pd.to_numeric(
            result["annual_fixed_pay"].astype(str).str.replace(
                ",", "", regex=False
            ),
            errors="coerce",
        )

        denominator = result["department_id"].map(
            self.department_medians_
        )
        denominator = denominator.fillna(self.global_median_)
        denominator = denominator.mask(denominator.eq(0))

        result["salary_vs_department_median"] = salary / denominator

        return result


def create_preprocessing_pipeline():
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
    ])

    return Pipeline([
        ("department_ratio", DepartmentMedianRatioAdder()),
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
        "categorical_features": CATEGORICAL_FEATURES,
        "final_features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
    }

    with open(output_path / "metadata.json", "w") as file:
        json.dump(metadata, file, indent=4)

    print("Pipeline and metadata saved successfully.")
