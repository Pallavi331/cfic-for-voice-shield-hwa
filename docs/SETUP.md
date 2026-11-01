# CFIC × VoiceShield HackVersion — Local Development & Setup Guide

This guide provides instructions for setting up, running, and testing the CFIC backend locally on Windows, macOS, or Linux.

---

## 1. Prerequisites

- **Python:** Version 3.11 or 3.12 installed.
- **Git:** Standard Git command-line client.
- **Docker & Docker Compose (Optional):** For containerized execution.

---

## 2. Local Environment Setup

### 2.1 Clone Repository
```bash
git clone <GITHUB_REPOSITORY_URL>
cd CFIC-VoiceShield-HackVersion
```

### 2.2 Create Virtual Environment
```bash
# Using Python 3.11 or 3.12
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on macOS/Linux:
source .venv/bin/activate
```

### 2.3 Install Dependencies
```bash
# Install core and testing dependencies
pip install -r requirements-dev.txt

# Or install in editable mode:
pip install -e ".[dev]"
```

### 2.4 Configure Environment Variables
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Review `.env` and configure keys as needed for local testing:
- `CFIC_API_KEY`: Key passed in `X-API-Key` header (default `replace-me-for-local-testing`).
- `CFIC_PELLA_BASE_URL`: URL for Pella service (default `http://localhost:8101`).
- `CFIC_TRANSCRIPTION_BASE_URL`: URL for transcription service (default `http://localhost:8102`).
- `CFIC_ASKDRIP_LLM_BASE_URL` & `CFIC_ASKDRIP_LLM_API_KEY`: Hosted AskDrip LLM endpoint (leave blank to run in mock/skipped mode).

---

## 3. Running Services Locally

### 3.1 Run CFIC API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

### 3.2 Run Standalone Downstream Services (Optional Mocks)
In separate terminal windows:
```bash
# Run PellaV2 Mock Service on port 8101
python services/pella/service.py

# Run Transcription Mock Service on port 8102
python services/transcription/service.py
```

---

## 4. Running with Docker Compose

When Docker is running, you can launch all three microservices in isolated containers with a single command:

```bash
docker compose up --build
```

Services exposed:
- `cfic-api`: `http://localhost:8000`
- `pella-service`: `http://localhost:8101`
- `transcription-service`: `http://localhost:8102`

To shut down:
```bash
docker compose down
```

---

## 5. Verification Commands

### Test Health Endpoint
```bash
curl -X GET http://localhost:8000/health
```

### Test Analysis Endpoint with Audio File
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "X-API-Key: replace-me-for-local-testing" \
  -F "file=@path/to/sample.wav"
```
