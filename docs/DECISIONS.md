# Technical decisions (ADR summary)

## 001: One turn per request

**Status:** Accepted. Use an audio upload endpoint and browser MediaRecorder. Full-duplex streaming, VAD and WebSockets are intentionally deferred. This makes cancellation and reproducible tests tractable. Input audio is fully read within a bounded limit before processing.

## 002: Honest providers and zero paid defaults

**Status:** Accepted. Demo STT returns a known phrase with \`simulated=true\`; rules routing is not a generative LLM. The UI makes the difference visible. Actual speech recognition uses whisper.cpp CLI, with ffmpeg conversion and a separately installed model. Actual audio output uses eSpeak CLI or browser SpeechSynthesis. A remote HTTPS chat completions provider is opt-in only, with explicit credentials and possible cost.

## 003: Small, explicit tool boundary

**Status:** Accepted. Five allowlisted functions use strict Pydantic schemas. All arithmetic is evaluated through a bounded AST allowlist. No arbitrary shell, filesystem reads or model-defined HTTP destinations. Note writes also require direct user wording. Only one function call per turn to bound damage and cost.

## 004: Ephemeral state and local-only exposure

**Status:** Accepted. In-memory sessions, TTL and bounded conversation history. No database, media retention, personal integrations or SaaS authentication in this portfolio demo. Public deployment is explicitly forbidden without a separate authentication, rate-limiting, privacy and abuse-control design.

## 005: Evidence-led automated quality

**Status:** Accepted. GitHub-hosted runners run Python compatibility, static analysis, synthetic audio tests and offline evaluation. They never download models, call paid endpoints or access a physical microphone. No invented benchmarks, screenshots or hosted demo.
