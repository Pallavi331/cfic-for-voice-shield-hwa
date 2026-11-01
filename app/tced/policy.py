from app.schemas import FinalOutcome, RiskLevel
def decide(pella: dict, rias: dict) -> tuple[FinalOutcome,str]:
    if rias.get("status")=="success" and rias.get("risk_level")==RiskLevel.HIGH.value:
        return FinalOutcome.SUSPICIOUS,"HIGH_RIAS_OVERRIDE"
    pok=pella.get("status")=="success" and pella.get("prediction") is not None
    rok=rias.get("status")=="success" and rias.get("risk_level") in {RiskLevel.LOW.value,RiskLevel.MEDIUM.value}
    if not pok and not rok: return FinalOutcome.INCONCLUSIVE,"INSUFFICIENT_EVIDENCE"
    if not pok or not rok: return FinalOutcome.INCONCLUSIVE,"PARTIAL_EVIDENCE_POLICY_TBD"
    return FinalOutcome.INCONCLUSIVE,"TCED_CALIBRATION_TBD"
