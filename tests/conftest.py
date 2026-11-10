"""Small synthetic PCM waves. No recordings from real people."""

import io
import math
import struct
import wave

import pytest
from fastapi.testclient import TestClient

from voice_ai_agent.config import Settings
from voice_ai_agent.main import create_app


def make_wav(
    seconds: float = 0.3,
    sample_rate: int = 16000,
    silence: bool = False,
) -> bytes:
    frames = int(seconds * sample_rate)
    samples = [
        0 if silence else int(2600 * math.sin(2 * math.pi * 440 * n / sample_rate))
        for n in range(frames)
    ]
    out = io.BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(struct.pack("<" + "h" * len(samples), *samples))
    return out.getvalue()


@pytest.fixture
def client() -> TestClient:
    app = create_app(Settings(_env_file=None))
    with TestClient(app) as test_client:
        yield test_client
