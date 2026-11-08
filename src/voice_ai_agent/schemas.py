"""Public contracts; fields intentionally avoid leaking audio or provider secrets."""

from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=2000)


class Transcription(BaseModel):
    text: str
    language: str | None = None
    source: Literal["scripted", "whisper_cpp"]
    simulated: bool


class ToolExecution(BaseModel):
    name: str
    ok: bool
    result: dict[str, object] = Field(default_factory=dict)


class Metrics(BaseModel):
    stt_ms: int = 0
    llm_ms: int = 0
    tools_ms: int = 0
    tts_ms: int = 0
    total_ms: int = 0


class TurnResponse(BaseModel):
    session_id: str
    request_id: str
    transcript: Transcription
    response: str
    tool: ToolExecution | None = None
    audio_base64: str | None = None
    audio_mime: str | None = None
    tts_source: Literal["espeak", "browser"] = "browser"
    tts_error: str | None = None
    metrics: Metrics


class TextTurnRequest(BaseModel):
    session_id: str | None = Field(default=None, max_length=80)
    request_id: str | None = Field(default=None, max_length=80)
    text: str = Field(min_length=1, max_length=1000)
    language: Literal["en", "pt", "es"] = "en"


class RuntimeInfo(BaseModel):
    mode: str
    stt: str
    llm: str
    tts: str
    microphone_is_recognized: bool
    disclaimer: str


class PublicError(BaseModel):
    detail: str
