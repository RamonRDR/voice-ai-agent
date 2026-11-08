# Voice AI Agent

[English](README.md) | [Português](README.pt-BR.md) | **Español**

Agente conversacional por voz **por turnos**, desarrollado en Python y FastAPI como demostración técnica. Incluye grabación en navegador, carga validada, transcripción STT, integración opcional con LLM, herramientas seguras y respuestas habladas.

> **Modo demo transparente:** STT **simulado** con etiqueta visible, respuestas **predefinidas**, pero operaciones de herramientas locales reales. El navegador realiza síntesis de voz real al pulsar Reproducir. Docker instala eSpeak para TTS real. Para transcripción real se necesita whisper.cpp y un modelo compatible instalado por separado.

## Funcionalidades, arquitectura y flujo de voz

```text
Micrófono / archivo → FastAPI → validar / convertir con ffmpeg
→ STT (simulado o whisper.cpp real)
→ reglas determinísticas o LLM externo opcional
→ herramienta permitida, parámetros Pydantic
→ texto → TTS del navegador o eSpeak local → audio
```

La entrada de texto se identifica como `typed`, sin pretender que fue reconocida por voz. En el STT demo el resultado lleva `simulated: true`.

Herramientas reales: `get_current_time` (zona horaria), `calculate` (aritmética limitada, sin ejecución de código), `create_note`, `list_notes` y `get_session_summary`. Hay validación de argumentos y una sola llamada por turno.

## Tecnologías y requisitos

Python 3.14 preferido (también CI con 3.12), FastAPI, Pydantic v2, httpx, pytest, Ruff, mypy, Docker, GitHub Actions. Para formatos WebM, OGG, MP3 y M4A se usa ffmpeg y WAV PCM16 mono de 16 kHz. El navegador requiere **localhost o HTTPS** y permiso explícito para el micrófono; no se graba automáticamente.

## Instalación y ejecución local

```bash
git clone https://github.com/RamonRDR/voice-ai-agent.git
cd voice-ai-agent
python -m venv .venv
# Activa el entorno virtual
python -m pip install -e ".[dev]"
cp .env.example .env
uvicorn voice_ai_agent.main:app --host 127.0.0.1 --port 8000
```

Web: http://127.0.0.1:8000. Documentación OpenAPI: http://127.0.0.1:8000/docs.

Demo con Docker y voz de eSpeak: `docker build -t voice-ai-agent .` y `docker run --rm -p 127.0.0.1:8000:8000 voice-ai-agent`.

## Configuración de STT, LLM y TTS

Por defecto, `.env.example` configura `VOICE_MODE=demo`, `VOICE_STT_BACKEND=demo`, `VOICE_LLM_BACKEND=rules`, `VOICE_TTS_BACKEND=browser`. No hay llamadas de pago.

Para usar reconocimiento real de voz, instala whisper.cpp y un modelo GGML y configura:

```dotenv
VOICE_MODE=local
VOICE_STT_BACKEND=whisper_cpp
VOICE_WHISPER_EXECUTABLE=/ruta/whisper-cli
VOICE_WHISPER_MODEL=/ruta/ggml-base.bin
VOICE_LLM_BACKEND=rules
VOICE_TTS_BACKEND=espeak
```

El reconocimiento es real, pero el diálogo sigue basado en reglas. Para respuestas **generadas por un LLM real**, usa `VOICE_MODE=remote`, `VOICE_LLM_BACKEND=openai_compatible`, `VOICE_LLM_ENDPOINT` HTTPS, `VOICE_LLM_MODEL` y `VOICE_LLM_API_KEY`. **Esta configuración puede generar cargos y enviar texto a terceros.** Solo se habilita por decisión explícita. Los idiomas prioritarios son inglés y portugués; español es opcional según el motor.

## Interfaz, micrófono y ejemplos

La interfaz permite grabar, detener, subir audio, enviar texto, elegir idioma, ver la transcripción, el historial, la herramienta ejecutada y los tiempos, cancelar y reproducir voz. La reproducción es manual.

Prueba `What time is it?`, `calculate 12*4`, `note: buy milk` y `list notes`. La entrada de audio en modo demo muestra que la transcripción es fija y simulada; el cuadro de texto sirve para probar herramientas sin usar STT.

```bash
curl -X POST http://127.0.0.1:8000/api/session
curl -X POST http://127.0.0.1:8000/api/turn/text \
  -H 'Content-Type: application/json' \
  -d '{"text":"calculate 12*4","language":"en"}'
curl -X POST http://127.0.0.1:8000/api/turn \
  -F 'audio=@ejemplo.wav' -F 'language=es'
```

La respuesta distingue `source` y `simulated`, e incluye herramienta, texto, WAV codificado en base64 si se usa eSpeak y métricas por etapa. El historial se consulta en `GET /api/history/{session_id}`. Para cancelar: `POST /api/cancel/{request_id}?session_id=...`.

## Pruebas, evaluaciones y CI

```bash
ruff check .
ruff format --check .
mypy src
pytest -q
python evaluations/run.py
python -m build
```

Incluye 20 escenarios determinísticos del **enrutador demo**, no mediciones del rendimiento de Whisper ni LLM externos. Las pruebas cubren la API, audio sintético, duración, silencio, errores, sesiones, herramientas, límites, seguridad y cancelación. GitHub Actions utiliza runners estándar, sin micrófono físico, servicios pagos, modelos pesados, autodespliegue o fusión automática. No existe WER medido sin transcripciones de referencia.

## Seguridad, privacidad y limitaciones

Se comprueban firmas, duración y tamaño del audio; la conversión se realiza sin shell arbitrario. Los archivos temporales se borran; el historial y las notas solo viven en memoria y expiran. No se guardan audios permanentemente ni secretos en el repositorio. No se integran cuentas personales ni se clonan voces. Consulta [SECURITY](docs/SECURITY.md).

**No está listo para publicarse como servicio abierto:** falta autenticación, control de abuso, límites por usuario, control de gasto y sesiones distribuidas. No hay streaming full-duplex, WebSockets, interrupción de voz en tiempo real ni modelo Whisper empaquetado. La demostración debe indicar claramente qué componentes son reales.

Licencia MIT © 2026 Ramon Rodriguez. Consulta [LICENSE](LICENSE); modelos y voces de terceros tienen sus propias licencias. Decisiones técnicas en [DECISIONS](docs/DECISIONS.md).
