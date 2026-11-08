# Voice AI Agent

[![CI](https://github.com/RamonRDR/voice-ai-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/RamonRDR/voice-ai-agent/actions/workflows/ci.yml)
[![MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**English** | [Português](README.pt-BR.md) | [Español](README.es.md)

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

For real local speech recognition, install whisper.cpp and its model separately. Then configure:

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

## Security and privacy

- Microphone starts only after a click and permission; audio output playback is user initiated.
- Fixed file signatures, size/duration checks, canonicalized WAV, safe subprocess argument vectors (no shell), limited messages and output length.
- No stored audio: temporary files are removed after processing, including failure. Notes and history stay in process memory until expiry/restart.
- User transcripts are untrusted inputs. Function calls use fixed schemas and allowlisted execution; note writes require explicit user wording. No arbitrary code execution or unbounded URLs.
- No secrets are checked into Git. The opt-in remote LLM sends text/history to the configured third-party provider, subject to its own privacy terms.
- Minimal CI permissions, synthetic inputs, no public artifacts containing voice recordings, no model downloads, no auto deployment or auto merge.

**Not production-ready:** the application intentionally has **no authentication, multi-tenant isolation, public rate limiting, distributed state or billing guardrails**. Do not expose it publicly before adding auth, origin/request protections, abuse limits, authenticated sessions, cost budgets and a security review. This local/demo limitation is deliberate. See [SECURITY](docs/SECURITY.md).

## Tests / CI

```bash
python -m pip install -e ".[dev]" build
ruff check .
ruff format --check .
mypy src
pytest -q
python evaluations/run.py
python -m build
```

GitHub Actions uses standard GitHub-hosted Ubuntu runners, Python 3.12/3.14, ffmpeg, package checks, simulated integration tests, offline evals and a Docker build. It does not depend on a personal runner or microphone and never invokes Codex, a remote paid model or a deployment.

## Known limitations / evolution

Turn-based requests only; no full-duplex streaming, WebSockets or real-time speech interruption. The scripted demo is not speech recognition or a generative LLM. Local whisper.cpp requires separately installed executable/model. eSpeak voices are synthetic and may sound robotic. Browser recording/container audio codec support varies. Sessions are in-memory single-instance only, and cancellation is best-effort between awaited stages. External integrations, persistent storage, public deployment and voice cloning are intentionally out of scope.

Next steps: document a real Whisper integration run in a suitable local machine, optionally add opt-in realistic STT/TTS benchmarks, and only later investigate VAD/streaming and authenticated deployment.

## License

MIT, copyright © 2026 Ramon Rodriguez. See [LICENSE](LICENSE). Third-party engine/model licenses remain governed by their owners; validate downloaded model and voice licensing separately. Architectural rationale: [DECISIONS](docs/DECISIONS.md).
