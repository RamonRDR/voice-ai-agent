"""FastAPI application and static, locally hosted demonstration interface."""

import asyncio
import logging
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import Settings, get_settings
from .errors import VoiceError
from .pipeline import VoicePipeline
from .schemas import RuntimeInfo, TextTurnRequest, TurnResponse

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("voice_ai_agent")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title="Voice AI Agent",
        version="0.1.0",
        description="Turn-based voice assistant with explicitly labeled demo components.",
    )
    pipeline = VoicePipeline(settings)
    app.state.pipeline = pipeline
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )

    @app.exception_handler(VoiceError)
    async def voice_error(_request: Request, exc: VoiceError) -> JSONResponse:
        logger.warning("voice_error status=%s category=%s", exc.status_code, type(exc).__name__)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": "Invalid request parameters"})

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": "0.1.0"}

    @app.post("/api/session")
    async def new_session() -> dict[str, str]:
        session_id, _session = await pipeline.store.get(None)
        return {"session_id": session_id}

    @app.get("/api/config", response_model=RuntimeInfo)
    async def config() -> RuntimeInfo:
        demo = settings.stt_backend == "demo"
        return RuntimeInfo(
            mode=settings.mode,
            stt=settings.stt_backend,
            llm=settings.llm_backend,
            tts=settings.tts_backend,
            microphone_is_recognized=not demo,
            disclaimer=(
                "DEMO: Speech-to-text is scripted and replies are rules, not AI recognition."
                if demo
                else "Real STT enabled. Audio stays local unless a remote LLM is configured."
            ),
        )

    @app.post("/api/turn", response_model=TurnResponse)
    async def audio_turn(
        audio: Annotated[UploadFile, File()],
        session_id: Annotated[str | None, Form()] = None,
        request_id: Annotated[str | None, Form()] = None,
        language: Annotated[Literal["en", "pt", "es"], Form()] = "en",
    ) -> TurnResponse:
        try:
            return await pipeline.process(session_id, request_id, language, audio=audio)
        except asyncio.CancelledError:
            raise VoiceError("Processing cancelled", status_code=409) from None
        finally:
            await audio.close()

    @app.post("/api/turn/text", response_model=TurnResponse)
    async def text_turn(body: TextTurnRequest) -> TurnResponse:
        try:
            return await pipeline.process(
                body.session_id, body.request_id, body.language, text=body.text
            )
        except asyncio.CancelledError:
            raise VoiceError("Processing cancelled", status_code=409) from None

    @app.post("/api/cancel/{request_id}")
    async def cancel(request_id: str, session_id: str) -> dict[str, bool]:
        return {"cancelled": await pipeline.cancel(request_id, session_id)}

    @app.get("/api/history/{session_id}")
    async def history(session_id: str) -> dict[str, object]:
        _id, _session = await pipeline.store.get(session_id)
        return {
            "session_id": _id,
            "messages": [item.model_dump() for item in await pipeline.store.history(_id)],
        }

    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run("voice_ai_agent.main:app", host="127.0.0.1", port=8000)
