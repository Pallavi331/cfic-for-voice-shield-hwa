import asyncio, time, uuid
from app.schemas import AnalysisResponse
from app.tced.policy import decide
from services.pella.client import PellaClient
from services.transcription.client import TranscriptionClient
from services.rias.assessor import assess_transcript
pella_client=PellaClient(); transcription_client=TranscriptionClient()
async def analyze_audio(audio: bytes, filename: str, content_type: str) -> AnalysisResponse:
    rid=str(uuid.uuid4()); started=time.perf_counter()
    ptask=asyncio.create_task(pella_client.predict(audio, filename, content_type))
    ttask=asyncio.create_task(transcription_client.transcribe(audio, filename, content_type))
    p,t=await asyncio.gather(ptask, ttask, return_exceptions=True)
    p={"status":"error"} if isinstance(p,Exception) else p
    t={"status":"error"} if isinstance(t,Exception) else t
    r={"status":"error","risk_level":None}
    if t.get("status")=="success" and t.get("text"):
        try: r=await assess_transcript(t["text"])
        except Exception: pass
    outcome,reason=decide(p,r)
    return AnalysisResponse(request_id=rid, final_outcome=outcome, reason_code=reason,
        pella_status=p.get("status","error"), rias_transcription_status=t.get("status","error"),
        rias_risk_status=r.get("status","error"), rias_risk_level=r.get("risk_level"),
        model_version=p.get("model_version"), latency_ms={"total":round((time.perf_counter()-started)*1000,2)})
