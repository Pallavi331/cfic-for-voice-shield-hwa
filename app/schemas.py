from enum import Enum
from pydantic import BaseModel, Field
class FinalOutcome(str, Enum):
    GENUINE="GENUINE"; FAKE="FAKE"; SUSPICIOUS="SUSPICIOUS"; INCONCLUSIVE="INCONCLUSIVE"
class RiskLevel(str, Enum):
    LOW="LOW"; MEDIUM="MEDIUM"; HIGH="HIGH"
class AnalysisResponse(BaseModel):
    request_id: str
    final_outcome: FinalOutcome
    reason_code: str
    pella_status: str
    rias_transcription_status: str
    rias_risk_status: str
    rias_risk_level: RiskLevel | None = None
    model_version: str | None = None
    latency_ms: dict[str, float] = Field(default_factory=dict)
