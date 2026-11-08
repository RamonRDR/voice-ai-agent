"""Fault-injection tests for stage-level failures without external services."""

from io import BytesIO
from pathlib import Path

import pytest
from conftest import make_wav
from fastapi import UploadFile
from voice_ai_agent.config import Settings
from voice_ai_agent.errors import VoiceError
from voice_ai_agent.pipeline import VoicePipeline
from voice_ai_agent.providers import WhisperCppSTT


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
