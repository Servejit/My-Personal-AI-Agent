# My Personal AI Agent

A free-first Streamlit personal assistant with Gemini-powered chat, direct sung-MP3 requests from Chat, an AI Music Studio, and a Punjabi Song Generator, plus a safe calculator, CSV/Excel analysis, and notes/tasks. Gemini requires your own API key stored securely as a Codespaces secret.

## Run in GitHub Codespaces

1. Open this repository in a Codespace.
2. Wait for the Python environment to be ready.
3. In VS Code, open **Terminal → Run Task…**.
4. Choose **Run Personal AI Agent**. The task installs `requirements.txt` and starts Streamlit on port 8501.
5. When Codespaces offers to open port 8501, choose **Open in Browser**.

If the task is not listed, use the Codespaces terminal and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Connect the language model

1. Open [Google AI Studio API keys](https://aistudio.google.com/apikey) and create an API key if the Gemini API free tier is available to your account.
2. In your GitHub Codespace, open the **Secrets** panel (usually the key icon in the left sidebar) and add a secret named `GEMINI_API_KEY` with the API key as its value.
3. Restart the Streamlit process. If `st.secrets` or environment variables do not refresh, stop and restart the Codespace app.
4. Open **Punjabi Song Generator** or **Chat**. Choose Gurmukhi Punjabi or Roman Punjabi and generate lyrics.

The Gemini API has limited free-tier access for eligible models/accounts; quotas and terms can change. Check [official Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) before use. Do not commit API keys to GitHub or paste them into chat. Requests are sent to Google for generation, so do not send sensitive information.

## Features

- Gemini-powered chat and original Punjabi song lyrics (requires `GEMINI_API_KEY`).
- Ask for a sung MP3 directly in **Chat**: the app writes Punjabi lyrics, requests a sung track with instrumental accompaniment, and shows an audio player plus MP3 download when generation succeeds.
- **Generate a poster directly from Chat:** type a command such as `Create a ruby-red poster for my cardamom brand, with the headline Fresh Green Cardamom and a premium glossy style`. The agent prepares poster copy and creates a real PNG image in the app, with a preview and **Download generated poster (PNG)** button. The poster renderer runs locally with Pillow; Gemini helps format the content when configured.
- AI Music Studio and Punjabi Song Generator remain available for more control over language, style, lyrics, and duration.
- Safe arithmetic calculator (does not execute arbitrary Python).
- CSV and Excel spreadsheet previews and summaries.
- Notes and tasks saved in `data/notes.json` in the working environment.
- **Poster Maker task:** turn pasted content or a recent Chat message into a styled portrait or square PNG poster, with a headline, subtitle, colour theme, and optional call to action. Poster rendering is local with Pillow and does not require a paid image-generation API.
- Confirmation before deleting notes or clearing chat history.

## Add future tasks without editing the main app

The app supports independent task plugins in the `tasks/` folder. To add a task, copy `tasks/_template.py` to a new Python file (for example, `tasks/weather_task.py`), set a unique `TASK_NAME`, optionally set `TASK_ICON`, and implement its `render()` function. The task will appear automatically in the Workspace sidebar after the app reloads. Read [tasks/README.md](tasks/README.md) for the full instructions.

Keep widget keys, session-state keys, files, and outputs namespaced to each task. Plugin code shares the same Python process and machine resources, so this improves organization and limits ordinary UI errors but is not a security sandbox.

## Privacy and limitations

- No paid AI API is required for the built-in tools.
- AI generation requires a valid `GEMINI_API_KEY` and internet access.
- Do not upload sensitive files to a publicly accessible deployment.
- Codespaces and hosted environments may not preserve local note files after a rebuild or restart. Download or back up important notes.

## Model and cost notes

The app uses the Gemini API model configured in `app.py` for lyrics and chat. The API has a limited free tier for eligible accounts, but availability and quotas can change. The app does not intentionally fall back to paid models if the request fails.

Sung MP3 generation uses the public open-source [ACE-Step v1.5 Hugging Face Space](https://huggingface.co/spaces/ACE-Step/Ace-Step-v1.5) HTTP API. It does not require a paid API key, but public demos can sleep, queue, change their API, or become unavailable. This is a best-effort free option, not a guaranteed service. If it fails, open the linked demo directly and use its Lyrics and Generate controls.
