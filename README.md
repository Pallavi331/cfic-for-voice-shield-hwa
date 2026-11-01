# CFIC × VoiceShield HackVersion
Four-person contribution scaffold for Team SAIL.

Architecture: VoiceShield → CFIC API → PellaV2 detector and RIAS transcription in parallel → existing hosted AskDrip LLM risk assessment → TCED → normalized result.

Final outcomes: GENUINE, FAKE, SUSPICIOUS, INCONCLUSIVE.
Locked rule: RIAS HIGH always yields SUSPICIOUS.

Excluded: LID, LACR, seven language-cluster detectors, DSR, and a separate XLS-R service if the confirmed PellaV2 artifact already embeds XLS-R.

This scaffold uses mock adapters and does not contain model weights. It must not be treated as a validated deepfake detector.

## Run locally
Python 3.11+
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

## Contribution branches
- contrib/project-lead-cfic
- contrib/varun-pellav2-quantization
- contrib/varshu-pellav2-docker
- contrib/pallavi-transcription-docker

Push each branch to your remote and open one PR per contributor. See docs/contribution-workflow.md.
