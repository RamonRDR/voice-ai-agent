"""Provider adapters. Scripted demo components are never presented as real AI."""

import asyncio
import json
import re
import tempfile
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Protocol

import httpx

from .config import Settings
from .errors import VoiceError
from .schemas import Message, Transcription
from .tools import TOOL_SPECS

SYSTEM_PROMPT = (
    files("voice_ai_agent").joinpath("prompts/system_v1.txt").read_text(encoding="utf-8")
)


@dataclass
class ModelOutput:
    content: str | None = None
    tool_name: str | None = None
    tool_args: dict[str, object] | None = None


class SpeechToText(Protocol):
    async def transcribe(self, wav_path: Path, language: str) -> Transcription: ...


class LanguageModel(Protocol):
    async def respond(self, text: str, history: list[Message]) -> ModelOutput: ...


class TextToSpeech(Protocol):
    async def synthesize(self, text: str, language: str) -> bytes | None: ...


async def run_command(
    args: list[str], timeout: int, input_bytes: bytes | None = None
) -> tuple[bytes, bytes]:
    process = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE if input_bytes is not None else asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        output, error = await asyncio.wait_for(process.communicate(input_bytes), timeout=timeout)
    except (TimeoutError, asyncio.CancelledError):
        if process.returncode is None:
            process.kill()
            await process.communicate()
        raise
    if process.returncode != 0:
        raise VoiceError("Local audio engine failed", status_code=502)
    return output, error


class ScriptedSTT:
    """Fixture-like STT: never decodes speech. Explicitly marked simulated."""

    async def transcribe(self, wav_path: Path, language: str) -> Transcription:
        return Transcription(
            text={"pt": "Que horas são?", "es": "¿Qué hora es?"}.get(language, "What time is it?"),
            language=language,
            source="scripted",
            simulated=True,
        )


