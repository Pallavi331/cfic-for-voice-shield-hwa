from app.schemas import FinalOutcome
from app.tced.policy import decide
def test_high_rias_always_suspicious():
    assert decide({"status":"success","prediction":"GENUINE"},{"status":"success","risk_level":"HIGH"}) == (FinalOutcome.SUSPICIOUS,"HIGH_RIAS_OVERRIDE")
def test_both_failed_inconclusive():
    assert decide({"status":"error"},{"status":"error"}) == (FinalOutcome.INCONCLUSIVE,"INSUFFICIENT_EVIDENCE")
def test_unvalidated_fusion_is_inconclusive():
    assert decide({"status":"success","prediction":"native"},{"status":"success","risk_level":"LOW"})[0] == FinalOutcome.INCONCLUSIVE
