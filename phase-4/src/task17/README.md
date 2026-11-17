# CortexHR API — Task 17

## Overview

CortexHR is a versioned FastAPI service for HR analytics, anomaly detection, resume ranking, attrition risk prediction, and HR FAQ chatbot functionality. It also provides a Gradio prediction dashboard.

## Features

- Versioned REST API using `/v1`
- Models loaded once during application startup
- Pydantic request and response validation
- Attendance anomaly detection
- Payroll anomaly detection
- Attrition risk prediction
- Resume ranking
- HR chatbot with privacy safeguards
- Health monitoring endpoint
- CORS middleware
- Gradio prediction dashboard

## Requirements

Python 3.12 or later.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Prepare Models

From the repository root:

```bash
python src/prepare_anomaly_models.py
```

Ensure the required model artifacts are available under `models/`.

## Start the API

From `05_Starter/api_skeleton`:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Swagger UI:

`http://localhost:8000/docs`

Health:

`GET /v1/health`

### Available endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/v1/health` | API health |
| POST | `/v1/resume/rank` | Resume ranking |
| GET | `/v1/attrition/risk/{employee_id}` | Attrition risk |
| POST | `/v1/anomaly/attendance` | Attendance anomaly |
| POST | `/v1/anomaly/payroll` | Payroll anomaly |
| POST | `/v1/chat` | HR chatbot |

## Prediction Dashboard

Open:

`http://localhost:8000/ui`

The Gradio dashboard provides attendance and payroll anomaly prediction interfaces.

## Smoke Testing

Run:

```bash
python smoke_test.py
```

The smoke test checks health, attrition, attendance, payroll, resume ranking, and chatbot endpoints.

## Deployment

The API can be deployed using Render, Railway, Hugging Face Spaces, or AWS. Configure environment variables and ensure model artifacts and datasets are available in the deployment environment.

## Limitations

Anomaly flags and attrition scores support human review only. They must not be used as the sole basis for employment decisions. Anomaly flags do not establish fraud or misconduct.