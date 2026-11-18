"""Task 20 lightweight artifact/documentation release gate.

Run from repository root: python scripts/task20_release_gate.py
This checks file presence only; it does not rerun statistical evaluations.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "models/attrition/attrition-v2/model.joblib",
    "models/attrition/attrition-v2/metadata.json",
    "models/attendance_anomaly/1.0.0/model.joblib",
    "models/attendance_anomaly/1.0.0/metadata.json",
    "models/payroll_anomaly/1.0.0/model.joblib",
    "models/payroll_anomaly/1.0.0/metadata.json",
    "models/hr_chatbot_bundle.joblib",
    "models/feature_pipeline.joblib",
    "phase-4/models/task16_forecast_metadata.json",
    "phase-4/reports/task16_backtest_metrics.csv",
    "reports/task13_attrition_model_v2_report.md",
    "reports/task15_fair_pay_report.md",
    "phase-4/reports/task16_workforce_forecast_report.md",
    "model_cards/ATTRITION_XGBOOST_V2.md",
    "model_cards/ATTENDANCE_ANOMALY_IFOREST.md",
    "model_cards/PAYROLL_ANOMALY_IFOREST.md",
    "model_cards/HR_FAQ_CHATBOT.md",
    "model_cards/RESUME_SCREENER.md",
    "model_cards/FAIR_PAY_RECOMMENDER.md",
    "model_cards/WORKFORCE_FORECAST.md",
    "architecture/CORTEXHR_ARCHITECTURE.md",
    "RELEASE_NOTES.md",
    "reports/TASK20_FINAL_AUDIT.md",
    "reports/FINAL_CHALLENGE_NOTES.md",
]

missing = []
for rel in REQUIRED:
    exists = (ROOT / rel).is_file()
    print(f"{'PASS' if exists else 'FAIL'}  {rel}")
    if not exists:
        missing.append(rel)

print("\nKnown metric warnings (review manually):")
print("- Attrition calibrated recall at 0.50: 0.0172 (1.72%).")
print("- Payroll anomaly precision: 0.2011 (20.11%).")
print("- Exits forecast seasonal-baseline WAPE: 81.484%.")
print("- Monthly attrition forecast seasonal-baseline WAPE: 44.759%.")
print("\nThis gate checks artifact presence only; it does not rerun model evaluations.")

if missing:
    print(f"\nBLOCKED: {len(missing)} required files are missing.")
    sys.exit(1)

print("\nPASS: Required release artifacts are present.")
