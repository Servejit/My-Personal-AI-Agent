# My Personal AI Agent

A free-first Streamlit personal assistant with **separate app.py files for each task** and a **local-first AI architecture**. The root `app.py` is a launcher; shared reusable functions live in `core/services.py`, and optional offline text inference is in `core/local_ai.py`.

## Run in GitHub Codespaces

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Local AI (no Gemini API required)

External AI services are disabled by default. To run text generation locally, download a suitable GGUF instruct model, install `requirements-local.txt`, and set `LOCAL_MODEL_PATH` to the model file. Follow [LOCAL_AI.md](LOCAL_AI.md). Model weights are not committed to this repository. Small models run more slowly and may be less capable.

## Tasks

- `tasks/chat/app.py` — assistant chat, poster-by-command and sung-MP3 workflow.
- `tasks/ai_music_studio/app.py` — song idea, lyrics, style, and MP3 workflow.
- `tasks/punjabi_song_generator/app.py` — Punjabi lyrics and optional sung MP3.
- `tasks/file_analyst/app.py` — local CSV/Excel analysis.
- `tasks/calculator/app.py` — safe arithmetic calculator.
- `tasks/notes_tasks/app.py` — local saved notes and tasks.
- `tasks/poster_maker/app.py` — local designed graphic poster generation.
- `tasks/settings/app.py` — environment and privacy information.

## Honest capability limits

A local language model can handle text, brainstorming, and lyric writing. It is not automatically an image or music model. Poster Maker creates typography/shape-based PNG graphics locally. The sung-MP3 feature currently uses a hosted ACE-Step service and is disabled unless `ALLOW_EXTERNAL_AI=true`; high-quality singing or photorealistic image generation needs specialist models and substantial hardware. See [LOCAL_AI.md](LOCAL_AI.md).
