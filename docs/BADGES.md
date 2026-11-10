# Badge inventory and verification

This inventory covers **only** [RamonRDR/voice-ai-agent](https://github.com/RamonRDR/voice-ai-agent). It is based on code, dependency declarations, Dockerfile, CI workflow and the [passing main-branch CI run](https://github.com/RamonRDR/voice-ai-agent/actions/runs/42855676467); it does not assert that untested real speech providers are production-ready.

**Snapshot:** 2026-11-10. **Reference branch:** `main`. **PR:** [#1](https://github.com/RamonRDR/voice-ai-agent/pull/1) (merged; feature branch deleted). **Badges in each README:** 30. **Source of test results:** successful main-branch main-branch CI run #42855676467, with 52 pytest cases per Python version, 8 browser-state tests, 20/20 offline scripted cases and Docker/eSpeak WAV smoke.

| Category | Badge | Evidence | Scope / qualification |
|---|---|---|---|
| General | CI | .github/workflows/ci.yml | workflow branch status |
| General | Python · 3.14 CI plus 3.12 | Dockerfile; .github/workflows/ci.yml | Docker Python 3.14; CI 3.12 and 3.14 |
| General | License · MIT | LICENSE | MIT license |
| Backend and infrastructure | FastAPI · >=0.115 | pyproject.toml; src/voice_ai_agent/main.py | Declared minimum, not pinned |
| Backend and infrastructure | Pydantic · v2 | pyproject.toml; src/voice_ai_agent/schemas.py | Major-version contract |
| Backend and infrastructure | Pydantic Settings · environment | pyproject.toml; src/voice_ai_agent/config.py | Typed environment configuration |
| Backend and infrastructure | Uvicorn · ASGI | pyproject.toml; Dockerfile | Application ASGI server |
| Backend and infrastructure | httpx · >=0.28 | pyproject.toml; src/voice_ai_agent/providers.py | Declared minimum, used by optional remote adapter |
| Backend and infrastructure | python multipart · uploads | pyproject.toml; src/voice_ai_agent/main.py | Multipart audio route |
| Backend and infrastructure | HTML5 · web interface | src/voice_ai_agent/static/index.html | Browser UI |
| Backend and infrastructure | JavaScript · browser UI | src/voice_ai_agent/static/index.html | Plain browser JavaScript |
| Backend and infrastructure | Docker · image build | Dockerfile; .github/workflows/ci.yml | Docker image successfully built |
| Backend and infrastructure | FFmpeg · audio conversion | Dockerfile; src/voice_ai_agent/audio.py | Audio conversion implementation |
| Voice and AI capabilities | MediaRecorder · mic capture | src/voice_ai_agent/static/index.html | Browser microphone API (not physical-browser CI tested) |
| Voice and AI capabilities | STT · scripted demo | src/voice_ai_agent/providers.py | Mocked speech recognition clearly labeled |
| Voice and AI capabilities | whisper.cpp · STT adapter only | src/voice_ai_agent/providers.py | Real integration path, not validated with model in CI |
| Voice and AI capabilities | LLM · opt in HTTPS adapter | src/voice_ai_agent/providers.py; src/voice_ai_agent/config.py | Disabled by default; external provider not CI validated |
| Voice and AI capabilities | Tool Calling · 5 allowlisted | src/voice_ai_agent/tools.py; tests/test_tools.py | Five local functions with strict validation |
| Voice and AI capabilities | eSpeak NG · TTS verified | Dockerfile; .github/workflows/ci.yml | Real WAV response verified in Docker smoke test |
| Voice and AI capabilities | Web Speech API · browser TTS | src/voice_ai_agent/static/index.html | SpeechSynthesis on user click |
| Tests, documentation and quality | pytest · 52 passing | main-branch CI run #42855676467 Python 3.12 and 3.14 jobs | 52 passed, 0 failed, 0 skipped, 1 non-blocking warning |
| Tests, documentation and quality | pytest asyncio · async tests | pyproject.toml; tests/test_pipeline.py | Async pytest fixtures and cases |
| Tests, documentation and quality | Ruff · lint & format | pyproject.toml; .github/workflows/ci.yml | Both CI checks passed |
| Tests, documentation and quality | mypy · type checked | pyproject.toml; .github/workflows/ci.yml | mypy src passed |
| Tests, documentation and quality | Offline evaluation · 20 of 20 scripted | evaluations/scenarios.json; evaluations/run.py; main-branch CI run #42855676467 | Deterministic evaluation only, not a real STT/LLM benchmark |
| Tests, documentation and quality | OpenAPI · documented | src/voice_ai_agent/main.py; tests/test_api.py | FastAPI /docs and /openapi.json |
| Tests, documentation and quality | JS syntax · checked | .github/workflows/ci.yml | node --check on extracted browser script passed |
| Tests, documentation and quality | Browser state tests · 8 passing | tests/browser_state.test.cjs; .github/workflows/ci.yml; main-branch CI run #42855676467 | 8 passed, 0 failed, 0 skipped (Node.js built-in test runner, simulated browser APIs) |
| Tests, documentation and quality | Python build · wheel & sdist | pyproject.toml; .github/workflows/ci.yml | python -m build passed |
| Tests, documentation and quality | Docker smoke · eSpeak WAV | .github/workflows/ci.yml | Live container WAV response assertion passed |

## Static test-count maintenance

The `pytest | 52 passing`, `Browser state tests | 8 passing` and `Offline evaluation | 20 of 20 scripted` badges are **static snapshots**, not continuously calculated status. After a code/test change, wait for a completed and successful CI run for the correct branch. Inspect the actual Pytest, Test browser state and Deterministic evaluation job output (including failures, skips and XPASS/XFAIL). Update the counts in `README.md`, `README.pt-BR.md`, `README.es.md` and this inventory together through a reviewed PR. Never infer counts from files or collected functions. No auto-commits or paid services are used.

The CI badge is **dynamic** and follows `main`, the sole branch after PR #1 merged. The evidence for static quality badges is the successful main-branch run cited above; do not refresh counts from incomplete or failed runs.

## Items intentionally not badged

No PostgreSQL/Redis/SQLite, ORM, Alembic, Docker Compose, Next.js/React, RAG, embeddings, MCP, OAuth, WhatsApp, coverage percentage, WER score, hosted demo, public deployment, full-duplex streaming or real Whisper/remote-LLM validation are evidenced by this repository. Node.js is used **only for JavaScript syntax validation and eight deterministic browser-state regression tests in CI**; it is not the application's runtime and does not constitute real-device microphone testing.

## Review and approval policy

Further code changes should follow the owner's review and PR approval workflow. The repository was merged only after the fourth Codex review reported no actionable findings and all prior review conversations were resolved.
