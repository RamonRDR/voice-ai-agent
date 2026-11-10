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

![pytest: 37 passing](https://img.shields.io/badge/pytest-37%20passing-0A9EDC)
![pytest asyncio: async tests](https://img.shields.io/badge/pytest%20asyncio-async%20tests-0A9EDC)
![Ruff: lint & format](https://img.shields.io/badge/Ruff-lint%20%26%20format-D7FF64)
![mypy: type checked](https://img.shields.io/badge/mypy-type%20checked-2A6DB4)
![Offline evaluation: 20 of 20 scripted](https://img.shields.io/badge/Offline%20evaluation-20%20of%2020%20scripted-6F42C1)
![OpenAPI: documented](https://img.shields.io/badge/OpenAPI-documented-6BA539)
![JS syntax: checked](https://img.shields.io/badge/JS%20syntax-checked-F7DF1E)
![Python build: wheel & sdist](https://img.shields.io/badge/Python%20build-wheel%20%26%20sdist-6B7280)
![Docker smoke: eSpeak WAV](https://img.shields.io/badge/Docker%20smoke-eSpeak%20WAV-2496ED)

</div>

> **Estado del proyecto:** MVP implementado en el [PR #1 en borrador](https://github.com/RamonRDR/voice-ai-agent/pull/1), todavía no fusionado con `main`. La [ejecución de GitHub Actions del PR](https://github.com/RamonRDR/voice-ai-agent/actions/runs/42485463114) aprobó 37/37 pruebas pytest, 20/20 evaluaciones determinísticas del modo demo, síntesis WAV en Docker y controles de calidad. **Todavía no se solicitó revisión de Codex.** Whisper real y el LLM remoto no han sido validados con proveedores reales.

## Visión general

Agente conversacional por voz **por turnos**, desarrollado en Python y FastAPI como demostración técnica. Incluye grabación en navegador, carga validada, transcripción STT, integración opcional con LLM, herramientas seguras y respuestas habladas.

> **Modo demo transparente:** STT **simulado** con etiqueta visible, respuestas **predefinidas**, pero operaciones de herramientas locales reales. El navegador realiza síntesis de voz real al pulsar Reproducir. Docker instala eSpeak para TTS real. Para transcripción real se necesita whisper.cpp y un modelo compatible instalado por separado.

## Funcionalidades implementadas

- Grabación con permiso, detener, cargar archivos, entrada escrita y reproducción manual; estados y cancelación.
- Validación de WAV, WebM, OGG, MP3 y M4A con límites, conversión PCM16 16 kHz, detección de silencio y limpieza temporal.
- STT simulado en demo, adaptador whisper.cpp opcional, respuestas por reglas, LLM remoto opcional y TTS real del navegador o eSpeak.
- Cinco herramientas locales validadas, sesiones efímeras, historial limitado, tiempos por etapa y OpenAPI.
- 37 pruebas pytest, 20 evaluaciones determinísticas, GitHub Actions y documentación en tres idiomas.

## Pila tecnológica

Docker y CI usan Python **3.14**; CI también prueba **3.12** (`requires-python >=3.12`). Las versiones son **rangos declarados**, no instalaciones fijadas: FastAPI `>=0.115,<1`, Uvicorn `>=0.32,<1`, Pydantic `>=2.10,<3`, Pydantic Settings `>=2.6,<3`, httpx `>=0.28,<1` y python-multipart `>=0.0.20,<1`. La interfaz usa HTML/JavaScript sin framework, MediaRecorder y SpeechSynthesis. Docker instala FFmpeg y eSpeak-NG. Calidad: pytest, pytest-asyncio, Ruff, mypy, empaquetado Python y GitHub Actions.

**Límites de IA:** la demo simula STT y usa reglas; whisper.cpp ofrece un adaptador de transcripción real, **no validado con modelo en CI**. El LLM HTTPS compatible con OpenAI es opcional y **no está validado con un proveedor real**. La salida WAV de eSpeak **sí fue verificada** en una prueba Docker real. Las cinco herramientas locales usan validación Pydantic. No existen base de datos, Redis, Docker Compose, autenticación, despliegue público, RAG ni MCP.

## Arquitectura y flujo de voz

```text
Micrófono / archivo → FastAPI → validar / convertir con ffmpeg
→ STT (simulado o whisper.cpp real)
→ reglas determinísticas o LLM externo opcional
→ herramienta permitida, parámetros Pydantic
→ texto → TTS del navegador o eSpeak local → audio
```

La entrada de texto se identifica como `typed`, sin pretender que fue reconocida por voz. En el STT demo el resultado lleva `simulated: true`.

Herramientas reales: `get_current_time` (zona horaria), `calculate` (aritmética limitada, sin ejecución de código), `create_note`, `list_notes` y `get_session_summary`. Hay validación de argumentos y una sola llamada por turno.

## Requisitos previos

Python 3.14 preferido (también CI con 3.12), FastAPI, Pydantic v2, httpx, pytest, Ruff, mypy, Docker, GitHub Actions. Para formatos WebM, OGG, MP3 y M4A se usa ffmpeg y WAV PCM16 mono de 16 kHz. El navegador requiere **localhost o HTTPS** y permiso explícito para el micrófono; no se graba automáticamente.

## Estructura del repositorio

| Ruta | Responsabilidad |
|---|---|
| `src/voice_ai_agent/main.py` | FastAPI, rutas, estado, OpenAPI e interfaz estática |
| `audio.py`, `providers.py` | Validación, ffmpeg y adaptadores STT/LLM/TTS |
| `pipeline.py`, `sessions.py` | Orquestación, cancelación y estado limitado |
| `tools.py`, `schemas.py`, `config.py` | Herramientas permitidas, modelos Pydantic y configuración |
| `static/index.html`, `prompts/system_v1.txt` | Interfaz e instrucciones LLM versionadas |
| `tests/`, `evaluations/` | Pruebas de audio sintético y evaluaciones determinísticas |
| `.github/workflows/ci.yml`, `Dockerfile` | GitHub Actions y prueba real del contenedor |

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

## Referencia de la API

| Método | Ruta | Objetivo |
|---|---|---|
| `GET` | `/` | Interfaz web de demostración |
| `GET` | `/health` | Estado de la API |
| `GET` | `/docs`, `/openapi.json` | OpenAPI interactivo y legible por máquina |
| `GET` | `/api/config` | Modo de proveedores y aviso de demostración |
| `POST` | `/api/session` | Crear sesión temporal |
| `POST` | `/api/turn` | Carga de audio, STT y flujo de respuesta |
| `POST` | `/api/turn/text` | Entrada escrita; no ejecuta STT |
| `GET` | `/api/history/{session_id}` | Historial limitado de conversaciones |
| `POST` | `/api/cancel/{request_id}` | Intento de cancelar con session_id en la consulta |

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

## Evidencias de los badges y mantenimiento

El badge `pytest | 37 passing` es una **instantánea estática** de la [ejecución GitHub Actions #42485463114 del PR](https://github.com/RamonRDR/voice-ai-agent/actions/runs/42485463114) en `feat/voice-ai-agent-mvp`: **37 aprobadas, 0 fallidas, 0 omitidas y 1 aviso no bloqueante de una dependencia externa** en cada versión Python. El badge **20/20** se refiere únicamente a la evaluación determinística del enrutador demo, no a la precisión de voz ni a benchmarks de LLM. Ruff lint/format, mypy, sintaxis JS, paquetes wheel/sdist, Docker y la prueba real WAV de eSpeak fueron aprobados. No se afirma ningún porcentaje de cobertura.

El badge dinámico de CI sigue la **rama de desarrollo** porque `main` todavía contiene los archivos iniciales. Después de una fusión autorizada, cambia la rama a `main` en **los tres READMEs** y verifica CI allí. Cuando cambien los casos de prueba, consulta los jobs aprobados **Pytest** y **Deterministic evaluation**, actualiza los recuentos estáticos en los tres idiomas mediante PR revisado y actualiza el [inventario de evidencias](docs/BADGES.md). No uses ejecuciones fallidas o incompletas para actualizar badges.

## Seguridad y privacidad

Se comprueban firmas, duración y tamaño del audio; la conversión se realiza sin shell arbitrario. Los archivos temporales se borran; el historial y las notas solo viven en memoria y expiran. No se guardan audios permanentemente ni secretos en el repositorio. No se integran cuentas personales ni se clonan voces. Consulta [SECURITY](docs/SECURITY.md).

**No está listo para publicarse como servicio abierto:** falta autenticación, control de abuso, límites por usuario, control de gasto y sesiones distribuidas. No hay streaming full-duplex, WebSockets, interrupción de voz en tiempo real ni modelo Whisper empaquetado. La demostración debe indicar claramente qué componentes son reales.

## Limitaciones conocidas y próximas mejoras

No hay streaming full-duplex, WebSockets, interrupción de voz en tiempo real ni modelo Whisper incluido. Las voces y códecs dependen del entorno. Las sesiones son efímeras, en memoria y de una sola instancia. La cancelación es cooperativa. No hay servicio público ni capturas o métricas de reconocimiento real verificadas. Mejoras opcionales: validar Whisper con un modelo y transcripciones de referencia, medir WER y considerar streaming y autenticación antes del despliegue. Consulta [DEMO](docs/DEMO.md) y [DECISIONS](docs/DECISIONS.md).

## Contribuciones

Se aceptan propuestas mediante un PR revisado. No agregues audios personales, secretos ni pesos grandes; conserva pruebas determinísticas y etiquetas claras de funciones simuladas. Las fusiones requieren autorización explícita.

## Licencia

MIT © 2026 Ramon Rodriguez. Consulta [LICENSE](LICENSE); los modelos, bibliotecas y voces de terceros conservan sus propias licencias.
