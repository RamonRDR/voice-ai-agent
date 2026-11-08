"""Environment-only provider configuration; no paid provider is active by default."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, HttpUrl, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VOICE_", env_file=".env", extra="ignore")

    mode: Literal["demo", "local", "remote"] = "demo"
    stt_backend: Literal["demo", "whisper_cpp"] = "demo"
    tts_backend: Literal["browser", "espeak"] = "browser"
    llm_backend: Literal["rules", "openai_compatible"] = "rules"
    llm_endpoint: HttpUrl | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None
    whisper_executable: str = "whisper-cli"
    whisper_model: str | None = None
    espeak_executable: str = "espeak-ng"
    ffmpeg_executable: str = "ffmpeg"
    ffprobe_executable: str = "ffprobe"
    max_upload_bytes: int = Field(default=8 * 1024 * 1024, ge=1024, le=50 * 1024 * 1024)
    max_audio_seconds: int = Field(default=30, ge=1, le=180)
    process_timeout_seconds: int = Field(default=90, ge=5, le=300)
    max_history: int = Field(default=12, ge=2, le=40)
    session_ttl_seconds: int = Field(default=1800, ge=60, le=86400)
    timezone: str = "UTC"
    cors_origins: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_providers(self) -> "Settings":
        if self.mode == "demo":
            if self.stt_backend != "demo" or self.llm_backend != "rules":
                raise ValueError("Demo mode requires scripted STT and rules LLM")
        else:
            if self.stt_backend != "whisper_cpp":
                raise ValueError("Real mode requires whisper_cpp STT")
            if not self.whisper_model:
                raise ValueError("A local Whisper model path is required")
        if self.llm_backend == "openai_compatible":
            if self.mode != "remote" or not all(
                [self.llm_endpoint, self.llm_api_key, self.llm_model]
            ):
                raise ValueError("External LLM needs remote mode, HTTPS endpoint, key and model")
            if self.llm_endpoint and self.llm_endpoint.scheme != "https":
                raise ValueError("External LLM endpoint must use HTTPS")
        if self.mode == "remote" and self.llm_backend != "openai_compatible":
            raise ValueError("Remote mode requires an explicitly configured LLM")
        for origin in self.cors_origins:
            if not origin.startswith(("http://localhost:", "http://127.0.0.1:", "https://")):
                raise ValueError("CORS origins must use HTTPS or loopback")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
