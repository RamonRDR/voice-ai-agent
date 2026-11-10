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

> **Status do projeto:** MVP no [PR #1 em rascunho](https://github.com/RamonRDR/voice-ai-agent/pull/1), ainda não integrado à `main`. A **primeira revisão do Codex** identificou cinco apontamentos (um P1, quatro P2), todos tratados. A **segunda revisão** apontou mais dois P2 na interface (cancelamento tardio e retorno pelo histórico), também corrigidos com testes de regressão; a próxima revisão ainda não foi solicitada. A [execução de GitHub Actions na branch #42849121931](https://github.com/RamonRDR/voice-ai-agent/actions/runs/42849121931) aprovou **52/52 testes pytest por versão Python, 7/7 testes de estado do navegador, 20/20 avaliações determinísticas** e a síntese WAV real no Docker. Whisper real e LLM remoto ainda não foram validados com provedores externos.

## Visão geral

Agente de voz demonstrativo, **por turnos**, criado em Python e FastAPI para portfólio internacional. Inclui captura pelo navegador, upload validado, transcrição por adaptador STT, integração opcional com LLM, ferramentas controladas e resposta falada.

> **Transparência:** o modo demo padrão usa transcrição **simulada e identificada** e respostas **baseadas em regras**. As ferramentas realizam ações locais reais. Ao clicar em Reproduzir, o navegador faz síntese de voz real. No Docker, eSpeak produz áudio real. Para reconhecer fala de verdade, configure whisper.cpp com executável e modelo instalados separadamente.

## Funcionalidades implementadas

- Captura de microfone sob permissão, parada, upload, entrada de texto e reprodução manual; estados e cancelamento.
- Validação de WAV, WebM, OGG, MP3 e M4A com limite, conversão para PCM16 16 kHz, rejeição de silêncio e limpeza temporária.
- STT demo simulado, adaptador whisper.cpp real opcional, respostas por regras, LLM remoto opcional e TTS real no navegador ou eSpeak.
- Cinco ferramentas locais validadas, sessões efêmeras, histórico limitado, métricas por etapa e endpoints OpenAPI.
- 52 testes pytest, 20 avaliações determinísticas, GitHub Actions e documentação trilíngue.

## Tecnologias

O Docker e a CI usam Python **3.14**; a CI também testa **3.12** (`requires-python >=3.12`). As versões são **intervalos declarados**, não versões fixadas: FastAPI `>=0.115,<1`, Uvicorn `>=0.32,<1`, Pydantic `>=2.10,<3`, Pydantic Settings `>=2.6,<3`, httpx `>=0.28,<1` e python-multipart `>=0.0.20,<1`. A interface usa HTML/JavaScript sem framework, MediaRecorder e SpeechSynthesis. O Docker instala FFmpeg e eSpeak-NG. Qualidade e automação: pytest, pytest-asyncio, Ruff, mypy, empacotamento Python e GitHub Actions.

**Limites das integrações de IA:** o modo padrão simula STT e usa regras; o adaptador whisper.cpp permite transcrição real, porém **não foi validado com um modelo na CI**. O LLM compatível com OpenAI por HTTPS é opcional e **não foi validado com provedor real**. A saída eSpeak WAV **foi validada** no teste real Docker. As cinco ferramentas locais são executadas com validação Pydantic. Não há banco de dados, Redis, Docker Compose, autenticação, deploy público, RAG ou MCP.

## Arquitetura e pipeline de voz

```text
Microfone / upload → FastAPI → validação / ffmpeg
→ STT (demo simulado ou whisper.cpp real)
→ regras (demo) ou LLM remoto opcional
→ ferramentas validadas (Pydantic) → resposta textual
→ TTS (SpeechSynthesis do navegador ou eSpeak)
→ reprodução + tempos e histórico limitado
```

A entrada digitada passa diretamente ao processamento textual e aparece como `source: typed`, sem fingir transcrição. O STT simulado retorna frase predefinida com `simulated: true`.

Ferramentas: `get_current_time` (fuso configurável), `calculate` (aritmética segura, sem `eval`), `create_note` e `list_notes` (anotações efêmeras por sessão), `get_session_summary` (resumo simples do histórico). Chamadas e argumentos ficam restritos a uma lista fixa.

## Estrutura do repositório

| Caminho | Responsabilidade |
|---|---|
| `src/voice_ai_agent/main.py` | FastAPI, rotas, saúde, OpenAPI e interface estática |
| `audio.py`, `providers.py` | Validação, ffmpeg e adaptadores STT/LLM/TTS |
| `pipeline.py`, `sessions.py` | Orquestração, cancelamento e estado limitado |
| `tools.py`, `schemas.py`, `config.py` | Ferramentas autorizadas, modelos Pydantic e configurações |
| `static/index.html`, `prompts/system_v1.txt` | Interface e instruções versionadas do LLM |
| `tests/`, `evaluations/` | Testes com áudio sintético e cenários determinísticos |
| `.github/workflows/ci.yml`, `Dockerfile` | GitHub Actions e teste real do contêiner |

## Pré-requisitos

Python 3.14 preferido, FastAPI, Pydantic v2, httpx, pytest, Ruff, mypy, Docker e GitHub Actions. CI também testa Python 3.12. ffmpeg é necessário para converter formatos WebM, OGG, MP3 e M4A para WAV PCM16 mono 16 kHz. WAV compatível funciona sem conversão. O navegador precisa de **localhost ou HTTPS** e permissão de microfone. A captura nunca começa automaticamente.

## Instalação e execução local

```bash
git clone https://github.com/RamonRDR/voice-ai-agent.git
cd voice-ai-agent
python -m venv .venv
# Ative o ambiente virtual
python -m pip install -e ".[dev]"
cp .env.example .env
uvicorn voice_ai_agent.main:app --host 127.0.0.1 --port 8000
```

Interface: http://127.0.0.1:8000. OpenAPI: http://127.0.0.1:8000/docs.

Demo via Docker com TTS local eSpeak: `docker build -t voice-ai-agent .` e `docker run --rm -p 127.0.0.1:8000:8000 voice-ai-agent`.

## Configurações: STT, LLM e TTS

O `.env.example` usa `VOICE_MODE=demo`, `VOICE_STT_BACKEND=demo`, `VOICE_LLM_BACKEND=rules` e `VOICE_TTS_BACKEND=browser`. Nenhum serviço pago é chamado.

| Variável | Padrão do exemplo | Observação |
|---|---|---|
| `VOICE_MODE` | `demo` | Alternativas: `local` e `remote` |
| `VOICE_STT_BACKEND` | `demo` | `whisper_cpp` exige executável e modelo instalados |
| `VOICE_LLM_BACKEND` | `rules` | `openai_compatible` só no modo `remote` com autorização/custos |
| `VOICE_TTS_BACKEND` | `browser` | `espeak` gera WAV local |
| `VOICE_MAX_UPLOAD_BYTES` | `8388608` (8 MiB) | Limite da carga de áudio |
| `VOICE_MAX_AUDIO_SECONDS` | `30` | Duração permitida |
| `VOICE_MAX_HISTORY` | `12` | Mensagens retidas no histórico |
| `VOICE_SESSION_TTL_SECONDS` | `1800` (30 min) | Expiração da sessão em memória |
| `VOICE_PROCESS_TIMEOUT_SECONDS` | `90` | Limite de tempo de processamento |
| `VOICE_TIMEZONE` | `America/Sao_Paulo` | Fuso no exemplo; padrão interno UTC |

Para transcrição real (Whisper local), instale whisper.cpp e um modelo GGML compatível e configure:

```dotenv
VOICE_MODE=local
VOICE_STT_BACKEND=whisper_cpp
VOICE_WHISPER_EXECUTABLE=/caminho/whisper-cli
VOICE_WHISPER_MODEL=/caminho/ggml-base.bin
VOICE_LLM_BACKEND=rules
VOICE_TTS_BACKEND=espeak
```

Esse modo executa **STT real**, mas ainda utiliza respostas baseadas em regras. Para um **LLM generativo real**, utilize `VOICE_MODE=remote`, `VOICE_LLM_BACKEND=openai_compatible`, além de `VOICE_LLM_ENDPOINT` HTTPS, `VOICE_LLM_MODEL` e `VOICE_LLM_API_KEY`. É uma opção que **pode gerar custos e enviar texto/histórico a terceiros**. Não será ativada por padrão. Inglês e português são prioridade; espanhol é uma seleção adicional sujeita à capacidade dos motores.

## Referência da API

| Método | Rota | Finalidade |
|---|---|---|
| `GET` | `/` | Interface web de demonstração |
| `GET` | `/health` | Saúde da API |
| `GET` | `/docs`, `/openapi.json` | OpenAPI interativo e legível por máquina |
| `GET` | `/api/config` | Modo de provedores e aviso de demonstração |
| `POST` | `/api/session` | Criar sessão temporária |
| `POST` | `/api/turn` | Upload de áudio, STT e pipeline de resposta |
| `POST` | `/api/turn/text` | Entrada digitada; não executa STT |
| `GET` | `/api/history/{session_id}` | Histórico limitado de conversa |
| `POST` | `/api/cancel/{request_id}` | Tentativa de cancelar com session_id na consulta |

## Interface, microfone e exemplos

Na interface responsiva há botão de gravar, parar, enviar arquivo, entrada digitada, seleção de idioma, transcrição, histórico, estado da operação, cancelamento, execução de ferramenta, métricas e reprodução de áudio. Áudio nunca é reproduzido automaticamente.

Experimente `What time is it?`, `calculate 12*4`, `note: buy milk` e `list notes`. O modo demo de **áudio** usa pergunta fixa e informará que a transcrição foi simulada. O campo de texto permite testar outras ferramentas sem STT.

```bash
curl -X POST http://127.0.0.1:8000/api/session
curl -X POST http://127.0.0.1:8000/api/turn/text \
  -H 'Content-Type: application/json' \
  -d '{"text":"calculate 12*4","language":"en"}'
curl -X POST http://127.0.0.1:8000/api/turn \
  -F 'audio=@exemplo.wav' -F 'language=pt'
```

A resposta informa `source`, `simulated`, tool, texto, áudio WAV em base64 quando disponível e tempos de STT, LLM, ferramentas, TTS e total. O histórico pode ser consultado com `GET /api/history/{session_id}`; cancelamento usa `POST /api/cancel/{request_id}?session_id=...`.

## Testes, avaliações e GitHub Actions

```bash
ruff check .
ruff format --check .
mypy src
pytest -q
python evaluations/run.py
node --test tests/browser_state.test.cjs
python -m build
```

Há 20 cenários de avaliação **determinística do roteador demo**, não benchmarks de Whisper ou LLM real. Testes incluem API, uploads, silêncio, limites, sessões, isolamento, ferramentas, injeção de prompt simulada, cancelamento e falhas. Os áudios de teste são sintéticos. Sete testes Node.js verificam o bloqueio de operações concorrentes, a limpeza do microfone, o envio único, o isolamento do cancelamento e a restauração após navegação pelo histórico, sem substituir uma validação manual em navegador real. A CI usa runners hospedados do GitHub, sem microfone físico, modelos grandes, APIs pagas ou computador pessoal. Não executa deploy ou merge automático. WER só deve ser medido com transcrições de referência reais, não foi inventado.

## Evidências dos badges e manutenção

O badge `pytest | 52 passing` é um **registro estático** da [execução do GitHub Actions na branch #42849121931](https://github.com/RamonRDR/voice-ai-agent/actions/runs/42849121931) na branch `feat/voice-ai-agent-mvp`: **52 aprovados, 0 falhas, 0 ignorados e 1 aviso não bloqueante de dependência de terceiros** em cada versão Python. O badge **20/20** refere-se apenas à avaliação determinística do roteador demo, não à precisão de fala ou a benchmarks do LLM. Ruff lint/format, mypy, sintaxe JS, **7/7 testes de estado do navegador com Node.js**, empacotamento wheel/sdist, Docker e teste WAV real com eSpeak foram aprovados. Não há cobertura percentual medida.

O badge dinâmico de CI aponta para a **branch de desenvolvimento** porque a `main` ainda contém somente os arquivos iniciais. Após eventual merge autorizado, altere a seleção para `main` nos **três READMEs** e confira a CI nessa branch. Sempre que testes mudarem, consulte os jobs **Pytest**, **Test browser state** e **Deterministic evaluation** aprovados, atualize as contagens estáticas nas três traduções por PR revisado e atualize o [inventário de evidências](docs/BADGES.md). Nunca atualize os badges a partir de testes com falha ou execução incompleta.

## Segurança e privacidade

Validação de conteúdo e duração de áudio, subprocessos sem shell, restrições de ferramentas, mensagens limitadas, histórico somente em memória com expiração, arquivos temporários removidos após cada solicitação, logs técnicos sem conteúdo sensível e credenciais somente por ambiente. Gravação requer permissão. Não integramos contas pessoais nem clonamos vozes. Ver [segurança](docs/SECURITY.md).

**Não exponha a aplicação publicamente:** este MVP local não tem autenticação, controle de abuso público, persistência distribuída ou isolamento multiusuário. Para produção, seria preciso acrescentar autenticação, limites por usuário, orçamento para APIs, proteção de sessões, monitoramento e revisão de segurança.

## Limitações conhecidas e próximas evoluções

Não há streaming full-duplex, WebSockets nem interrupção de fala em tempo real. whisper.cpp e o modelo devem ser instalados separadamente; vozes e codecs variam conforme ambiente. Sessões são locais e efêmeras. Demonstre sempre o modo utilizado; não há vídeo, captura de tela ou deploy alegado sem evidência. Documentação de decisões em [docs/DECISIONS.md](docs/DECISIONS.md).

Próximas evoluções opcionais: validar o reconhecimento real do Whisper em ambiente adequado, avaliar WER com transcrições de referência, evoluir para streaming e autenticação antes de qualquer publicação. Veja o [roteiro de demonstração](docs/DEMO.md) e as [decisões técnicas](docs/DECISIONS.md).

## Contribuições

Contribuições e relatos de problemas podem ser propostos por PR revisado. Não adicione gravações pessoais, credenciais ou pesos de modelos; preserve testes determinísticos, transparência sobre simulações e merges somente mediante autorização.

## Licença

MIT © 2026 Ramon Rodriguez; consulte [LICENSE](LICENSE). Bibliotecas, modelos e vozes de terceiros seguem suas próprias licenças.
