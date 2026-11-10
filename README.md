<div align="center">

# Voice AI Agent 🎙️

**Turn speech into actions with modular Python, controlled tools, and transparent AI modes.**

[🇺🇸 English](README.md) · [🇧🇷 Português](README.pt-BR.md) · [🇪🇸 Español](README.es.md)

[![CI](https://github.com/RamonRDR/voice-ai-agent/actions/workflows/ci.yml/badge.svg?branch=feat%2Fvoice-ai-agent-mvp)](https://github.com/RamonRDR/voice-ai-agent/actions/workflows/ci.yml)
![Python: 3.14 CI plus 3.12](https://img.shields.io/badge/Python-3.14%20CI%20plus%203.12-3776AB)
![License: MIT](https://img.shields.io/badge/License-MIT-36B37E)

![FastAPI: >=0.115](https://img.shields.io/badge/FastAPI-%3E%3D0.115-009688)
![Pydantic: v2](https://img.shields.io/badge/Pydantic-v2-E92063)
![Pydantic Settings: environment](https://img.shields.io/badge/Pydantic%20Settings-environment-B72867)
![Uvicorn: ASGI](https://img.shields.io/badge/Uvicorn-ASGI-4051B5)
![httpx: >=0.28](https://img.shields.io/badge/httpx-%3E%3D0.28-5A6EA8)
![python multipart: uploads](https://img.shields.io/badge/python%20multipart-uploads-64748B)
![HTML5: web interface](https://img.shields.io/badge/HTML5-web%20interface-E34F26)
![JavaScript: browser UI](https://img.shields.io/badge/JavaScript-browser%20UI-F7DF1E)
![Docker: image build](https://img.shields.io/badge/Docker-image%20build-2496ED)
![FFmpeg: audio conversion](https://img.shields.io/badge/FFmpeg-audio%20conversion-4B8E36)

![MediaRecorder: mic capture](https://img.shields.io/badge/MediaRecorder-mic%20capture-6B7280)
![STT: scripted demo](https://img.shields.io/badge/STT-scripted%20demo-6B7280)
![whisper.cpp: STT adapter only](https://img.shields.io/badge/whisper.cpp-STT%20adapter%20only-6B7280)
![LLM: opt in HTTPS adapter](https://img.shields.io/badge/LLM-opt%20in%20HTTPS%20adapter-6B7280)
![Tool Calling: 5 allowlisted](https://img.shields.io/badge/Tool%20Calling-5%20allowlisted-6F42C1)
![eSpeak NG: TTS verified](https://img.shields.io/badge/eSpeak%20NG-TTS%20verified-3478C0)
![Web Speech API: browser TTS](https://img.shields.io/badge/Web%20Speech%20API-browser%20TTS-3478C0)

![pytest: 52 passing](https://img.shields.io/badge/pytest-52%20passing-0A9EDC)
![pytest asyncio: async tests](https://img.shields.io/badge/pytest%20asyncio-async%20tests-0A9EDC)
![Ruff: lint & format](https://img.shields.io/badge/Ruff-lint%20%26%20format-D7FF64)
![mypy: type checked](https://img.shields.io/badge/mypy-type%20checked-2A6DB4)
![Offline evaluation: 20 of 20 scripted](https://img.shields.io/badge/Offline%20evaluation-20%20of%2020%20scripted-6F42C1)
![OpenAPI: documented](https://img.shields.io/badge/OpenAPI-documented-6BA539)
![JS syntax: checked](https://img.shields.io/badge/JS%20syntax-checked-F7DF1E)
![Browser state tests: 7 passing](https://img.shields.io/badge/Browser%20state%20tests-7%20passing-F7DF1E)
![Python build: wheel & sdist](https://img.shields.io/badge/Python%20build-wheel%20%26%20sdist-6B7280)
![Docker smoke: eSpeak WAV](https://img.shields.io/badge/Docker%20smoke-eSpeak%20WAV-2496ED)

</div>

> **Project status:** MVP implemented on [Draft PR #1](https://github.com/RamonRDR/voice-ai-agent/pull/1), not merged to `main`. **Codex round 1** identified five findings (1 P1, 4 P2), all treated with regression tests. **Round 2** identified two additional P2 browser issues (late cancellation and back-forward cache restoration), also corrected with focused tests; another review has not yet been requested. [GitHub Actions feature-branch run #42849121931](https://github.com/RamonRDR/voice-ai-agent/actions/runs/42849121931) passed **52/52 pytest per Python version, 7/7 simulated-browser state tests, 20/20 scripted evaluations** and Docker eSpeak WAV smoke. Real Whisper STT and external LLM remain unvalidated with actual providers.

## Overview

An intentionally compact voice agent showcasing Python, FastAPI, validated audio uploads, real local speech recognition through whisper.cpp, an opt-in LLM adapter with constrained tool calling, real speech synthesis, and an accessible browser interface. Designed as a **turn-based** demonstrator, not a production voice SaaS.

> **Honest demo labeling:** Out of the box, speech-to-text is *scripted*, responses are *rule-based*, tools perform real local operations, and speech is synthesized by your browser when you click Play. Docker defaults to **real local eSpeak synthesis**. Use the local configuration below for actual STT and the opt-in remote configuration for generative LLM responses. A scripted transcript is never presented as recognized speech.

## Features

- Microphone recording (permission requested on click), stop, upload, typed test input, response playback and cancellation.
- Explicit WAV, WebM, OGG, MP3 and M4A handling, signature validation, max upload/duration, conversion to 16-kHz mono PCM16, silence detection and per-request temporary-file cleanup.
- Pluggable STT: deterministic **ScriptedSTT** or real **whisper.cpp** CLI using a separately provisioned model.
- Pluggable conversation logic: deterministic **RulesLLM**, or opt-in HTTPS OpenAI-compatible chat completions with validated function calls.
- Five allowlisted tools: current time (configurable timezone), safe basic arithmetic, create/list short session notes, and a bounded session summary.
- Pluggable TTS: real browser SpeechSynthesis on explicit click or real server-side eSpeak-NG WAV output.
- One-request-at-a-time session processing, cancellation, duplicate request protection, expiring in-memory sessions and bounded conversation history.
- OpenAPI, health endpoint, stage timings, deterministic tests and 20 offline routing evaluation cases, Docker and GitHub Actions.
- Documentation in English, Brazilian Portuguese and Spanish.

## Technology stack

Python **3.14** is used by Docker and CI; CI also tests **3.12** (`requires-python >=3.12`). The dependency declarations are **ranges**, not pinned installs: FastAPI `>=0.115,<1`, Uvicorn `>=0.32,<1`, Pydantic `>=2.10,<3`, Pydantic Settings `>=2.6,<3`, httpx `>=0.28,<1` and python-multipart `>=0.0.20,<1`. The browser UI is native HTML/JavaScript with MediaRecorder and SpeechSynthesis. Docker installs FFmpeg and eSpeak-NG. Development tools: pytest, pytest-asyncio, Ruff, mypy, Python packaging and GitHub Actions.

**AI capability boundaries:** scripted STT and rule routing are the default; whisper.cpp is a **real STT adapter not exercised with a downloaded model in CI**; an HTTPS OpenAI-compatible LLM is opt-in and **not provider-tested**; the eSpeak WAV output **was verified** in a live Docker smoke test. The five local tools really execute under Pydantic validation. No database, Redis, Docker Compose, authentication, public deployment, RAG or MCP is implemented.

## Architecture and pipeline

```text
[Browser microphone / upload] --HTTPS or localhost--> [FastAPI]
      |                                           |
[Typed debug input] ------------------------------+
                                                  v
                           [validate | cap size/duration | ffmpeg WAV]
                                                  |
                          [Scripted STT (demo) / whisper.cpp (real)]
                                                  |
                             [Rules (demo) / opt-in remote LLM]
                                                  |
                          [allowlisted Pydantic tool arguments]
                                                  |
                                    [real local tool execution]
                                                  |
                           [response text + bounded session history]
                                                  |
                      [browser SpeechSynthesis / eSpeak WAV synthesis]
                                                  |
                              [text, audio, timings and tool status]
```

The typed-input route intentionally bypasses STT and labels the input as **typed**. In demo mode, uploaded audio is decoded and validated, but speech recognition is **not** performed: the scripted STT returns a fixed example question in the selected language, with `simulated: true`. This avoids representing dummy output as real recognition.

Source layout: `main.py` (FastAPI), `audio.py` (validation), `providers.py` (STT / LLM / TTS), `tools.py` (Pydantic allowlist), `pipeline.py` (orchestration), `sessions.py` (ephemeral state), `static/index.html` (web UI).

## Project structure

| Path | Responsibility |
|---|---|
| `src/voice_ai_agent/main.py` | FastAPI, routes, health, OpenAPI and static app |
| `audio.py`, `providers.py` | Audio validation, ffmpeg, STT/LLM/TTS adapters |
| `pipeline.py`, `sessions.py` | Turn orchestration, cancellation and bounded state |
| `tools.py`, `schemas.py`, `config.py` | Allowlisted actions, Pydantic contracts and settings |
| `static/index.html`, `prompts/system_v1.txt` | Browser UI and versioned LLM instructions |
| `tests/`, `evaluations/` | Synthetic audio tests and scripted evaluation suite |
| `.github/workflows/ci.yml`, `Dockerfile` | GitHub Actions and container smoke test |

## Requirements and install

- Python **3.14** is the preferred runtime; CI also checks **3.12**.
- ffmpeg to convert compressed/browser audio; WAV 16-kHz mono PCM16 can be processed without it.
- Optional: `whisper-cli` built from [whisper.cpp](https://github.com/ggml-org/whisper.cpp) and your own compatible GGML model for **real STT**.
- Optional: `espeak-ng` for **server TTS**. Browser SpeechSynthesis requires a compatible browser.
- For microphone recording: **localhost** or **HTTPS** secure context, plus explicit user permission. MediaRecorder support varies by browser.

```bash
git clone https://github.com/RamonRDR/voice-ai-agent.git
cd voice-ai-agent
python -m venv .venv
# Activate .venv using your shell's standard command
python -m pip install -e ".[dev]"
cp .env.example .env
uvicorn voice_ai_agent.main:app --host 127.0.0.1 --port 8000
```

Visit **http://127.0.0.1:8000** for the UI and **http://127.0.0.1:8000/docs** for OpenAPI.

For a local container demo with **actual eSpeak TTS**, run `docker build -t voice-ai-agent .` and `docker run --rm -p 127.0.0.1:8000:8000 voice-ai-agent`. The Dockerfile installs ffmpeg and eSpeak, but does not download Whisper models. It is a localhost demo, not a hardened public server.

## Configuration: demo, real STT and generative LLM

Copy `.env.example` and change only what you intend to enable:

| Variable | Demo default | Real option |
|---|---|---|
| `VOICE_MODE` | `demo` | `local` or `remote` |
| `VOICE_STT_BACKEND` | `demo` | `whisper_cpp` |
| `VOICE_WHISPER_MODEL` | empty | absolute path to an installed GGML model |
| `VOICE_WHISPER_EXECUTABLE` | `whisper-cli` | path to built executable |
| `VOICE_LLM_BACKEND` | `rules` | `openai_compatible` (remote mode only) |
| `VOICE_LLM_ENDPOINT` | empty | explicitly configured HTTPS chat-completions endpoint |
| `VOICE_LLM_MODEL` | empty | provider's model identifier |
| `VOICE_LLM_API_KEY` | empty | secret, never commit |
| `VOICE_TTS_BACKEND` | `browser` | `espeak` |
| `VOICE_TIMEZONE` | `America/Sao_Paulo` in example | valid IANA timezone |

The default local limits are **8 MiB** per uploaded file, **30 seconds** per recording, **12 history messages**, **30-minute session TTL** and a **90-second processing timeout**; all are configurable in `.env.example` and enforced within the declared bounds. The local settings default to UTC if the example `.env` is not loaded. For real local speech recognition, install whisper.cpp and its model separately. Then configure:

```dotenv
VOICE_MODE=local
VOICE_STT_BACKEND=whisper_cpp
VOICE_WHISPER_EXECUTABLE=/path/to/whisper-cli
VOICE_WHISPER_MODEL=/path/to/ggml-base.bin
VOICE_LLM_BACKEND=rules
VOICE_TTS_BACKEND=espeak
```

That mode performs **real local STT and TTS**, but the conversation policy is still explicitly **scripted rules**, not a generative model. Whisper model requirements, licensing, language availability and performance depend on the chosen build and model. Downloads are not part of CI. `en` and `pt` are target languages; `es` is available as a configurable best-effort selection.

For **actual LLM generation**, explicitly switch to `VOICE_MODE=remote`, retain `whisper_cpp`, configure `VOICE_LLM_BACKEND=openai_compatible` and set HTTPS `VOICE_LLM_ENDPOINT`, model and key. This can transmit text to a third party **and may incur charges**; do not enable without your own provider authorization. Tool arguments are validated and only one call is executed per turn. In particular, **tools never receive arbitrary file paths, shell commands or model-selected HTTP URLs**.

## API reference

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Browser demo interface |
| `GET` | `/health` | Service health |
| `GET` | `/docs`, `/openapi.json` | Interactive and machine-readable OpenAPI |
| `GET` | `/api/config` | Current provider mode and its demo disclaimer |
| `POST` | `/api/session` | Create a temporary session |
| `POST` | `/api/turn` | Audio upload, STT and response pipeline |
| `POST` | `/api/turn/text` | Typed input; does not exercise STT |
| `GET` | `/api/history/{session_id}` | Bounded conversation history |
| `POST` | `/api/cancel/{request_id}` | Attempt to cancel a turn, with session_id query |

## API examples

```bash
# Start an ephemeral session (no login; keep local)
curl -X POST http://127.0.0.1:8000/api/session

# Text route for deterministic logic/tool demonstrations, does not exercise STT:
curl -X POST http://127.0.0.1:8000/api/turn/text \
  -H 'Content-Type: application/json' \
  -d '{"text":"calculate 12*4","language":"en"}'

# Real/Scripted audio route depending on configured STT:
curl -X POST http://127.0.0.1:8000/api/turn \
  -F 'audio=@example.wav' -F 'language=en'
```

The response contains a session ID, request ID, text transcript, `simulated` and `source` flags, response, optional real tool result, WAV audio as base64 if using eSpeak, and stage latencies. Reuse `session_id` on subsequent turns. POST `/api/cancel/{request_id}?session_id=...` cancels an in-flight request. GET `/api/history/{session_id}` returns only the bounded session transcript.

## Demonstration and evaluation

For the **zero-paid-API demonstration**:

1. Run the default demo and open the UI.
2. Enter `What time is it?`, `calculate 12*4`, `note: buy milk`, then `list notes`.
3. Use a synthetic audio WAV upload or microphone: the UI visibly labels its *scripted STT*, while the upload and pipeline still validate audio.
4. Click **Play latest reply** to use actual browser synthesis (or the actual eSpeak audio when configured).
5. Try a silent WAV, invalid file, or cancel an in-flight operation to demonstrate error handling.

Use `python evaluations/run.py` for 20 **offline scripted-routing scenarios**. These are not Whisper accuracy benchmarks and do not measure generative LLM quality. Use `pytest -q` for request, cancellation, sanitization, isolation, TTS-mode and integration tests; all fixtures synthesize audio without real people's recordings. No paid APIs or large models are needed in mandatory CI. WER is not reported because this project does not include a reference-transcript evaluation corpus for real STT. Latencies are **observations per interaction**, not invented benchmark figures.

For an interview recording or screenshot, operate the application yourself in the chosen mode and accurately label the provider configuration. No screenshots, hosted demo or results are asserted without evidence.

## Tests / CI

```bash
python -m pip install -e ".[dev]" build
ruff check .
ruff format --check .
mypy src
pytest -q
python evaluations/run.py
node --test tests/browser_state.test.cjs
python -m build
```

GitHub Actions uses standard GitHub-hosted Ubuntu runners, Python 3.12/3.14, ffmpeg, package checks, simulated integration tests, offline evals and a Docker build. It does not depend on a personal runner or microphone and never invokes Codex, a remote paid model or a deployment.

## Badge evidence and maintenance

The `pytest | 52 passing` badge is a **static snapshot** of [GitHub Actions feature-branch run #42849121931](https://github.com/RamonRDR/voice-ai-agent/actions/runs/42849121931) on `feat/voice-ai-agent-mvp`: **52 passed, 0 failed, 0 skipped, 1 non-blocking third-party deprecation warning** in each Python version. The separate **20/20** badge refers only to the deterministic scripted evaluation in the same run; it is not a speech accuracy score or LLM benchmark. Ruff lint and formatting, mypy, JS syntax, **7/7 Node.js browser-state regression tests**, wheel/sdist build, Docker build and actual eSpeak WAV smoke test all passed. No coverage percentage is claimed.

The CI image badge follows the **feature branch** because `main` still contains only the initial files. On an authorized merge, change its branch selection to `main` in **all three READMEs**, then verify CI on main. After any test additions, removals, parametrizations or skips, read the latest successful **Pytest**, **browser state**, and **Deterministic evaluation** jobs on the relevant branch, update the static badge counts in all three languages through a reviewed PR, and update [badge inventory and evidence](docs/BADGES.md). Badges must never be refreshed from a failed or partial test run.

## Security and privacy

- Microphone starts only after a click and permission; audio output playback is user initiated.
- Fixed file signatures, size/duration checks, canonicalized WAV, safe subprocess argument vectors (no shell), limited messages and output length.
- No stored audio: temporary files are removed after processing, including failure. Notes and history stay in process memory until expiry/restart.
- User transcripts are untrusted inputs. Function calls use fixed schemas and allowlisted execution; note writes require explicit user wording. No arbitrary code execution or unbounded URLs.
- No secrets are checked into Git. The opt-in remote LLM sends text/history to the configured third-party provider, subject to its own privacy terms.
- Minimal CI permissions, synthetic inputs, no public artifacts containing voice recordings, no model downloads, no auto deployment or auto merge.

**Not production-ready:** the application intentionally has **no authentication, multi-tenant isolation, public rate limiting, distributed state or billing guardrails**. Do not expose it publicly before adding auth, origin/request protections, abuse limits, authenticated sessions, cost budgets and a security review. This local/demo limitation is deliberate. See [SECURITY](docs/SECURITY.md).

## Known limitations / evolution

Turn-based requests only; no full-duplex streaming, WebSockets or real-time speech interruption. The scripted demo is not speech recognition or a generative LLM. Local whisper.cpp requires separately installed executable/model. eSpeak voices are synthetic and may sound robotic. Browser recording/container audio codec support varies. Sessions are in-memory single-instance only, and cancellation is best-effort between awaited stages. External integrations, persistent storage, public deployment and voice cloning are intentionally out of scope.

Next steps: document a real Whisper integration run in a suitable local machine, optionally add opt-in realistic STT/TTS benchmarks, and only later investigate VAD/streaming and authenticated deployment.

## Contributing

Contributions and issue reports are welcome through a reviewed pull request. Do not commit recordings, provider credentials or large model weights. Keep scripted and real-provider behavior explicitly distinguished, add deterministic tests for changes, and preserve the approval-only merge policy described in [PR #1](https://github.com/RamonRDR/voice-ai-agent/pull/1).

## License

MIT, copyright © 2026 Ramon Rodriguez. See [LICENSE](LICENSE). Third-party engine/model licenses remain governed by their owners; validate downloaded model and voice licensing separately. Architectural rationale: [DECISIONS](docs/DECISIONS.md).
