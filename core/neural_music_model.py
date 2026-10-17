"""Small train-from-scratch symbolic music Transformer prototype.

It learns pitch sequences from user-provided MIDI files. It is not an audio diffusion
model and cannot generate realistic singing. PyTorch and mido are optional dependencies.
"""
from __future__ import annotations

import io
import math
import random
import wave
from array import array
from pathlib import Path
from typing import Iterable

PITCH_COUNT = 128
REST_TOKEN = 128
VOCAB_SIZE = 129


def midi_to_pitch_sequence(path: str | Path) -> list[int]:
    """Read MIDI and return a time-ordered monophonic pitch sequence."""
    try:
        import mido
    except ImportError as exc:
        raise RuntimeError("Install optional dependencies: pip install -r requirements-neural.txt") from exc
    midi = mido.MidiFile(str(path))
    notes: list[tuple[int, int]] = []
    absolute_tick = 0
    active: dict[tuple[int, int], list[int]] = {}
    for track in midi.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active.setdefault((msg.channel, msg.note), []).append(tick)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                key = (msg.channel, msg.note)
                starts = active.get(key)
                if starts:
                    start = starts.pop(0)
                    notes.append((start, int(msg.note)))
    notes.sort(key=lambda item: item[0])
    pitches = [pitch for _, pitch in notes]
    return pitches


def build_model(sequence_length: int = 64, d_model: int = 128, layers: int = 3, heads: int = 4):
    """Create a compact causal Transformer language model for MIDI pitches."""
    try:
        import torch
        from torch import nn
    except ImportError as exc:
        raise RuntimeError("PyTorch is required. Install requirements-neural.txt first.") from exc

    class PositionalEncoding(nn.Module):
        def __init__(self):
            super().__init__()
            position = torch.arange(sequence_length).unsqueeze(1)
            div = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
            pe = torch.zeros(sequence_length, d_model)
            pe[:, 0::2] = torch.sin(position * div)
            pe[:, 1::2] = torch.cos(position * div[: pe[:, 1::2].shape[1]])
            self.register_buffer("pe", pe.unsqueeze(0))

        def forward(self, x):
            return x + self.pe[:, : x.size(1)]

    class PitchTransformer(nn.Module):
        def __init__(self):
            super().__init__()
            self.embedding = nn.Embedding(VOCAB_SIZE, d_model)
            self.position = PositionalEncoding()
            layer = nn.TransformerEncoderLayer(
                d_model=d_model, nhead=heads, dim_feedforward=d_model * 4,
                batch_first=True, dropout=0.1, activation="gelu",
            )
            self.transformer = nn.TransformerEncoder(layer, num_layers=layers)
            self.norm = nn.LayerNorm(d_model)
            self.output = nn.Linear(d_model, VOCAB_SIZE)

        def forward(self, tokens):
            length = tokens.size(1)
            mask = torch.triu(torch.ones(length, length, device=tokens.device, dtype=torch.bool), diagonal=1)
            x = self.position(self.embedding(tokens))
            return self.output(self.norm(self.transformer(x, mask=mask)))

    return PitchTransformer()


