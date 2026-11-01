"""Pydantic schemas for the CFIC API."""

from enum import Enum
from pydantic import BaseModel, Field


class FinalOutcome(str, Enum):
    """Normalized final decision from TCED."""

    GENUINE = "GENUINE"
    FAKE = "FAKE"
    SUSPICIOUS = "SUSPICIOUS"
    INCONCLUSIVE = "INCONCLUSIVE"


class RiskLevel(str, Enum):
    """Categorical risk assessment from AskDrip LLM (RIAS)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ComponentStatus(str, Enum):
    """Status of downstream analysis components."""

    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    NOT_CONFIGURED = "not_configured"


class AnalysisResponse(BaseModel):
    """Normalized analysis response from CFIC."""

    request_id: str = Field(..., description="Unique request identifier for tracing")
    final_outcome: FinalOutcome = Field(
        ..., description="Final combined outcome from TCED"
    )
    reason_code: str = Field(..., description="Machine-readable decision rationale")
    pella_status: str = Field(..., description="Status of PellaV2 deepfake detector")
    rias_transcription_status: str = Field(
        ..., description="Status of transcription stage"
    )
    rias_risk_status: str = Field(
        ..., description="Status of hosted AskDrip LLM risk assessment"
    )
    rias_risk_level: RiskLevel | None = Field(
        default=None, description="Assessed semantic risk level (LOW/MEDIUM/HIGH)"
    )
    model_version: str | None = Field(
        default=None, description="Detector / pipeline model version if available"
    )
    latency_ms: dict[str, float] = Field(
        default_factory=dict,
        description="Latency breakdown in milliseconds (total, pella, transcription, rias_llm)",
    )


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(default="ok")
    service: str = Field(default="cfic-api")
    version: str = Field(default="0.1.0")
    environment: str = Field(...)
    downstream_status: dict[str, str] = Field(default_factory=dict)
