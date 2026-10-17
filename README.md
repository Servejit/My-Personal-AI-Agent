# My Personal AI Agent

A free-first Streamlit personal assistant with separate task apps and a local-first architecture. The root `app.py` launches the task menu; shared helpers live in `core/services.py`.

## Run the app

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Suno-style local music studio

`tasks/ai_music_studio/app.py` provides a Suno-style creation interface with song descriptions, genre/mood, vocal arrangement, language, duration, BPM, lyrics input, seed, MP3 playback and download. It is designed to send generation requests only to a local ACE-Step server at `http://127.0.0.1:8001`. It blocks remote generation hosts; it does not call Suno, Gemini, or hosted Hugging Face inference.

To install the local music engine on a suitable computer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/ace-step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync
uv run acestep-api
```

Start the engine and leave it running on port 8001. On first start, model weights are downloaded once; inference then runs locally. Full music generation needs significant disk space and compute. Free GitHub Codespaces may not have sufficient GPU/RAM and may be unsuitable for full-length music.

Official project and hardware guidance: https://github.com/ace-step/ACE-Step-1.5

## Local AI (no Gemini API required)

External AI services are disabled by default. For local text generation, download a suitable GGUF instruct model, install `requirements-local.txt`, and set `LOCAL_MODEL_PATH`. Follow [LOCAL_AI.md](LOCAL_AI.md). Model weights are not committed to GitHub.

## Tasks

- `tasks/chat/app.py` — assistant chat and poster-by-command workflow.
- `tasks/ai_music_studio/app.py` — local-first Suno-style music studio.
- `tasks/punjabi_song_generator/app.py` — offline Punjabi lyric writer.
- `tasks/file_analyst/app.py` — local CSV/Excel analysis.
- `tasks/calculator/app.py` — safe arithmetic calculator.
- `tasks/notes_tasks/app.py` — local saved notes and tasks.
- `tasks/poster_maker/app.py` — local designed graphic poster generation.
- `tasks/settings/app.py` — environment and privacy information.

## Honest capability limits

Python code provides the UI and workflow, but music generation requires a specialist music model. ACE-Step is an open-source option that can run locally; hardware support and speed vary. The offline lyric starter is template-based rather than a full language model. Poster Maker creates typography/shape-based PNG graphics locally and does not create photorealistic artwork.