def train_from_midi_files(
    midi_paths: Iterable[str | Path],
    output_path: str | Path = "models/music_transformer.pt",
    epochs: int = 30,
    sequence_length: int = 64,
    learning_rate: float = 0.001,
) -> dict:
    """Train a small model from scratch using a user's own MIDI collection."""
    import torch
    from torch import nn

    paths = list(midi_paths)
    sequences = []
    for path in paths:
        seq = midi_to_pitch_sequence(path)
        if len(seq) >= 4:
            sequences.append(seq)
    if not sequences:
        raise ValueError("No usable notes found. Upload valid MIDI files containing notes.")
    windows = []
    stride = max(1, sequence_length // 2)
    for seq in sequences:
        for start in range(0, max(1, len(seq) - 1), stride):
            chunk = seq[start : start + sequence_length + 1]
            if len(chunk) >= 4:
                windows.append(chunk)
    if not windows:
        raise ValueError("The MIDI files are too short to create training examples.")

    model = build_model(sequence_length=sequence_length)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    loss_fn = nn.CrossEntropyLoss()
    model.train()
    losses = []
    for epoch in range(max(1, int(epochs))):
        random.shuffle(windows)
        epoch_losses = []
        for chunk in windows:
            x = torch.tensor(chunk[:-1], dtype=torch.long).unsqueeze(0)
            y = torch.tensor(chunk[1:], dtype=torch.long).unsqueeze(0)
            optimizer.zero_grad(set_to_none=True)
            logits = model(x)
            loss = loss_fn(logits.reshape(-1, VOCAB_SIZE), y.reshape(-1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_losses.append(float(loss.detach()))
        losses.append(sum(epoch_losses) / max(1, len(epoch_losses)))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "state_dict": model.state_dict(),
        "sequence_length": sequence_length,
        "d_model": 128,
        "layers": 3,
        "heads": 4,
        "vocab_size": VOCAB_SIZE,
        "training_files": len(sequences),
        "final_loss": losses[-1],
    }, destination)
    return {"files": len(sequences), "windows": len(windows), "epochs": len(losses),
            "final_loss": losses[-1], "checkpoint": str(destination)}


def generate_pitch_sequence(
    checkpoint_path: str | Path = "models/music_transformer.pt",
    length: int = 128,
    temperature: float = 0.9,
    seed: int = 7,
) -> list[int]:
    """Sample a pitch sequence from a previously trained checkpoint."""
    import torch

    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    seq_len = int(checkpoint.get("sequence_length", 64))
    model = build_model(seq_len, int(checkpoint.get("d_model", 128)),
                        int(checkpoint.get("layers", 3)), int(checkpoint.get("heads", 4)))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    torch.manual_seed(int(seed))
    generated = [60]
    with torch.no_grad():
        for _ in range(max(1, int(length)) - 1):
            context = generated[-seq_len:]
            x = torch.tensor(context, dtype=torch.long).unsqueeze(0)
            logits = model(x)[0, -1] / max(0.15, float(temperature))
            # Keep generated notes in a useful melodic register.
            logits[:40] = -1e9
            logits[96:] = -1e9
            probabilities = torch.softmax(logits, dim=-1)
            next_token = int(torch.multinomial(probabilities, 1).item())
            generated.append(next_token)
    return generated


def render_pitch_sequence_wav(
    pitches: Iterable[int],
    output_path: str | Path = "generated_neural_music.wav",
    bpm: int = 100,
    note_seconds: float = 0.30,
    sample_rate: int = 22050,
) -> str:
    """Render a generated symbolic melody to a basic playable WAV for preview."""
    import numpy as np

    notes = list(pitches)
    bpm = max(50, min(180, int(bpm)))
    note_seconds = max(0.08, min(1.0, float(note_seconds)))
    sample_rate = int(sample_rate)
    total = max(1, int(len(notes) * note_seconds * sample_rate))
    mix = np.zeros(total, dtype=np.float32)
    for index, midi_note in enumerate(notes):
        start = int(index * note_seconds * sample_rate)
        end = min(total, start + int(note_seconds * 0.92 * sample_rate))
        if end <= start:
            continue
        t = np.arange(end - start, dtype=np.float32) / sample_rate
        frequency = 440.0 * (2.0 ** ((int(midi_note) - 69) / 12.0))
        envelope = np.minimum(1.0, t / 0.025) * np.maximum(0.0, 1.0 - t / max(0.001, note_seconds))
        tone = (np.sin(2 * np.pi * frequency * t)
                + 0.28 * np.sin(4 * np.pi * frequency * t)
                + 0.10 * np.sin(6 * np.pi * frequency * t))
        mix[start:end] += 0.24 * tone * envelope
    peak = float(np.max(np.abs(mix))) if mix.size else 0.0
    if peak > 0:
        mix *= 0.9 / peak
    pcm = array("h", (int(max(-1.0, min(1.0, x)) * 32767) for x in mix))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())
    return str(destination)
