from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from app.core.config import settings
from app.orchestration.service import analyze_audio
router=APIRouter()
async def require_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != settings.api_key: raise HTTPException(status_code=401, detail="Invalid API key")
@router.post("/analyze")
async def analyze(file: UploadFile=File(...), _: None=Depends(require_api_key)):
    content=await file.read()
    if not content: raise HTTPException(status_code=400, detail="Empty audio payload")
    if len(content)>25*1024*1024: raise HTTPException(status_code=413, detail="Audio exceeds 25 MiB scaffold limit")
    result=await analyze_audio(content, file.filename or "audio", file.content_type or "application/octet-stream")
    return result.model_dump(mode="json")
