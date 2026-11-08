# Voice AI Agent

[English](README.md) | **Português** | [Español](README.es.md)

Agente de voz demonstrativo, **por turnos**, criado em Python e FastAPI para portfólio internacional. Inclui captura pelo navegador, upload validado, transcrição por adaptador STT, integração opcional com LLM, ferramentas controladas e resposta falada.

> **Transparência:** o modo demo padrão usa transcrição **simulada e identificada** e respostas **baseadas em regras**. As ferramentas realizam ações locais reais. Ao clicar em Reproduzir, o navegador faz síntese de voz real. No Docker, eSpeak produz áudio real. Para reconhecer fala de verdade, configure whisper.cpp com executável e modelo instalados separadamente.

## Recursos, arquitetura e pipeline

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

## Tecnologias e requisitos

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
python -m build
```

Há 20 cenários de avaliação **determinística do roteador demo**, não benchmarks de Whisper ou LLM real. Testes incluem API, uploads, silêncio, limites, sessões, isolamento, ferramentas, injeção de prompt simulada, cancelamento e falhas. Os áudios de teste são sintéticos. A CI usa runners hospedados do GitHub, sem microfone físico, modelos grandes, APIs pagas ou computador pessoal. Não executa deploy ou merge automático. WER só deve ser medido com transcrições de referência reais, não foi inventado.

## Segurança e privacidade

Validação de conteúdo e duração de áudio, subprocessos sem shell, restrições de ferramentas, mensagens limitadas, histórico somente em memória com expiração, arquivos temporários removidos após cada solicitação, logs técnicos sem conteúdo sensível e credenciais somente por ambiente. Gravação requer permissão. Não integramos contas pessoais nem clonamos vozes. Ver [segurança](docs/SECURITY.md).

**Não exponha a aplicação publicamente:** este MVP local não tem autenticação, controle de abuso público, persistência distribuída ou isolamento multiusuário. Para produção, seria preciso acrescentar autenticação, limites por usuário, orçamento para APIs, proteção de sessões, monitoramento e revisão de segurança.

## Limitações, demonstração e licença

Não há streaming full-duplex, WebSockets nem interrupção de fala em tempo real. whisper.cpp e o modelo devem ser instalados separadamente; vozes e codecs variam conforme ambiente. Sessões são locais e efêmeras. Demonstre sempre o modo utilizado; não há vídeo, captura de tela ou deploy alegado sem evidência. Documentação de decisões em [docs/DECISIONS.md](docs/DECISIONS.md).

MIT © 2026 Ramon Rodriguez, consulte [LICENSE](LICENSE). Bibliotecas, modelos e vozes de terceiros seguem suas próprias licenças.
