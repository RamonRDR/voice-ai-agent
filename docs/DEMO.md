# Demo walkthrough (not evidence of a completed real-model run)

1. Install the project, start FastAPI and open http://127.0.0.1:8000.
2. Confirm the mode badge reads \`DEMO · STT demo · LLM rules\` and the disclosure clearly says speech recognition is scripted.
3. Click **Send text** with \`calculate 12*4\`; verify the \`calculate\` tool reports 48.
4. Enter \`note: buy milk\`, then \`list notes\` and verify the note exists only in this session.
5. Press **Play latest reply**. On compatible browsers this uses native speechSynthesis.
6. Upload a generated synthetic WAV or record a brief sample. The displayed transcript must be labeled **[scripted STT demo]**, not recognized speech.
7. Upload an empty, unsupported or silent WAV and confirm a safe error.
8. Change to actual local STT only after installing whisper.cpp and a GGML model as documented; label the real mode in any screenshot or video.
9. With eSpeak installed, set \`VOICE_TTS_BACKEND=espeak\` for server-generated WAV and test replay.
10. Collect screenshots or video only from an actual running instance and do not imply a validated real Whisper benchmark without a documented test environment.

For a scripted-routing smoke suite, run \`python evaluations/run.py\`. Its results are **not** inference speed, WER, or speech quality benchmarks.
