# CortexHR API — Task 17

## Overview

CortexHR is a versioned FastAPI service for HR analytics, anomaly detection, resume ranking, attrition risk prediction, and HR FAQ chatbot functionality. It also provides a Gradio-based prediction dashboard.

## Features

- Versioned REST API using the `/v1` prefix
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
- Docker-based deployment support
- Automated API smoke testing

## Project Structure

```text
phase-4/
└── src/
    └── task17/
        ├── app/
        │   ├── main.py
        │   ├── attrition_service.py
        │   ├── chatbot_service.py
        │   ├── resume_service.py
        │   └── ui.py
        ├── Dockerfile
        ├── requirements.txt
        ├── .env.example
        ├── README.md
        └── smoke_test.py
```

Model artifacts and datasets required by the API are maintained in the repository's shared `models/` and `data/` directories.

## Requirements

- Python 3.12 or later
- pip
- Docker (for containerized execution)

## Installation

Run the following commands from the repository root:

```bash
pip install -r phase-4/src/task17/requirements.txt
```

Ensure that the required model artifacts and datasets are available in the repository's `models/` and `data/` directories.

## Environment Configuration

The project includes an `.env.example` file.

Create a `.env` file if environment-specific configuration is required:

```bash
cp phase-4/src/task17/.env.example phase-4/src/task17/.env
```

Configure the required values before deployment. Do not commit secrets or private credentials.

## Running the API Locally

Run this command from the repository root:

```bash
python -m uvicorn app.main:app --app-dir phase-4/src/task17 --host 0.0.0.0 --port 8000
```

The API will be available at:

- API base URL: `http://localhost:8000`
- Swagger documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`
- Health endpoint: `http://localhost:8000/v1/health`
- Gradio dashboard: `http://localhost:8000/ui`

## API Documentation

All application endpoints use the `/v1` version prefix.

### Available Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/v1/health` | Checks API health and service status |
| POST | `/v1/resume/rank` | Ranks resumes against job requirements |
| GET | `/v1/attrition/risk/{employee_id}` | Retrieves employee attrition risk |
| POST | `/v1/anomaly/attendance` | Detects attendance anomalies |
| POST | `/v1/anomaly/payroll` | Detects payroll anomalies |
| POST | `/v1/chat` | Answers HR-related questions |

### Interactive API Testing

Open Swagger UI:

```text
http://localhost:8000/docs
```

Swagger UI allows users to inspect endpoint schemas, provide request data, execute API calls, and view responses.

### Health Check Example

Request:

```http
GET /v1/health
```

Example response:

```json
{
  "status": "ok",
  "service": "cortexhr"
}
```

## Prediction Dashboard

The project includes a Gradio-based interface for interacting with the anomaly detection functionality.

Open:

```text
http://localhost:8000/ui
```

The dashboard provides interfaces for:

- Attendance anomaly prediction
- Payroll anomaly prediction

Users can submit input data and view the corresponding model predictions.

## Smoke Testing

The project includes an automated smoke-test script that checks the availability and basic functionality of all six API endpoints.

Run it from the repository root:

```bash
python phase-4/src/task17/smoke_test.py
```

The script checks:

1. API health
2. Attrition risk
3. Attendance anomaly detection
4. Payroll anomaly detection
5. Resume ranking
6. HR chatbot

Expected successful result:

```text
CortexHR API Smoke Test
PASS: Health HTTP 200
PASS: Attrition Risk HTTP 200
PASS: Attendance Anomaly HTTP 200
PASS: Payroll Anomaly HTTP 200
PASS: Resume Ranking HTTP 200
PASS: Chatbot HTTP 200
Results: 6/6 tests passed
```

The API must be running before executing the smoke test.

## Docker Deployment

A dedicated Dockerfile is provided for Task 17:

```text
phase-4/src/task17/Dockerfile
```

Build the Docker image from the repository root:

```bash
docker build -f phase-4/src/task17/Dockerfile -t cortexhr-api .
```

Run the container:

```bash
docker run -d --name cortexhr-api -p 8000:8000 cortexhr-api
```

Verify the service:

```text
http://localhost:8000/docs
http://localhost:8000/v1/health
http://localhost:8000/ui
```

## Hosting Platform Comparison

The following platforms were considered for deploying the CortexHR API.

| Platform | Advantages | Considerations |
|---|---|---|
| Render | Supports Docker-based web services and straightforward GitHub integration | Free-tier services may have resource and availability limitations |
| Railway | Simple deployment workflow, Docker support, and environment variable configuration | Usage-based pricing and resource limits should be considered |
| Hugging Face Spaces | Useful for hosting ML demos and Gradio applications | API deployment configuration and resource availability may be limiting |
| AWS | Flexible infrastructure, scalability, and extensive deployment options | Requires more configuration and cloud infrastructure knowledge |

### Selected Deployment Platform

Render is considered a suitable option for deploying this Docker-based FastAPI application because it supports Dockerfiles and GitHub-connected deployments.

The deployment configuration should use:

- Runtime: Docker
- Branch: `task17-release-api`
- Dockerfile path: `phase-4/src/task17/Dockerfile`
- Docker build context: Repository root (`.`)

The deployed service should be tested using its live health endpoint, Swagger documentation, prediction dashboard, and smoke-test script.

**Deployment status:** Local Docker execution and API smoke tests have been verified. Live deployment should be marked complete only after the hosted service is successfully deployed and its endpoints are tested.

## Limitations and Responsible Use

- Attrition predictions are intended to support HR review and should not independently determine employment decisions.
- Attendance and payroll anomaly flags indicate unusual patterns; they do not establish fraud, misconduct, or intentional wrongdoing.
- Resume ranking should support human review rather than replace recruitment decisions.
- HR chatbot responses should be treated as informational assistance.
- Employee information and private payroll data must be protected.
- Production deployments should use appropriate authentication, authorization, and secure environment configuration.

## Task 17 Verification

| Requirement | Status |
|---|---|
| Versioned FastAPI endpoints | Completed |
| Model loading during startup | Completed |
| Pydantic validation | Completed |
| Error handling and CORS | Implemented |
| Health endpoint | Verified locally |
| Automated smoke testing | Passed — 6/6 |
| Docker image build | Successful |
| Gradio prediction dashboard | Verified locally |
| API documentation | Available through Swagger |
| Hosting platform comparison | Documented |
| Live deployment | Pending deployment and verification |

