class TranscriptionClient:
    async def transcribe(self, audio: bytes, filename: str, content_type: str) -> dict:
        return {"status":"error","text":None,"language":None,"error":"not_configured"}
