class PellaClient:
    async def predict(self, audio: bytes, filename: str, content_type: str) -> dict:
        return {"status":"error","prediction":None,"score":None,"model_version":None,"error":"not_configured"}
