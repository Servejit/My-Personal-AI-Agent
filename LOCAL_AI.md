# Local AI mode (no external AI APIs)

This repository is designed to work local-first. External AI calls are not needed for the offline lyric starter, calculator, file analysis, notes, or graphic poster renderer.

## Local text generation

1. Download a suitable GGUF instruct model for your hardware.
2. Store the file outside the repository; do not commit model weights.
3. Install the optional runtime:

```bash
python -m pip install -r requirements-local.txt
```

4. Set the path to the actual GGUF file:

```bash
export LOCAL_MODEL_PATH="$HOME/models/your-model.gguf"
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Suno-style local music generation

The AI Music Studio integrates with the open-source ACE-Step 1.5 server running locally. It deliberately refuses non-local generation hosts, so song prompts and lyrics are not sent to hosted inference services.

Install the local engine on a suitable machine:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/ace-step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync
uv run acestep-api
```

Keep the engine running at `http://127.0.0.1:8001`, then open the Streamlit AI Music Studio. Model weights are downloaded on first startup; subsequent inference runs locally. To use another local port, set `ACESTEP_API_BASE` to a localhost URL. The app blocks non-local hosts.

**Hardware note:** ACE-Step is a specialist music-generation model. It requires substantial storage and compute; a GPU is recommended. Free Codespaces or a phone alone may not be capable of generating full songs reliably. If Streamlit runs in Codespaces but ACE-Step runs on another computer, a secure local network tunnel would be required; this app intentionally does not accept remote hosts by default.

Official install and GPU guidance: https://github.com/ace-step/ACE-Step-1.5

## What works without a model

- Punjabi and basic multilingual lyric starter templates.
- Calculator and local file analysis.
- Notes and tasks, subject to the host filesystem's persistence.
- Typography/shape-based poster graphics via Pillow.

## Privacy

The local music studio does not use Suno, Gemini, hosted Hugging Face Spaces, or remote inference endpoints. External AI providers elsewhere in the repository remain disabled by default. Do not enable external providers unless you explicitly want prompts or content sent to those services.
