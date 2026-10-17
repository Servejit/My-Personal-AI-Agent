# My Personal AI Agent

A free-first Streamlit starter for a personal assistant. The current version provides a chat shell, safe calculator, CSV/Excel analysis, and notes/tasks. A generative language model is **not connected yet**; built-in chat responses are intentionally basic.

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

## Features

- Safe arithmetic calculator (does not execute arbitrary Python).
- CSV and Excel spreadsheet previews and summaries.
- Notes and tasks saved in `data/notes.json` in the working environment.
- Confirmation before deleting notes or clearing chat history.

## Privacy and limitations

- No paid AI API is required for the built-in tools.
- The app does not yet generate open-ended answers using an AI model.
- Do not upload sensitive files to a publicly accessible deployment.
- Codespaces and hosted environments may not preserve local note files after a rebuild or restart. Download or back up important notes.

## Next development step

Add a free/local language-model connection and keep important external actions behind explicit approval.
