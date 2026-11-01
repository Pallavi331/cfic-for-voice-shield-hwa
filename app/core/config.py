from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "CFIC VoiceShield HackVersion"
    environment: str = "development"
    api_key: str = "replace-me-for-local-testing"
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60
    pella_base_url: str = "http://localhost:8101"
    transcription_base_url: str = "http://localhost:8102"
    askdrip_llm_base_url: str = ""
    askdrip_llm_api_key: str = ""
    request_timeout_seconds: float = 30.0
    model_config = SettingsConfigDict(env_prefix="CFIC_", extra="ignore")
settings = Settings()
