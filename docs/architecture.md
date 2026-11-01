# CFIC Architecture

See the authoritative architecture specification in [ARCHITECTURE.md](file:///C:/MyProjects/CFIC-VoiceShield-HackVersion/docs/ARCHITECTURE.md).

### Summary Flow
VoiceShield → CFIC API (auth / validation / rate limiting) → Parallel Execution:
1. PellaV2 Deepfake Detector (`POST /predict`)
2. Speech-to-Text Transcription (`POST /transcribe`) → Hosted AskDrip LLM Risk Assessment (RIAS)

Combined at TCED (Temporal and Contextual Evidence Decision) → Normalized Final Outcome (`GENUINE`, `FAKE`, `SUSPICIOUS`, `INCONCLUSIVE`).

**Locked Safety Rule:**
RIAS `HIGH` always forces `SUSPICIOUS` regardless of PellaV2 detector output.
