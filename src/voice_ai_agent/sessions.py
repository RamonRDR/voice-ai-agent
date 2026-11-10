"""Ephemeral single-process session store; no persistent audio or personal data."""

import asyncio
import time
import uuid
from dataclasses import dataclass, field

from .errors import VoiceError
from .schemas import Message


@dataclass
class Session:
    touched: float = field(default_factory=time.monotonic)
    active_turns: int = 0
    messages: list[Message] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class SessionStore:
    def __init__(self, history_limit: int, ttl_seconds: int) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = asyncio.Lock()
        self.history_limit = history_limit
        self.ttl_seconds = ttl_seconds

    async def get(self, session_id: str | None, *, pin: bool = False) -> tuple[str, Session]:
        async with self._lock:
            now = time.monotonic()
            self._sessions = {
                key: value
                for key, value in self._sessions.items()
                if value.active_turns > 0 or now - value.touched < self.ttl_seconds
            }
            if session_id is not None:
                try:
                    uuid.UUID(session_id)
                except (ValueError, AttributeError) as exc:
                    raise VoiceError("Invalid session ID") from exc
                if session_id not in self._sessions:
                    raise VoiceError("Session not found or expired", status_code=404)
            else:
                session_id = str(uuid.uuid4())
                self._sessions[session_id] = Session()
            session = self._sessions[session_id]
            session.touched = now
            if pin:
                session.active_turns += 1
            return session_id, session

    async def release(self, session_id: str) -> None:
        """Keep an in-flight session alive, then restart its TTL when work finishes."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is not None and session.active_turns > 0:
                session.active_turns -= 1
                session.touched = time.monotonic()

    async def append(self, session_id: str, user: str, assistant: str) -> None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise VoiceError("Session expired", status_code=404)
            session.messages.extend(
                [Message(role="user", content=user), Message(role="assistant", content=assistant)]
            )
            session.messages = session.messages[-self.history_limit :]
            session.touched = time.monotonic()

    async def history(self, session_id: str) -> list[Message]:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise VoiceError("Session not found or expired", status_code=404)
            return list(session.messages)

    async def add_note(self, session_id: str, text: str) -> int:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise VoiceError("Session not found or expired", status_code=404)
            if len(session.notes) >= 20:
                raise VoiceError("Note limit reached")
            session.notes.append(text)
            return len(session.notes)

    async def list_notes(self, session_id: str) -> list[str]:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise VoiceError("Session not found or expired", status_code=404)
            return list(session.notes)
