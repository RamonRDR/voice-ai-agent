"""Validated, size-capped upload conversion to PCM 16-bit mono WAV."""

import array
import io
import math
import wave
from pathlib import Path

from fastapi import UploadFile

from .config import Settings
from .errors import VoiceError
from .providers import run_command


def detect_type(data: bytes) -> str:
    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return "wav"
    if data[:4] == b"OggS":
        return "ogg"
    if data[:4] == b"\x1a\x45\xdf\xa3":
        return "webm"
    if data[:3] == b"ID3" or (len(data) >= 2 and data[0] == 0xFF and data[1] & 0xE0 == 0xE0):
        return "mp3"
    if data[4:8] == b"ftyp":
        return "m4a"
    raise VoiceError("Unsupported audio format: WAV, WebM, OGG, MP3 or M4A required")


def verify_wav(data: bytes, max_seconds: int) -> None:
    try:
        with wave.open(io.BytesIO(data), "rb") as wav:
            channels, rate, width = wav.getnchannels(), wav.getframerate(), wav.getsampwidth()
            count = wav.getnframes()
            if rate != 16000 or channels != 1 or width != 2:
                raise VoiceError("Audio conversion did not produce 16 kHz mono PCM16")
            duration = count / rate
            if duration < 0.1 or duration > max_seconds:
                raise VoiceError("Audio duration is outside configured limits")
            frames = wav.readframes(count)
            samples = array.array("h")
            samples.frombytes(frames)
            if not samples:
                raise VoiceError("Audio is empty")
            stride = max(1, len(samples) // 100_000)
            sampled = samples[::stride]
            rms = math.sqrt(sum(s * s for s in sampled) / len(sampled))
            if rms < 40:
                raise VoiceError("Audio is silent or too quiet")
    except (wave.Error, EOFError, ValueError, ZeroDivisionError) as exc:
        raise VoiceError("Corrupted or malformed WAV audio") from exc


async def prepare_audio(upload: UploadFile, settings: Settings, directory: Path) -> Path:
    data = await upload.read(settings.max_upload_bytes + 1)
    if not data:
        raise VoiceError("Empty audio upload")
    if len(data) > settings.max_upload_bytes:
        raise VoiceError("Audio file exceeds size limit", 413)
    kind = detect_type(data)
    source = directory / ("input." + kind)
    target = directory / "normalized.wav"
    source.write_bytes(data)
    if kind == "wav":
        try:
            with wave.open(io.BytesIO(data), "rb") as w:
                already_normalized = (
                    w.getnchannels() == 1
                    and w.getframerate() == 16000
                    and w.getsampwidth() == 2
                    and w.getcomptype() == "NONE"
                )
        except (wave.Error, EOFError) as exc:
            raise VoiceError("Malformed WAV header") from exc
        if already_normalized:
            verify_wav(data, settings.max_audio_seconds)
            target.write_bytes(data)
            return target
    try:
        await run_command(
            [
                settings.ffmpeg_executable, "-hide_banner", "-loglevel", "error",
                "-nostdin", "-y", "-i", str(source), "-vn", "-ac", "1",
                "-ar", "16000", "-acodec", "pcm_s16le", "-f", "wav", str(target),
            ],
            min(settings.process_timeout_seconds, 30),
        )
    except (FileNotFoundError, OSError, TimeoutError) as exc:
        raise VoiceError("ffmpeg missing or audio processing timed out", 503) from exc
    except VoiceError as exc:
        raise VoiceError("Audio decoding failed or file is corrupted") from exc
    if target.stat().st_size > (settings.max_audio_seconds + 2) * 32_000:
        raise VoiceError("Decoded audio exceeds duration limits")
    verify_wav(target.read_bytes(), settings.max_audio_seconds)
    return target
