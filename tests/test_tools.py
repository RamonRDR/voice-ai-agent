"""Tool safety checks and isolation."""

import pytest

from voice_ai_agent.errors import VoiceError
from voice_ai_agent.sessions import SessionStore
from voice_ai_agent.tools import ToolRegistry, safe_calculate


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2+2", "4"),
        ("(7-2)*3", "15"),
        ("10/4", "2.5"),
        ("-5 + 9", "4"),
        ("0.1+0.2", "0.3"),
    ],
)
def test_calculate(expression: str, expected: str) -> None:
    assert safe_calculate(expression) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('echo bad')",
        "2**40",
        "2//1",
        "1/0",
        "[x for x in range(5)]",
        "999999999999",
        "(1+2",
        "'hello'",
        "4%2",
        "True + 1",
    ],
)
def test_forbidden_calculations(expression: str) -> None:
    with pytest.raises(VoiceError):
        safe_calculate(expression)


async def test_tool_registry_rejects_invalid_operations() -> None:
    store = SessionStore(12, 1800)
    sid, _ = await store.get(None)
    tools = ToolRegistry(store, "UTC")
    with pytest.raises(VoiceError):
        await tools.execute("run_shell", {"command": "ls"}, sid)
    with pytest.raises(VoiceError):
        await tools.execute("get_current_time", {"unexpected": 1}, sid)
    with pytest.raises(VoiceError):
        await tools.execute("create_note", {"text": "x" * 300}, sid)
    assert "time" in (await tools.execute("get_current_time", {}, sid)).result


async def test_history_is_bounded() -> None:
    store = SessionStore(4, 1800)
    sid, _ = await store.get(None)
    for n in range(5):
        await store.append(sid, f"question {n}", f"answer {n}")
    history = await store.history(sid)
    assert len(history) == 4
    assert history[0].content == "question 3"


async def test_note_limit() -> None:
    store = SessionStore(12, 1800)
    sid, _ = await store.get(None)
    tools = ToolRegistry(store)
    for n in range(20):
        await tools.execute("create_note", {"text": f"note {n}"}, sid)
    with pytest.raises(VoiceError):
        await tools.execute("create_note", {"text": "one too many"}, sid)


def test_provider_config_requires_explicit_opt_in() -> None:
    from pydantic import ValidationError

    from voice_ai_agent.config import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None, mode="remote", llm_backend="rules")
    with pytest.raises(ValidationError):
        Settings(_env_file=None, mode="local", stt_backend="demo")
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            mode="remote",
            stt_backend="whisper_cpp",
            whisper_model="model.bin",
            llm_backend="openai_compatible",
            llm_endpoint="http://example.com",
            llm_api_key="x",
            llm_model="fake",
        )


def test_example_dotenv_enables_default_demo() -> None:
    from pathlib import Path

    from fastapi.testclient import TestClient

    from voice_ai_agent.config import Settings
    from voice_ai_agent.main import create_app

    example = Path(__file__).resolve().parents[1] / ".env.example"
    settings = Settings(_env_file=example)
    assert settings.mode == "demo"
    assert settings.llm_endpoint is None
    assert settings.llm_api_key is None
    assert settings.llm_model is None
    with TestClient(create_app(settings)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/api/config").json()["stt"] == "demo"
