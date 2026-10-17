# Local AI mode (no Gemini API required)

The app now defaults to **local-only AI**. Chat, lyric writing, and poster copy can use a GGUF language model running inside the Python process. Prompts are not sent to Gemini unless you explicitly opt in by setting `ALLOW_EXTERNAL_AI=true`.

## Important limitation

A local text model does not automatically provide image diffusion or sung music generation. Poster Maker already draws graphic posters locally with Pillow. The current sung-MP3 workflow uses a hosted ACE-Step service; it is blocked unless you explicitly enable external services. Running a Suno-class singing/music model or a Midjourney-class image model locally requires downloading large specialist model weights and enough RAM/VRAM. GitHub Codespaces is often too constrained for those workloads, especially on a free CPU-only instance.

## Enable local text generation

1. Choose a GGUF instruct model appropriate for your hardware. A small quantized model is easier to run but less capable. Review the model's license before use.
2. Download its `.gguf` file and store it somewhere in your Codespace (do not commit the model to GitHub).
3. In the Codespaces terminal, install the optional local runtime:

```bash
python -m pip install -r requirements-local.txt
```

4. Set the path for the current terminal session (replace the path with your actual file):

```bash
export LOCAL_MODEL_PATH="$HOME/models/your-model.gguf"
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

5. Keep the model file outside Git and do not commit it. `LOCAL_N_CTX` can be set to 2048 or 4096 to manage RAM use.

## External services

External AI calls are disabled by default. If you knowingly want to enable the old Gemini text provider and hosted ACE-Step music service, set `ALLOW_EXTERNAL_AI=true` in the environment. This sends prompts/lyrics to those providers; only enable it if you accept that data flow. No API key is required for the public ACE-Step endpoint, but its uptime is not guaranteed.

## Local features that do not need AI services

- Calculator uses safe local Python arithmetic.
- File Analyst reads and summarizes files locally.
- Notes & Tasks saves data locally (subject to the hosting filesystem's persistence).
- Poster Maker renders designed PNG posters locally with Pillow; it does not create photorealistic artwork.
