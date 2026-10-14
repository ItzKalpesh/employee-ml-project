
import json
from pathlib import Path

import joblib
import pandas as pd

from src.features.build_features import build_features
from src.features.pipeline import FINAL_FEATURES

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
MODELS = ROOT / "models"


def main():
    employees = pd.read_csv(DATA / "attrition_dataset.csv")
    attendance = pd.read_csv(DATA / "attendance_monthly_features.csv")
    payroll = pd.read_csv(DATA / "payroll_monthly_features.csv")

    features = build_features(employees, attendance, payroll)
    X = features[FINAL_FEATURES]

    pipeline_path = MODELS / "feature_pipeline.joblib"
    metadata_path = MODELS / "metadata.json"

    pipeline = joblib.load(pipeline_path)
    transformed = pipeline.transform(X)

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    print("Feature pipeline executed successfully.")
    print("Input rows:", len(X))
    print("Transformed shape:", transformed.shape)
    print("Feature version:", metadata["version"])


if __name__ == "__main__":
    main()
