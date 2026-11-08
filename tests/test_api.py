"""API and deterministic full-pipeline tests."""

import uuid

from fastapi.testclient import TestClient

from conftest import make_wav


def new_session(client: TestClient) -> str:
    response = client.post("/api/session")
    assert response.status_code == 200
    return response.json()["session_id"]


def test_health_and_docs(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/openapi.json").status_code == 200
    assert "VOICE" in client.get("/").text
    assert client.get("/api/config").json()["microphone_is_recognized"] is False


def test_demo_audio_pipeline_is_explicitly_simulated(client: TestClient) -> None:
    sid = new_session(client)
    result = client.post(
        "/api/turn",
        files={"audio": ("synthetic.wav", make_wav(), "audio/wav")},
        data={"session_id": sid, "language": "en"},
    )
    assert result.status_code == 200, result.text
    body = result.json()
    assert body["transcript"]["simulated"] is True
    assert body["transcript"]["source"] == "scripted"
    assert body["tool"]["name"] == "get_current_time"
    assert body["metrics"]["total_ms"] >= 0
    assert body["audio_base64"] is None
    assert body["tts_source"] == "browser"
    assert len(client.get("/api/history/" + sid).json()["messages"]) == 2


def test_text_tool_calling_and_notes(client: TestClient) -> None:
    sid = new_session(client)

    def send(text: str) -> dict:
        response = client.post("/api/turn/text", json={"session_id": sid, "text": text})
        assert response.status_code == 200, response.text
        return response.json()

    assert send("calculate 12*4")["tool"]["result"]["value"] == "48"
    assert send("note: buy milk")["tool"]["result"]["created"] is True
    assert send("list notes")["tool"]["result"]["notes"] == ["buy milk"]
    assert send("session summary")["tool"]["result"]["turns"] == 3
    assert len(client.get("/api/history/" + sid).json()["messages"]) == 8


def test_note_is_session_isolated(client: TestClient) -> None:
    a, b = new_session(client), new_session(client)
    client.post("/api/turn/text", json={"session_id": a, "text": "note: private"})
    response = client.post("/api/turn/text", json={"session_id": b, "text": "list notes"})
    assert response.json()["tool"]["result"]["notes"] == []


def test_duplicate_request_rejected(client: TestClient) -> None:
    sid = new_session(client)
    rid = str(uuid.uuid4())
    body = {"session_id": sid, "request_id": rid, "text": "hello"}
    assert client.post("/api/turn/text", json=body).status_code == 200
    assert client.post("/api/turn/text", json=body).status_code == 409


def test_validation_and_cross_session(client: TestClient) -> None:
    assert client.post("/api/turn/text", json={"text": ""}).status_code == 422
    assert client.post("/api/turn/text", json={"text": "hi", "language": "fr"}).status_code == 422
    assert client.post("/api/turn/text", json={"text": "hi", "session_id": "invalid"}).status_code == 422
    assert client.get("/api/history/" + str(uuid.uuid4())).status_code == 404
    assert client.post("/api/cancel/" + str(uuid.uuid4()) + "?session_id=invalid").json() == {
        "cancelled": False
    }


def test_empty_invalid_silent_audio_and_length(client: TestClient) -> None:
    sid = new_session(client)
    for data in (b"", b"not audio", make_wav(silence=True), make_wav(seconds=31.0)):
        response = client.post(
            "/api/turn",
            files={"audio": ("bad.wav", data, "audio/wav")},
            data={"session_id": sid},
        )
        assert response.status_code in (413, 422), response.text


def test_unsupported_or_corrupted_wav(client: TestClient) -> None:
    sid = new_session(client)
    invalid = b"RIFF" + bytes(4) + b"WAVE" + b"invalid"
    result = client.post(
        "/api/turn", files={"audio": ("fake.wav", invalid, "audio/wav")},
        data={"session_id": sid},
    )
    assert result.status_code == 422


def test_upload_size_limit() -> None:
    from voice_ai_agent.config import Settings
    from voice_ai_agent.main import create_app

    app = create_app(Settings(_env_file=None, max_upload_bytes=1024))
    with TestClient(app) as client:
        result = client.post(
            "/api/turn",
            files={"audio": ("large.wav", make_wav(), "audio/wav")},
        )
        assert result.status_code == 413


def test_audio_conversion_8khz(client: TestClient) -> None:
    result = client.post(
        "/api/turn",
        files={"audio": ("tone.wav", make_wav(sample_rate=8000), "audio/wav")},
    )
    assert result.status_code == 200, result.text
    assert result.json()["transcript"]["simulated"] is True
