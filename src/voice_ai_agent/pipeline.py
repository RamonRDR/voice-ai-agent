"""Turn-by-turn orchestration, bounded state and cancellation."""

import asyncio
import base64
import tempfile
import time
import uuid
from pathlib import Path

from fastapi import UploadFile

from .audio import prepare_audio
from .config import Settings
from .errors import VoiceError
from .providers import build_providers
from .schemas import Metrics, Transcription, TurnResponse
from .sessions import SessionStore
from .tools import ToolRegistry


def elapsed_ms(start: float) -> int:
    return round((time.perf_counter() - start) * 1000)


class VoicePipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.stt, self.llm, self.tts = build_providers(settings)
        self.store = SessionStore(settings.max_history, settings.session_ttl_seconds)
        self.tools = ToolRegistry(self.store, settings.timezone)
        self.running: dict[str, tuple[str, asyncio.Task[object]]] = {}
        self.busy_sessions: set[str] = set()
        self.completed: set[str] = set()

    async def process(
        self,
        session_id: str | None,
        request_id: str | None,
        language: str,
        audio: UploadFile | None = None,
        text: str | None = None,
    ) -> TurnResponse:
        if (audio is None) == (text is None):
            raise VoiceError("Provide audio or text, not both")
        if language not in ("en", "pt", "es"):
            raise VoiceError("Unsupported language")
        session_id, _ = await self.store.get(session_id)
        request_id = request_id or str(uuid.uuid4())
        try:
            uuid.UUID(request_id)
        except ValueError as exc:
            raise VoiceError("Invalid request ID") from exc
        if request_id in self.running or request_id in self.completed:
            raise VoiceError("Duplicate request ID", 409)
        if session_id in self.busy_sessions:
            raise VoiceError("Another turn is processing in this session", 409)
        self.busy_sessions.add(session_id)
        task = asyncio.current_task()
        assert task is not None
        self.running[request_id] = (session_id, task)
        started = time.perf_counter()
        metrics = Metrics()
        try:
            if audio is not None:
                with tempfile.TemporaryDirectory(prefix="voice-turn-") as temp:
                    wav = await prepare_audio(audio, self.settings, Path(temp))
                    tick = time.perf_counter()
                    transcript = await asyncio.wait_for(
                        self.stt.transcribe(wav, language),
                        timeout=self.settings.process_timeout_seconds,
                    )
                    metrics.stt_ms = elapsed_ms(tick)
            else:
                assert text is not None
                transcript = Transcription(
                    text=text.strip(), language=language, source="typed", simulated=False
                )
            if not transcript.text or not transcript.text.strip():
                raise VoiceError("No recognizable speech")
            if len(transcript.text) > 1000:
                raise VoiceError("Transcription too long")
            tick = time.perf_counter()
            history = await self.store.history(session_id)
            model = await asyncio.wait_for(
                self.llm.respond(transcript.text, history),
                timeout=self.settings.process_timeout_seconds,
            )
            metrics.llm_ms = elapsed_ms(tick)
            tool_result = None
            response = model.content or ""
            if model.tool_name:
                if model.tool_name == "create_note":
                    requested = (
                        transcript.text.casefold()
                        .lstrip()
                        .startswith(
                            ("note:", "save note:", "anote:", "anotar:", "nota:", "apunta:")
                        )
                    )
                    if not requested:
                        raise VoiceError("Note creation needs an explicit user request", 403)
                tick = time.perf_counter()
                tool_result = await self.tools.execute(
                    model.tool_name, model.tool_args or {}, session_id
                )
                metrics.tools_ms = elapsed_ms(tick)
                response = f"{tool_result.name}: {tool_result.result}"
            if not response.strip():
                raise VoiceError("Assistant produced an empty response", 502)
            response = response[:1000]
            tick = time.perf_counter()
            audio_bytes: bytes | None = None
            tts_error = None
            try:
                audio_bytes = await asyncio.wait_for(
                    self.tts.synthesize(response, language),
                    timeout=self.settings.process_timeout_seconds,
                )
            except (VoiceError, TimeoutError, OSError):
                tts_error = "Server speech synthesis unavailable; use the browser voice button."
            metrics.tts_ms = elapsed_ms(tick)
            await self.store.append(session_id, transcript.text, response)
            metrics.total_ms = elapsed_ms(started)
            return TurnResponse(
                session_id=session_id,
                request_id=request_id,
                transcript=transcript,
                response=response,
                tool=tool_result,
                audio_base64=base64.b64encode(audio_bytes).decode("ascii") if audio_bytes else None,
                audio_mime="audio/wav" if audio_bytes else None,
                tts_source="espeak" if audio_bytes else "browser",
                tts_error=tts_error,
                metrics=metrics,
            )
        except TimeoutError as exc:
            raise VoiceError("Processing timed out", 504) from exc
        finally:
            self.running.pop(request_id, None)
            self.busy_sessions.discard(session_id)
            self.completed.add(request_id)
            if len(self.completed) > 1000:
                self.completed.clear()

    async def cancel(self, request_id: str, session_id: str) -> bool:
        item = self.running.get(request_id)
        if item and item[0] == session_id:
            item[1].cancel()
            return True
        return False
