"""Fault-injection tests for stage-level failures without external services."""

from io import BytesIO
from pathlib import Path

import httpx

import pytest
from conftest import make_wav
from fastapi import UploadFile

from voice_ai_agent.config import Settings
from voice_ai_agent.errors import VoiceError
from voice_ai_agent.pipeline import VoicePipeline
from voice_ai_agent.providers import OpenAICompatibleLLM, RulesLLM, WhisperCppSTT


async def test_stt_failure_is_propagated_and_cleans_state() -> None:
    pipeline = VoicePipeline(Settings(_env_file=None))

    class BrokenSTT:
        async def transcribe(self, wav_path: Path, language: str) -> None:
            raise VoiceError("STT failure", 502)

    pipeline.stt = BrokenSTT()
    upload = UploadFile(file=BytesIO(make_wav()), filename="synthetic.wav")
    with pytest.raises(VoiceError, match="STT failure"):
        await pipeline.process(None, None, "en", audio=upload)
    assert not pipeline.running
    assert not pipeline.busy_sessions


async def test_tts_failure_preserves_text_response() -> None:
    pipeline = VoicePipeline(Settings(_env_file=None))

    class BrokenTTS:
        async def synthesize(self, text: str, language: str) -> bytes:
            raise VoiceError("TTS failure", 502)

    pipeline.tts = BrokenTTS()
    response = await pipeline.process(None, None, "en", text="hello")
    assert "Hello!" in response.response
    assert response.tts_error is not None
    assert response.audio_base64 is None
    assert response.tts_source == "browser"


async def test_local_whisper_missing_executable_gives_safe_error(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        mode="local",
        stt_backend="whisper_cpp",
        whisper_model=str(tmp_path / "model.bin"),
        whisper_executable=str(tmp_path / "missing-cli"),
    )
    adapter = WhisperCppSTT(settings)
    with pytest.raises(VoiceError, match="Whisper is unavailable"):
        await adapter.transcribe(tmp_path / "synthetic.wav", "en")


@pytest.mark.parametrize(
    ("command", "note"),
    [
        ("note: ask what time the train arrives", "ask what time the train arrives"),
        ("anote: que horas é o encontro", "que horas é o encontro"),
        ("apunta: qué hora llega el autobús", "qué hora llega el autobús"),
    ],
)
async def test_explicit_note_command_takes_precedence(command: str, note: str) -> None:
    result = await RulesLLM().respond(command, [])
    assert result.tool_name == "create_note"
    assert result.tool_args == {"text": note}


@pytest.mark.parametrize(
    "payload",
    [
        {"choices": [{"message": None}]},
        {"choices": [{"message": {"tool_calls": [{"function": None}]}}]},
        {"choices": [{"message": {"tool_calls": [{"function": []}]}}]},
        {"choices": [{"message": {"tool_calls": "not-a-list"}}]},
        {"choices": [{"message": {"tool_calls": [None]}}]},
        {"choices": [{"message": {"content": []}}]},
        {"choices": "not-a-list"},
        {},
    ],
)
async def test_remote_llm_rejects_malformed_provider_json(monkeypatch, payload: object) -> None:
    original_client = httpx.AsyncClient

    def mock_client(**kwargs):
        def handle(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=payload)

        return original_client(transport=httpx.MockTransport(handle), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", mock_client)
    settings = Settings(
        _env_file=None,
        mode="remote",
        stt_backend="whisper_cpp",
        whisper_model="test-model.bin",
        llm_backend="openai_compatible",
        llm_endpoint="https://example.org/chat/completions",
        llm_api_key="test-only-key",
        llm_model="test-model",
    )
    with pytest.raises(VoiceError, match="invalid data") as exc:
        await OpenAICompatibleLLM(settings).respond("hello", [])
    assert exc.value.status_code == 502


async def test_remote_llm_accepts_valid_tool_call(monkeypatch) -> None:
    original_client = httpx.AsyncClient

    def mock_client(**kwargs):
        def handle(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {"message": {"tool_calls": [{"function": {
                            "name": "calculate", "arguments": '{"expression":"2+2"}'
                        }}]}}
                    ]
                },
            )

        return original_client(transport=httpx.MockTransport(handle), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", mock_client)
    settings = Settings(
        _env_file=None,
        mode="remote",
        stt_backend="whisper_cpp",
        whisper_model="test-model.bin",
        llm_backend="openai_compatible",
        llm_endpoint="https://example.org/chat/completions",
        llm_api_key="test-only-key",
        llm_model="test-model",
    )
    result = await OpenAICompatibleLLM(settings).respond("calculate 2+2", [])
    assert result.tool_name == "calculate"
    assert result.tool_args == {"expression": "2+2"}
