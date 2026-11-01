from fastapi import FastAPI
from app.api.routes import router
app=FastAPI(title="CFIC × VoiceShield HackVersion", version="0.1.0")
app.include_router(router, prefix="/v1")
@app.get("/health")
async def health(): return {"status":"ok","service":"cfic-api"}
