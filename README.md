# My Personal AI Agent

A free-first Streamlit personal assistant with Gemini-powered chat and a Punjabi Song Generator, plus a safe calculator, CSV/Excel analysis, and notes/tasks. Gemini requires your own API key stored securely as a Codespaces secret.

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
- Optional sung Punjabi MP3 generation through the public ACE-Step Hugging Face demo; uses generated lyrics, style selection, and an approximate duration, then provides an MP3 download.
- Safe arithmetic calculator (does not execute arbitrary Python).
- CSV and Excel spreadsheet previews and summaries.
- Notes and tasks saved in `data/notes.json` in the working environment.
- Confirmation before deleting notes or clearing chat history.

## Privacy and limitations

- No paid AI API is required for the built-in tools.
- AI generation requires a valid `GEMINI_API_KEY` and internet access.
- Do not upload sensitive files to a publicly accessible deployment.
- Codespaces and hosted environments may not preserve local note files after a rebuild or restart. Download or back up important notes.

## Model and cost notes

The app uses the Gemini API model configured in `app.py` for lyrics and chat. The API has a limited free tier for eligible accounts, but availability and quotas can change. The app does not intentionally fall back to paid models if the request fails.

Sung MP3 generation uses the public open-source [ACE-Step v1.5 Hugging Face Space](https://huggingface.co/spaces/ACE-Step/Ace-Step-v1.5) via `gradio_client`. It does not require a paid API key, but public demos can sleep, queue, change their API, or become unavailable. This is a best-effort free option, not a guaranteed service. If it fails, open the linked demo directly and use its Lyrics and Generate controls.
