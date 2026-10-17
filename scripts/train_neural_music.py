"""Train and sample the local symbolic music Transformer.

Usage:
  python scripts/train_neural_music.py train --midi-dir data/midi --epochs 30
  python scripts/train_neural_music.py generate --length 128 --bpm 100
"""
from __future__ import annotations

import argparse
from pathlib import Path

from core.neural_music_model import (
    generate_pitch_sequence,
    render_pitch_sequence_wav,
    train_from_midi_files,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train an original small MIDI-pitch Transformer.")
    sub = parser.add_subparsers(dest="command", required=True)
    train = sub.add_parser("train", help="Train from a folder of MIDI files")
    train.add_argument("--midi-dir", default="data/midi")
    train.add_argument("--epochs", type=int, default=30)
    train.add_argument("--sequence-length", type=int, default=64)
    train.add_argument("--output", default="models/music_transformer.pt")
    generate = sub.add_parser("generate", help="Generate a WAV melody from a trained checkpoint")
    generate.add_argument("--checkpoint", default="models/music_transformer.pt")
    generate.add_argument("--length", type=int, default=128)
    generate.add_argument("--temperature", type=float, default=0.9)
    generate.add_argument("--seed", type=int, default=7)
    generate.add_argument("--bpm", type=int, default=100)
    generate.add_argument("--output", default="generated_neural_music.wav")
    args = parser.parse_args()

    if args.command == "train":
        folder = Path(args.midi_dir)
        midi_paths = sorted([*folder.glob("*.mid"), *folder.glob("*.midi")])
        if not midi_paths:
            parser.error(f"No .mid/.midi files found in {folder}. Add MIDI files and retry.")
        result = train_from_midi_files(
            midi_paths, output_path=args.output, epochs=args.epochs,
            sequence_length=args.sequence_length,
        )
        print("Training complete:", result)
        print("Note: this is a small symbolic model; quality depends heavily on the MIDI corpus.")
        return 0

    pitches = generate_pitch_sequence(
        args.checkpoint, length=args.length, temperature=args.temperature, seed=args.seed
    )
    path = render_pitch_sequence_wav(pitches, output_path=args.output, bpm=args.bpm)
    print(f"Generated preview: {path} ({len(pitches)} notes)")
    print("This prototype generates a synthesized melody, not full-band audio or singing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
