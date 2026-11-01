"""API routes for CFIC."""

import uuid
from fastapi import APIRouter, Depends, File, Header, Request, UploadFile
from app.core.config import settings
from app.core.errors import (
    AudioPayloadTooLargeException,
    EmptyAudioPayloadException,
    RateLimitExceededException,
    UnauthorizedException,
)
from app.core.rate_limiter import InMemoryRateLimiter
from app.orchestration.service import analyze_audio
from app.schemas import AnalysisResponse, HealthResponse

router = APIRouter()

# Process-local rate limiter instance
rate_limiter = InMemoryRateLimiter(
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)


def get_request_id(request: Request) -> str:
    """Retrieve existing X-Request-ID header or generate a new UUID."""
    req_id = request.headers.get("X-Request-ID")
    if not req_id:
        req_id = str(uuid.uuid4())
    return req_id


async def verify_api_key_and_rate_limit(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """Validate API key authentication and enforce rate limits."""
    # 1. API Key Authentication
    if not x_api_key or x_api_key != settings.api_key:
        raise UnauthorizedException("Missing or invalid API key provided in X-API-Key header")

    # 2. Rate Limiting Key: Use client IP combined with API key hash
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{x_api_key[-6:]}"

    allowed, remaining, retry_after = rate_limiter.check(rate_key)
    if not allowed:
        raise RateLimitExceededException(retry_after=retry_after)


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def router_health() -> HealthResponse:
    """Health status and downstream dependency configuration."""
    return HealthResponse(
        status="ok",
        service="cfic-api",
        version="0.1.0",
        environment=settings.environment,
        downstream_status={
            "pella_url_configured": str(bool(settings.pella_base_url)),
            "transcription_url_configured": str(bool(settings.transcription_base_url)),
            "askdrip_llm_configured": str(
                bool(settings.askdrip_llm_base_url and settings.askdrip_llm_api_key)
            ),
        },
    )


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    tags=["Analysis"],
    summary="Analyze audio sample for synthetic speech and conversational risk",
)
async def analyze(
    request: Request,
    file: UploadFile = File(..., description="Audio file payload (WAV/MP3/FLAC/OGG)"),
    _: None = Depends(verify_api_key_and_rate_limit),
) -> AnalysisResponse:
    """Accept an audio recording from VoiceShield, dispatch downstream analysis, and return TCED outcome."""
    req_id = get_request_id(request)

    # Read audio bytes
    content = await file.read()

    # Request Validation: empty payload
    if not content:
        raise EmptyAudioPayloadException("Received empty audio payload (0 bytes)")

    # Request Validation: size limit
    if len(content) > settings.max_audio_bytes:
        raise AudioPayloadTooLargeException(
            max_bytes=settings.max_audio_bytes, actual_bytes=len(content)
        )

    filename = file.filename or "audio.wav"
    content_type = file.content_type or "audio/wav"

    response = await analyze_audio(
        audio=content,
        filename=filename,
        content_type=content_type,
        request_id=req_id,
    )

    return response
