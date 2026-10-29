# CortexHR Anomaly API — Task 8

## Overview

FastAPI service for detecting attendance and payroll anomalies using trained Isolation Forest models. The API returns anomaly scores, rule-based reason codes, explanations, and potential financial exposure where applicable.

## Prerequisites

- Python 3.10 or later
- Project dependencies installed
- Attendance and payroll datasets available in the repository's `data/` directory

## Installation

Run these commands from the repository root:

```powershell
python -m pip install -r .\05_Starter\requirements.txt
```

## Prepare the models

Generate the attendance and payroll model artifacts:

```powershell
python .\src\prepare_anomaly_models.py
```

The script saves model files and metadata under:

- `models/attendance_anomaly/1.0.0/`
- `models/payroll_anomaly/1.0.0/`

The generated `.joblib` files are excluded from Git by `.gitignore`. Generate them locally before starting the API.

## Run the API

From the repository root, run:

```powershell
python -m uvicorn app.main:app --app-dir .\05_Starter\api_skeleton
```

Wait until the terminal reports that application startup is complete.

## API documentation

Open the interactive Swagger UI:

http://127.0.0.1:8000/docs

Health check:

`GET /v1/health`

Attendance anomaly detection:

`POST /v1/anomaly/attendance`

Payroll anomaly detection:

`POST /v1/anomaly/payroll`

The attrition and chat endpoints are outside the scope of Task 8 and are not implemented.

## Run tests

From the repository root:

```powershell
python -m pytest -v
```

The Task 8 implementation was verified locally with 10 passing tests. Re-run the tests after making changes.

## Response interpretation

- `anomaly_score`: model-derived score from 0 to 1; higher values indicate greater anomaly concern.
- `flagged`: whether a statistical anomaly or business rule triggered a flag.
- `reason_code` and `reason_text`: the primary explanation for the flag.
- `money_at_risk`: a potential exposure estimate when available, not a confirmed financial loss.
- `model_version`: version of the detector used.

A successful request returns HTTP 200. Invalid request bodies may return HTTP 422.

## Important limitations

Anomaly flags indicate records that may require investigation; they do not establish fraud, misconduct, or confirmed financial loss. Review the underlying record before taking action.