
import joblib
import numpy as np
import pandas as pd

from src.features.build_features import build_features
from src.features.pipeline import FINAL_FEATURES

employees = pd.read_csv("data/attrition_dataset.csv")
attendance = pd.read_csv("data/attendance_monthly_features.csv")
payroll = pd.read_csv("data/payroll_monthly_features.csv")

features = build_features(employees, attendance, payroll)
X = features[FINAL_FEATURES]

pipeline = joblib.load("models/feature_pipeline.joblib")

first_output = pipeline.transform(X)
second_output = pipeline.transform(X)

if hasattr(first_output, "toarray"):
    first_output = first_output.toarray()

if hasattr(second_output, "toarray"):
    second_output = second_output.toarray()

assert np.array_equal(first_output, second_output), (
    "Reproducibility check failed."
)

print("Reproducibility check passed.")
print("Same input produces identical output.")
print("Output shape:", first_output.shape)
