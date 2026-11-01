# CloudForge Intelligence Core (CFIC) × VoiceShield HackVersion

**Developed by Team SAIL for HackWithAditya**  
**Repository Lead & System Architect:** Sainadh

---

## 1. Overview

**CloudForge Intelligence Core (CFIC)** is the intelligence engine powering **VoiceShield**, a real-time defense system protecting mobile and enterprise voice calls against AI-generated deepfake voices and conversational fraud.

CFIC orchestrates parallel acoustic deepfake detection and semantic risk analysis, fusing the signals through a hardened **Temporal and Contextual Evidence Decision (TCED)** policy engine.

---

## 2. Core Architecture

```
VoiceShield Client
       │
       ▼ (HTTP POST /v1/analyze, X-API-Key, audio payload)
┌────────────────────────────────────────────────────────┐
│                        CFIC API                        │
│  - X-API-Key Authentication                            │
│  - Sliding Window Rate Limiting                        │
│  - Max Audio Payload Validation (25 MiB)               │
│  - Request ID Tracing (X-Request-ID)                   │
└────────────────────────────────────────────────────────┘
       │
       ├─────────────────────────────────┐ (asyncio.gather)
       ▼                                 ▼
┌───────────────────────────┐     ┌───────────────────────────┐
│  PellaV2 Detector Service │     │   Transcription Service   │
│  (Port 8101 /predict)     │     │   (Port 8102 /transcribe) │
│  Owner: Varshu & Varun    │     │   Owner: Pallavi          │
└───────────────────────────┘     └───────────────────────────┘
       │                                 │
       │ (Synthetic Score)               ▼ (Call Transcript)
       │                          ┌───────────────────────────┐
       │                          │  Hosted AskDrip LLM API   │
       │                          │  (RIAS Conversational)    │
       │                          │  Owner: Sainadh           │
       │                          └───────────────────────────┘
       │                                 │ (Risk Level: LOW/MED/HIGH)
       └────────────────┬────────────────┘
                        ▼
       ┌─────────────────────────────────┐
       │           TCED Engine           │
       │  Mandatory Override & Fusion    │
       └─────────────────────────────────┘
                        │
                        ▼
       ┌─────────────────────────────────┐
       │       Normalized Response       │
       │ GENUINE / FAKE / SUSPICIOUS /   │
       │          INCONCLUSIVE           │
       └─────────────────────────────────┘
```

### Key Decision Rules
- **Locked Safety Rule:** If RIAS returns `HIGH` conversational risk, the final outcome **MUST be `SUSPICIOUS`**, regardless of PellaV2's acoustic detection verdict.
- **Fail-Safe Policy:** If services fail, time out, or provide missing/partial evidence, the system returns `INCONCLUSIVE`. It **never silently classifies an error as `GENUINE`**.
- **Excluded Components:** Separate LID model, LACR routing, 7 cluster models, DSR, and separate XLS-R service are explicitly excluded.

---

## 3. Team SAIL Roles & Responsibilities

| Contributor | Role | Primary Responsibility | Suggested Feature Branch |
| :--- | :--- | :--- | :--- |
| **Sainadh** | Project Lead & Architect | CFIC API, Auth, Rate Limiter, Parallel Orchestration, AskDrip LLM, TCED, PR Reviews | `main` |
| **Varun** | MLOps Architect | PellaV2 Checkpoint Verification, Score Semantics, INT8 Quantization, Model Manifest | `feature/varun-pellav2-model-preparation` |
| **Varshu** | Cloud Engineer | PellaV2 Docker Service (`services/pella/`), Health/Inference Endpoints, Latency Benchmarks | `feature/varshu-pellav2-docker-service` |
| **Pallavi** | Cloud Engineer | Multilingual Speech Transcription (`services/transcription/`), Whisper vs IndicConformer Benchmark | `feature/pallavi-transcription-service` |

---

## 4. Quick Start

### 4.1 Local Development (Python 3.11+)
```bash
# 1. Clone repository
git clone <GITHUB_REPOSITORY_URL>
cd CFIC-VoiceShield-HackVersion

# 2. Create virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements-dev.txt

# 4. Configure environment
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux

# 5. Run test suite
python -m pytest -v

# 6. Run CFIC API locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### 4.2 Docker Compose
```bash
docker compose up --build
```
Launches `cfic-api` (port 8000), `pella-service` (port 8101), and `transcription-service` (port 8102).

---

## 5. Documentation Directory

- [Architecture Specification](file:///C:/MyProjects/CFIC-VoiceShield-HackVersion/docs/ARCHITECTURE.md)
- [API & Service Contracts](file:///C:/MyProjects/CFIC-VoiceShield-HackVersion/docs/API_CONTRACTS.md)
- [Contribution & PR Guidelines](file:///C:/MyProjects/CFIC-VoiceShield-HackVersion/docs/CONTRIBUTING.md)
- [Team Task Specifications](file:///C:/MyProjects/CFIC-VoiceShield-HackVersion/docs/TEAM_TASKS.md)
- [Setup & Run Guide](file:///C:/MyProjects/CFIC-VoiceShield-HackVersion/docs/SETUP.md)
- [Testing Strategy](file:///C:/MyProjects/CFIC-VoiceShield-HackVersion/docs/TESTING.md)
- [Decisions & TBD Register](file:///C:/MyProjects/CFIC-VoiceShield-HackVersion/docs/DECISIONS_AND_TBDS.md)
