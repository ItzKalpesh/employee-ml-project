
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.features.build_features import build_features
from src.features.pipeline import (
    FEATURE_VERSION,
    INPUT_FEATURES,
    create_preprocessing_pipeline,
    save_pipeline,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
MODELS = ROOT / "models"

TARGET = "left_within_12m"
TEST_SIZE = 0.20
RANDOM_STATE = 42

# Columns that must never be used as model predictors.
FORBIDDEN_FEATURES = {
    "row_id",
    "employee_id",
    "observation_date",
    "source",
    "left_within_12m",
    "voluntary_left_within_12m",
    "exit_date",
    "resignation_date",
    "exit_reason",
    "exit_interview_done",
    "fnf_settlement_amount",
}


def main():
    # Load the source datasets.
    employees = pd.read_csv(DATA / "attrition_dataset.csv")
    attendance = pd.read_csv(DATA / "attendance_monthly_features.csv")
    payroll = pd.read_csv(DATA / "payroll_monthly_features.csv")

    # Build features using records available by each observation date.
    features = build_features(employees, attendance, payroll)

    if TARGET not in features.columns:
        raise ValueError(f"Missing target column: {TARGET}")

    # Validate predictors before selecting model inputs.
    forbidden_used = FORBIDDEN_FEATURES.intersection(INPUT_FEATURES)
    if forbidden_used:
        raise ValueError(
            f"Leakage or identifier columns in INPUT_FEATURES: "
            f"{sorted(forbidden_used)}"
        )

    missing = [
        column for column in INPUT_FEATURES
        if column not in features.columns
    ]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    # Only rows with known target labels can be used for supervised learning.
    labelled = features.loc[features[TARGET].notna()].copy()
    y = labelled[TARGET]

    if y.nunique() != 2:
        raise ValueError(
            f"{TARGET} must contain two classes; found {y.nunique()}."
        )

    # Split before fitting any imputers, scalers, or encoders.
    train_indices, _ = train_test_split(
        labelled.index,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    X_train = labelled.loc[train_indices, INPUT_FEATURES]

    # Fit all preprocessing statistics on training data only.
    pipeline = create_preprocessing_pipeline()
    pipeline.fit(X_train)

    # Save the fitted preprocessing artifact and its metadata.
    save_pipeline(pipeline, MODELS)

    # Confirm the saved artifact can transform the training data.
    transformed = pipeline.transform(X_train)

    metadata_path = MODELS / "metadata.json"
    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    metadata["target"] = TARGET
    metadata["test_size"] = TEST_SIZE
    metadata["random_state"] = RANDOM_STATE
    metadata["training_rows"] = int(len(X_train))
    metadata["test_rows"] = int(len(labelled) - len(X_train))
    metadata["fitted_on_training_data_only"] = True

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    print("Feature pipeline built successfully.")
    print("Total labelled rows:", len(labelled))
    print("Training rows:", len(X_train))
    print("Held-out rows:", len(labelled) - len(X_train))
    print("Transformed training shape:", transformed.shape)
    print("Feature version:", FEATURE_VERSION)
    print("Fitted on training data only: True")


if __name__ == "__main__":
    main()
