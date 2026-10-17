# My Personal AI Agent

A free-first Streamlit personal assistant with **separate app.py files for each task**. The root `app.py` is a lightweight launcher; each task has its own UI module, while shared reusable Python functions live in `core/services.py`.

## Run in GitHub Codespaces

1. Open this repository in a Codespace.
2. Open **Terminal → Run Task…** and choose **Run Personal AI Agent**.
3. If the task is not listed, run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Configure Gemini (optional)

Create a key at [Google AI Studio](https://aistudio.google.com/apikey) if the free tier is available to your account. Add it to Codespaces secrets as `GEMINI_API_KEY`, then restart Streamlit. Never commit API keys or paste them into chat. AI requests are sent to Google; do not send sensitive information.

## Task structure

- `app.py` — launcher and task navigation only.
- `core/services.py` — shared AI, audio, calculator, notes, and file-analysis helpers.
- `tasks/chat/app.py` — assistant chat, poster-by-command and sung-MP3 requests.
- `tasks/ai_music_studio/app.py` — song idea, lyrics, style, and MP3 workflow.
- `tasks/punjabi_song_generator/app.py` — Punjabi lyrics and optional sung MP3.
- `tasks/file_analyst/app.py` — CSV/Excel analysis.
- `tasks/calculator/app.py` — safe arithmetic calculator.
- `tasks/notes_tasks/app.py` — saved notes and tasks.
- `tasks/settings/app.py` — privacy, environment, and model setup.
- `tasks/poster_maker/app.py` — independent Poster Maker task UI.
- `tasks/_poster_renderer.py` — private shared implementation used by Poster Maker and Chat.

Every built-in task is loaded from its own `tasks/<task_name>/app.py`. Add a folder containing an `app.py` with a `render()` function to add a task. See [tasks/README.md](tasks/README.md).

## Features and limitations

- Gemini-powered chat and original Punjabi song lyrics (requires your own key and eligible API access).
- Chat can create a locally rendered PNG poster from a command using Pillow; it creates designed typography/shape graphics, not photorealistic AI artwork.
- AI Music Studio and Punjabi Song Generator use the public ACE-Step hosted demo for best-effort sung MP3 generation. The free public endpoint can change, sleep, or be unavailable; MP3 generation is not guaranteed.
- CSV and Excel previews, summaries, and download.
- Safe arithmetic (does not execute arbitrary Python).
- Notes/tasks stored locally in `data/notes.json`; hosted environments may not preserve local files across rebuilds.
- Deleting notes and clearing chat history require confirmation.

## Dependencies

All built-in tasks use the root `requirements.txt`. Keep dependencies centralized so a clean Codespace installs everything with one command. Do not install paid API SDKs or commit secrets.
