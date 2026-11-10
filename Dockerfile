FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VOICE_MODE=demo \
    VOICE_STT_BACKEND=demo \
    VOICE_LLM_BACKEND=rules \
    VOICE_TTS_BACKEND=espeak
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg espeak-ng ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN python -m pip install --no-cache-dir .
RUN useradd --create-home --uid 10001 --gid voice voice
USER voice
EXPOSE 8000
CMD ["uvicorn", "voice_ai_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
