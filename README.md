# My Personal AI Agent

A free-first Streamlit personal assistant with separate task apps and a local-first architecture. The root `app.py` launches the task menu; shared helpers live in `core/services.py`.

## Run the app

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Built-in Python Music Studio

`tasks/ai_music_studio/app.py` uses `core/procedural_music.py`, an original procedural music engine written in Python using only the standard library. It synthesizes chord pads, a changing melody, bass and percussion, and lets you play and download the result as a WAV file. An optional experimental formant layer creates vowel-like robotic tones guided by lyrics; it does not produce intelligible words or realistic singing. It does not require ACE-Step, Suno, a model download, API keys, or a separate server.

Choose a genre (Pop, Cinematic, Lo-fi, EDM, Punjabi-inspired or Ambient), mood, duration, BPM and variation seed. Change the seed to create a different arrangement.

**Current capability limit:** this is an algorithmic composer, not a trained text-to-music neural network. The optional vocal layer is experimental formant synthesis and does not pronounce lyrics intelligibly. Realistic singing and semantic natural-language-to-song generation are not provided by this from-scratch version. Its audio is synthesized locally by Python.

## Local AI (no external AI API required)

External AI services are disabled by default. For optional local text generation, download a suitable GGUF instruct model, install `requirements-local.txt`, and set `LOCAL_MODEL_PATH`. Follow [LOCAL_AI.md](LOCAL_AI.md). Model weights are not committed to GitHub.

## Tasks

- `tasks/chat/app.py` — assistant chat and poster-by-command workflow.
- `tasks/ai_music_studio/app.py` — built-in Python instrumental music studio.
- `core/procedural_music.py` — original standard-library audio synthesizer.
- `tasks/punjabi_song_generator/app.py` — offline Punjabi lyric writer.
- `tasks/file_analyst/app.py` — local CSV/Excel analysis.
- `tasks/calculator/app.py` — safe arithmetic calculator.
- `tasks/notes_tasks/app.py` — local saved notes and tasks.
- `tasks/poster_maker/app.py` — local designed graphic poster generation.
- `tasks/settings/app.py` — environment and privacy information.

## Honest capability limits

This app's music engine is original procedural Python code, not Suno-level generative AI. It creates instrumental WAV audio without a model or network connection. The offline lyric starter is template-based rather than a full language model. Poster Maker creates typography/shape-based PNG graphics locally and does not create photorealistic artwork.

## Experimental neural music model (train it yourself)

The AI Music Studio now includes an optional **Train your own neural music model** section. This is a small Transformer written for this repository and trained from scratch on MIDI note sequences supplied by you. It is not Suno source code, does not call a paid API, and does not download pretrained weights.

Install its optional dependencies in the Codespaces terminal:

```bash
python -m pip install -r requirements-neural.txt
```

Then open **AI Music Studio**, upload one or more `.mid` / `.midi` files, and select **Train model from my MIDI files**. After training, select **Generate neural melody preview** and download the WAV. The checkpoint is saved locally at `models/music_transformer.pt` in the Codespace.

CLI alternative:

```bash
mkdir -p data/midi
# Put MIDI files you have permission to use in data/midi/
python scripts/train_neural_music.py train --midi-dir data/midi --epochs 30
python scripts/train_neural_music.py generate --length 128 --bpm 100
```

**Important limitations:** this first neural prototype learns pitch sequences from MIDI, not raw audio. Its preview is a simple synthesized melody, not a full-band song; it does not generate lyrics, human vocals, realistic singing, or Suno-level audio. Training quality depends on the amount and quality of MIDI examples and available compute. The existing procedural instrumental generator remains available independently. Checkpoints are generated locally and are not committed to GitHub.
