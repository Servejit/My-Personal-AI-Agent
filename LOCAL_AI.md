# Local AI mode (no external AI APIs)

This repository is designed to work local-first. External AI calls are not needed for the offline lyric starter, calculator, file analysis, notes, graphic poster renderer, or built-in procedural instrumental composer.

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

## Built-in Python Music Studio

The AI Music Studio calls `core/procedural_music.py`, a from-scratch algorithmic synthesizer built using Python's standard library. It generates chord layers, a melodic lead, bass, and simple percussion, then provides a downloadable WAV file.

No ACE-Step, Suno, remote inference, music API, model download, or API key is used. Music is generated inside the Streamlit Python process.

**Current limitations:** the engine creates instrumental music only. Lyrics are stored as notes and are not sung; it is not a neural text-to-music model and does not yet produce natural vocals or interpret arbitrary prompts like Suno. Duration is limited to 8–60 seconds to keep generation practical in a small app runtime.

## What works without a model

- Punjabi and basic multilingual lyric starter templates.
- Original procedural instrumental music rendered as WAV.
- Calculator and local file analysis.
- Notes and tasks, subject to the host filesystem's persistence.
- Typography/shape-based poster graphics via Pillow.

## Privacy

The built-in music engine runs locally and makes no network requests. External AI providers elsewhere in the repository remain disabled by default. Do not enable external providers unless you explicitly want prompts or content sent to those services.
