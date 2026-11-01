"""Orchestration service coordinating PellaV2, Transcription, and RIAS."""

import asyncio
import time
import uuid
from typing import Any
from app.schemas import AnalysisResponse, RiskLevel
from app.tced.policy import decide
from services.pella.client import PellaClient
from services.rias.assessor import assess_transcript
from services.transcription.client import TranscriptionClient


class PipelineOrchestrator:
    """Orchestrates concurrent execution of audio deepfake detection and semantic risk analysis."""

    def __init__(
        self,
        pella_client: PellaClient | None = None,
        transcription_client: TranscriptionClient | None = None,
    ):
        self.pella_client = pella_client or PellaClient()
        self.transcription_client = transcription_client or TranscriptionClient()

    async def analyze_audio(
        self,
        audio: bytes,
        filename: str = "audio.wav",
        content_type: str = "audio/wav",
        request_id: str | None = None,
    ) -> AnalysisResponse:
        """Run audio analysis pipeline."""
        req_id = request_id or str(uuid.uuid4())
        pipeline_start = time.perf_counter()
        latencies: dict[str, float] = {}

        # Stage 1: Parallel dispatch of PellaV2 detector and Transcription
        pella_task = asyncio.create_task(
            self.pella_client.predict(audio, filename, content_type)
        )
        transcription_task = asyncio.create_task(
            self.transcription_client.transcribe(audio, filename, content_type)
        )

        pella_res_raw, transc_res_raw = await asyncio.gather(
            pella_task, transcription_task, return_exceptions=True
        )

        # Normalize PellaV2 outcome
        if isinstance(pella_res_raw, Exception):
            pella_res: dict[str, Any] = {
                "status": "error",
                "prediction": None,
                "score": None,
                "model_version": None,
                "error": str(pella_res_raw),
                "latency_ms": 0.0,
            }
        else:
            pella_res = pella_res_raw

        latencies["pella"] = pella_res.get("latency_ms", 0.0)

        # Normalize Transcription outcome
        if isinstance(transc_res_raw, Exception):
            transc_res: dict[str, Any] = {
                "status": "error",
                "text": None,
                "language": None,
                "model_version": None,
                "error": str(transc_res_raw),
                "latency_ms": 0.0,
            }
        else:
            transc_res = transc_res_raw

        latencies["transcription"] = transc_res.get("latency_ms", 0.0)

        # Stage 2: RIAS Risk Assessment (triggered if transcription produced text)
        rias_res: dict[str, Any] = {
            "status": "skipped",
            "risk_level": None,
            "reason": "Transcription was unsuccessful or produced no text",
            "latency_ms": 0.0,
        }

        if transc_res.get("status") == "success" and transc_res.get("text"):
            transcript_text = transc_res["text"]
            try:
                rias_res = await assess_transcript(transcript_text)
            except Exception as exc:
                rias_res = {
                    "status": "error",
                    "risk_level": None,
                    "reason": None,
                    "error": f"LLM assessment failed: {type(exc).__name__}",
                    "latency_ms": 0.0,
                }

        latencies["rias_llm"] = rias_res.get("latency_ms", 0.0)

        # Stage 3: TCED Decision
        outcome, reason = decide(pella_res, rias_res)

        total_latency = round((time.perf_counter() - pipeline_start) * 1000, 2)
        latencies["total"] = total_latency

        risk_level_enum = None
        if rias_res.get("risk_level"):
            try:
                risk_level_enum = RiskLevel(rias_res["risk_level"])
            except ValueError:
                risk_level_enum = None

        return AnalysisResponse(
            request_id=req_id,
            final_outcome=outcome,
            reason_code=reason,
            pella_status=pella_res.get("status", "error"),
            rias_transcription_status=transc_res.get("status", "error"),
            rias_risk_status=rias_res.get("status", "error"),
            rias_risk_level=risk_level_enum,
            model_version=pella_res.get("model_version"),
            latency_ms=latencies,
        )


# Global default instance
orchestrator = PipelineOrchestrator()


async def analyze_audio(
    audio: bytes,
    filename: str = "audio.wav",
    content_type: str = "audio/wav",
    request_id: str | None = None,
) -> AnalysisResponse:
    """Convenience functional interface."""
    return await orchestrator.analyze_audio(
        audio, filename=filename, content_type=content_type, request_id=request_id
    )
