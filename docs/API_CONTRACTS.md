# CFIC × VoiceShield HackVersion — API & Service Contracts

This document establishes the official interface specifications between VoiceShield, the CFIC API gateway, downstream detector/transcription services, and the RIAS LLM integration.

---

## 1. CFIC API Gateway Interface

### 1.1 `GET /health`
Verifies availability of the CFIC API gateway and downstream service configurations.

- **Request:** No parameters or headers required.
- **Response (200 OK):**
```json
{
  "status": "ok",
  "service": "cfic-api",
  "version": "0.1.0",
  "environment": "development",
  "downstream_status": {
    "pella_url_configured": "True",
    "transcription_url_configured": "True",
    "askdrip_llm_configured": "False"
  }
}
```

### 1.2 `POST /v1/analyze`
Main ingestion endpoint for VoiceShield client audio streams.

- **Headers:**
  - `X-API-Key` *(string, required)*: Authentication key matching `CFIC_API_KEY`.
  - `X-Request-ID` *(string, optional)*: Tracing UUID. If omitted, one is generated.
- **Request Body:**
  - Content-Type: `multipart/form-data`
  - Form Fields:
    - `file` *(binary upload, required)*: Audio file payload.
- **Constraints:**
  - Max audio file size: 25 MiB (`CFIC_MAX_AUDIO_BYTES`).
  - Allowed MIME types: `audio/wav`, `audio/mpeg`, `audio/ogg`, `audio/flac`, `application/octet-stream`.
  - Rate Limit: Default 30 requests / 60 seconds per client.

- **Success Response (200 OK):**
```json
{
  "request_id": "c1f7a012-78d1-4e78-9e56-11f46d9a8c7b",
  "final_outcome": "SUSPICIOUS",
  "reason_code": "HIGH_RIAS_OVERRIDE",
  "pella_status": "success",
  "rias_transcription_status": "success",
  "rias_risk_status": "success",
  "rias_risk_level": "HIGH",
  "model_version": "pellav2-scaffold-v0.1",
  "latency_ms": {
    "pella": 142.3,
    "transcription": 210.5,
    "rias_llm": 315.0,
    "total": 528.2
  }
}
```

- **Error Responses:**
  - `401 Unauthorized`: Missing or incorrect `X-API-Key`.
  - `400 Bad Request`: Empty audio payload or missing file field.
  - `413 Payload Too Large`: Upload exceeds maximum size limit.
  - `429 Too Many Requests`: Rate limit exceeded (`Retry-After` header included).
  - `500 Internal Server Error`: Unhandled gateway exception.

- **Standard Error Body:**
```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "detail": "Rate limit exceeded. Try again in 14.5 seconds.",
  "request_id": "c1f7a012-78d1-4e78-9e56-11f46d9a8c7b",
  "extra": {
    "retry_after_seconds": 14.5
  }
}
```

---

## 2. PellaV2 Deepfake Detector Contract

**Assigned Engineers:** Varshu (Service Packaging) & Varun (Model Preparation)  
**Base URL:** `http://pella-service:8101`

### 2.1 `GET /health`
- **Response (200 OK):**
```json
{
  "status": "ok",
  "service": "pella-service",
  "model_version": "pellav2-scaffold-v0.1",
  "is_mock": false,
  "artifact_found": true
}
```

### 2.2 `POST /predict`
- **Request:** `multipart/form-data` with `file: UploadFile`.
- **Audio Requirements:** 16 kHz mono WAV recommended.
- **Success Response (200 OK):**
```json
{
  "status": "success",
  "prediction": "GENUINE",
  "score": 0.12,
  "model_version": "pellav2-quantized-int8",
  "latency_ms": 32.4
}
```
*Note for Varun & Varshu: Class label format and score polarity (whether 1 = Fake or 1 = Genuine) must be verified and documented in `models/artifact_manifest.json` before enabling calibrated fusion.*

---

## 3. Multilingual Transcription Service Contract

**Assigned Engineer:** Pallavi  
**Base URL:** `http://transcription-service:8102`

### 3.1 `GET /health`
- **Response (200 OK):**
```json
{
  "status": "ok",
  "service": "transcription-service",
  "model_version": "whisper-small-indic-v1",
  "is_mock": false,
  "artifact_found": true
}
```

### 3.2 `POST /transcribe`
- **Request:** `multipart/form-data` with `file: UploadFile`.
- **Success Response (200 OK):**
```json
{
  "status": "success",
  "text": "Hello, this is an urgent security verification from your bank.",
  "language": "en",
  "model_version": "whisper-small-indic-v1",
  "latency_ms": 115.0
}
```
*Note for Pallavi: Language code should follow ISO 639-1 (e.g. `en`, `te`, `ta`, `kn`, `ml`).*

---

## 4. Hosted AskDrip LLM Risk Assessment Contract (RIAS Stage 2)

**Assigned Engineer:** Sainadh  
**Endpoint:** Configured via `CFIC_ASKDRIP_LLM_BASE_URL`

- **Headers:** `Authorization: Bearer <CFIC_ASKDRIP_LLM_API_KEY>`
- **Strict Response Schema (JSON):**
```json
{
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "reason": "Brief summary of conversational intent (max 25 words)"
}
```
- **Categorical Risk Semantics:**
  - `LOW`: Standard personal, commercial, or service call. No extortion or deception.
  - `MEDIUM`: Pushy, unverified request for callback, unconfirmed account updates.
  - `HIGH`: Direct threats, emergency impersonation, urgent OTP/password/wire requests.
- **Safety Guarantee:** Malformed or failed LLM responses result in `status="error"` and `risk_level=None`. The system **never** assumes `LOW` upon failure.

---

## 5. TCED Decision Contract

| PellaV2 Status | RIAS Status | RIAS Risk Level | Final Outcome | Reason Code |
| :--- | :--- | :--- | :--- | :--- |
| Any | `success` | `HIGH` | **`SUSPICIOUS`** | `HIGH_RIAS_OVERRIDE` |
| `error` / `timeout` | `error` / `timeout` | Any | **`INCONCLUSIVE`** | `INSUFFICIENT_EVIDENCE` |
| `success` | `error` / `skipped` | Any | **`INCONCLUSIVE`** | `PARTIAL_EVIDENCE_POLICY_TBD` |
| `error` | `success` | `LOW` / `MEDIUM` | **`INCONCLUSIVE`** | `PARTIAL_EVIDENCE_POLICY_TBD` |
| `success` | `success` | Unknown string | **`INCONCLUSIVE`** | `INVALID_RIAS_RISK_LEVEL` |
| `success` | `success` | `LOW` / `MEDIUM` | **`INCONCLUSIVE`** | `TCED_CALIBRATION_TBD` |