class WhisperCppSTT:
    """Local whisper.cpp CLI: models are provisioned out of band, not in CI."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def transcribe(self, wav_path: Path, language: str) -> Transcription:
        if not self.settings.whisper_model:
            raise VoiceError("Whisper model path not configured", status_code=503)
        with tempfile.TemporaryDirectory(prefix="voice-stt-") as directory:
            prefix = Path(directory) / "transcript"
            args = [
                self.settings.whisper_executable,
                "-m",
                self.settings.whisper_model,
                "-f",
                str(wav_path),
                "-l",
                language,
                "-nt",
                "-np",
                "-otxt",
                "-of",
                str(prefix),
            ]
            try:
                await run_command(args, timeout=self.settings.process_timeout_seconds)
                transcript = prefix.with_suffix(".txt").read_text(encoding="utf-8").strip()
            except (FileNotFoundError, OSError) as exc:
                raise VoiceError("Whisper is unavailable", status_code=503) from exc
            if not transcript:
                raise VoiceError("No recognizable speech", status_code=422)
            return Transcription(
                text=transcript[:2000], language=language, source="whisper_cpp", simulated=False
            )


class RulesLLM:
    """Deterministic scripted routing for free demos, not a generative LLM."""

    async def respond(self, text: str, history: list[Message]) -> ModelOutput:
        message = text.strip()
        lower = message.casefold()
        # An explicit command must take precedence over words inside its payload.
        note = re.match(r"^(?:note|save note|anote|anotar|nota|apunta)\s*:\s*(.+)$", message, re.I)
        if note:
            return ModelOutput(tool_name="create_note", tool_args={"text": note.group(1)[:250]})
        if any(w in lower for w in ("what time", "current time", "que horas", "qué hora")):
            return ModelOutput(tool_name="get_current_time", tool_args={})
        if any(w in lower for w in ("list notes", "show notes", "listar notas", "ver notas")):
            return ModelOutput(tool_name="list_notes", tool_args={})
        if any(w in lower for w in ("session summary", "resumo da sessão", "resumen")):
            return ModelOutput(tool_name="get_session_summary", tool_args={})
        calc = re.match(
            r"^(?:calculate|calc|quanto é|calcule|cuánto es)\s*:?\s*([0-9+\-*/().\s]+)\??$",
            message,
            re.I,
        )
        if calc:
            return ModelOutput(tool_name="calculate", tool_args={"expression": calc.group(1)})
        if any(w in lower for w in ("hello", "hi", "olá", "oi", "hola")):
            return ModelOutput(
                content="Olá! Posso consultar a hora, calcular ou guardar notas."
                if ("olá" in lower or "oi" in lower)
                else "Hello! I can check the time, calculate, and save notes."
            )
        return ModelOutput(
            content="Scripted demo: try 'What time is it?', 'calculate 2+2', "
            "'note: buy milk' or 'list notes'. This is not a generated LLM reply."
        )


class OpenAICompatibleLLM:
    """Opt-in remote chat-completion provider. No outgoing calls in demo mode."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def respond(self, text: str, history: list[Message]) -> ModelOutput:
        s = self.settings
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(m.model_dump() for m in history[-s.max_history :])
        messages.append({"role": "user", "content": text[:1000]})
        try:
            async with httpx.AsyncClient(timeout=min(s.process_timeout_seconds, 45)) as client:
                response = await client.post(
                    str(s.llm_endpoint),
                    headers={"Authorization": f"Bearer {s.llm_api_key}"},
                    json={
                        "model": s.llm_model,
                        "messages": messages,
                        "tools": TOOL_SPECS,
                        "tool_choice": "auto",
                        "max_tokens": 250,
                    },
                )
                response.raise_for_status()
                data = response.json()
            # Provider JSON is untrusted; validate nested shapes before accessing fields.
            if not isinstance(data, dict):
                raise ValueError("Invalid provider response")
            choices = data.get("choices")
            if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
                raise ValueError("Invalid provider choices")
            msg = choices[0].get("message")
            if not isinstance(msg, dict):
                raise ValueError("Invalid provider message")
            calls = msg.get("tool_calls")
            if calls is not None and not isinstance(calls, list):
                raise ValueError("Invalid tool calls")
            if calls:
                # One allowlisted tool call at most. Never execute arbitrary names or code.
                call = calls[0]
                if not isinstance(call, dict):
                    raise ValueError("Invalid tool call")
                fn = call.get("function")
                if not isinstance(fn, dict):
                    raise ValueError("Invalid function call")
                name = fn.get("name")
                raw_args = fn.get("arguments") or "{}"
                if not isinstance(name, str) or not name.strip() or not isinstance(raw_args, str):
                    raise ValueError("Invalid function name or arguments")
                args = json.loads(raw_args)
                if not isinstance(args, dict):
                    raise ValueError("Arguments must be an object")
                return ModelOutput(tool_name=name, tool_args=args)
            content = msg.get("content")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Empty LLM response")
            return ModelOutput(content=content[:1000])
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise VoiceError("LLM provider unavailable or returned invalid data", 502) from exc


class BrowserTTS:
    """No server audio. UI exposes optional real browser speechSynthesis on click."""

    async def synthesize(self, text: str, language: str) -> bytes | None:
        return None


class EspeakTTS:
    """Local actual WAV synthesis, no cloned voices or paid services."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def synthesize(self, text: str, language: str) -> bytes:
        if not text or len(text) > 1000:
            raise VoiceError("Invalid TTS text")
        voice = {"pt": "pt-br", "en": "en-us", "es": "es"}.get(language, "en-us")
        try:
            output, _ = await run_command(
                [self.settings.espeak_executable, "--stdin", "--stdout", "-v", voice],
                timeout=min(self.settings.process_timeout_seconds, 25),
                input_bytes=text.encode("utf-8"),
            )
        except (FileNotFoundError, OSError, TimeoutError) as exc:
            raise VoiceError("Speech synthesis unavailable", 503) from exc
        if not output.startswith(b"RIFF") or len(output) > 4 * 1024 * 1024:
            raise VoiceError("Speech synthesis returned invalid audio", 502)
        return output


def build_providers(settings: Settings) -> tuple[SpeechToText, LanguageModel, TextToSpeech]:
    stt: SpeechToText = ScriptedSTT() if settings.stt_backend == "demo" else WhisperCppSTT(settings)
    llm: LanguageModel = (
        RulesLLM() if settings.llm_backend == "rules" else OpenAICompatibleLLM(settings)
    )
    tts: TextToSpeech = BrowserTTS() if settings.tts_backend == "browser" else EspeakTTS(settings)
    return stt, llm, tts
