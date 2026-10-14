import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import json
from pathlib import Path

import joblib
import pandas as pd

from src.features.build_features import build_features
from src.features.pipeline import FINAL_FEATURES

ROOT = Path("/workspace")
DATA = ROOT / "data"
MODELS = ROOT / "models"

employees = pd.read_csv(DATA / "attrition_dataset.csv")
attendance = pd.read_csv(DATA / "attendance_monthly_features.csv")
payroll = pd.read_csv(DATA / "payroll_monthly_features.csv")


features = build_features(employees, attendance, payroll)
X = features[FINAL_FEATURES]

pipeline = joblib.load(MODELS / "feature_pipeline.joblib")
transformed = pipeline.transform(X)

print("Feature pipeline executed successfully.")
print("Input rows:", len(X))
print("Transformed shape:", transformed.shape)

with open(MODELS / "metadata.json", "r") as file:
    metadata = json.load(file)

print("Feature version:", metadata["version"])
