"""Original procedural music engine built with Python's standard library only.

This is a lightweight algorithmic synthesizer, not a trained generative audio model.
It creates original instrumental WAV music from chords, bass, melody and percussion.
"""
from __future__ import annotations

import hashlib
import io
import math
import random
import wave
from array import array

SAMPLE_RATE = 16000
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
CHORDS = {
    "Pop": ((0, 4, 7), (9, 0, 4), (5, 9, 0), (7, 11, 2)),
    "Cinematic": ((0, 7, 12), (5, 9, 12), (9, 12, 16), (7, 11, 14)),
    "Lo-fi": ((9, 0, 4, 7), (2, 5, 9, 0), (7, 11, 2, 5), (0, 4, 7, 11)),
    "EDM": ((9, 0, 4), (5, 9, 0), (0, 4, 7), (7, 11, 2)),
    "Punjabi-inspired": ((0, 4, 7), (7, 11, 2), (5, 9, 0), (7, 11, 2)),
    "Ambient": ((0, 7, 12), (5, 9, 12), (2, 7, 11), (9, 12, 16)),
}
MOOD_SCALE = {
    "Uplifting": (0, 2, 4, 7, 9),
    "Happy": (0, 2, 4, 7, 9, 11),
    "Emotional": (0, 2, 3, 7, 9),
    "Dark": (0, 3, 5, 7, 10),
    "Peaceful": (0, 2, 5, 7, 9),
    "Energetic": (0, 2, 4, 5, 7, 9, 11),
}


def _frequency(midi_note: int) -> float:
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def _add_tone(mix, start, duration, midi_note, volume, waveform, rng, attack=0.02, release=0.12):
    total = len(mix)
    first = max(0, int(start * SAMPLE_RATE))
    last = min(total, int((start + duration) * SAMPLE_RATE))
    if last <= first:
        return
    freq = _frequency(midi_note)
    phase = rng.random() * math.tau
    span = max(1, last - first)
    attack_n = max(1, int(attack * SAMPLE_RATE))
    release_n = max(1, int(release * SAMPLE_RATE))
    for index in range(first, last):
        local = index - first
        env = min(1.0, local / attack_n, (span - local) / release_n)
        env = max(0.0, env)
        t = index / SAMPLE_RATE
        angle = math.tau * freq * t + phase
        if waveform == "pluck":
            sample = math.sin(angle) * 0.72 + math.sin(angle * 2.01) * 0.20 + math.sin(angle * 3.0) * 0.08
            env *= math.exp(-4.0 * local / SAMPLE_RATE)
        elif waveform == "pad":
            sample = math.sin(angle) * 0.72 + math.sin(angle * 1.003) * 0.28
        elif waveform == "bass":
            sample = math.sin(angle) * 0.82 + math.sin(angle * 2.0) * 0.18
        else:
            sample = math.sin(angle) * 0.68 + math.sin(angle * 2.0) * 0.20 + math.sin(angle * 3.0) * 0.12
        mix[index] += sample * volume * env


def _add_drums(mix, beat_times, style, rng):
    total = len(mix)
    for beat_index, start in enumerate(beat_times):
        # Kick: a short downward pitch sweep gives a drum-like thump.
        if style in ("EDM", "Punjabi-inspired", "Pop", "Cinematic") and beat_index % 2 == 0:
            first = int(start * SAMPLE_RATE)
            length = min(int(0.22 * SAMPLE_RATE), total - first)
            for j in range(max(0, length)):
                t = j / SAMPLE_RATE
                freq = 105.0 - 65.0 * min(1.0, t / 0.22)
                mix[first + j] += math.sin(math.tau * freq * t) * math.exp(-18.0 * t) * 0.25
        # Snare/clap on beats 2 and 4.
        if beat_index % 4 in (1, 3) and style != "Ambient":
            first = int(start * SAMPLE_RATE)
            length = min(int(0.12 * SAMPLE_RATE), total - first)
            for j in range(max(0, length)):
                t = j / SAMPLE_RATE
                noise = rng.uniform(-1.0, 1.0)
                mix[first + j] += noise * math.exp(-30.0 * t) * (0.075 if style == "Lo-fi" else 0.12)
        # Closed hi-hat ticks.
        if style in ("EDM", "Punjabi-inspired", "Pop", "Lo-fi") and beat_index % 2 == 1:
            first = int(start * SAMPLE_RATE)
            length = min(int(0.045 * SAMPLE_RATE), total - first)
            for j in range(max(0, length)):
                t = j / SAMPLE_RATE
                mix[first + j] += rng.uniform(-1.0, 1.0) * math.exp(-90.0 * t) * 0.035


def generate_instrumental(title: str, genre: str = "Pop", mood: str = "Uplifting",
                          duration: int = 30, bpm: int = 100, seed: int = 7, prompt: str = "") -> bytes:
    """Return an original 16-bit mono WAV as bytes."""
    duration = max(8, min(60, int(duration)))
    bpm = max(60, min(160, int(bpm)))
    genre = genre if genre in CHORDS else "Pop"
    mood = mood if mood in MOOD_SCALE else "Uplifting"
    seed_material = f"{int(seed)}|{title}|{prompt}".encode("utf-8", errors="replace")
    effective_seed = int.from_bytes(hashlib.sha256(seed_material).digest()[:8], "big")
    rng = random.Random(effective_seed)
    total_samples = int(SAMPLE_RATE * duration)
    mix = [0.0] * total_samples
    beat = 60.0 / bpm
    bar = beat * 4.0
    chord_set = CHORDS[genre]
    scale = MOOD_SCALE[mood]
    # Choose a deterministic root from the seed so each seed has its own key.
    root = 48 + rng.randrange(0, 12)
    beat_times = [n * beat for n in range(int(duration / beat) + 1) if n * beat < duration]

    for bar_index, bar_start in enumerate([n * bar for n in range(int(math.ceil(duration / bar)))]):
        chord = chord_set[bar_index % len(chord_set)]
        chord_duration = min(bar, duration - bar_start)
        pad_wave = "pad" if genre in ("Ambient", "Cinematic", "Lo-fi") else "soft"
        for interval in chord:
            _add_tone(mix, bar_start, chord_duration, root + interval + 12, 0.075,
                      pad_wave, rng, attack=0.25, release=0.35)
        # Bass notes anchor the chord on beats 1 and 3.
        bass_note = root + chord[0] - 12
        for beat_no in (0, 2):
            start = bar_start + beat_no * beat
            if start < duration:
                _add_tone(mix, start, min(beat * 0.85, duration - start), bass_note,
                          0.17, "bass", rng, attack=0.008, release=0.10)
        # A changing lead motif, with small pauses and phrase variation.
        steps_per_bar = 8 if genre in ("EDM", "Punjabi-inspired") else 4
        step = beat * 4.0 / steps_per_bar
        for step_no in range(steps_per_bar):
            start = bar_start + step_no * step
            if start >= duration:
                continue
            if rng.random() < (0.12 if mood in ("Peaceful", "Emotional") else 0.06):
                continue
            scale_degree = rng.choice(scale)
            octave = rng.choice((0, 12, 12, 24))
            note = root + 12 + scale_degree + octave
            note_duration = min(step * rng.choice((0.65, 0.8, 0.95)), duration - start)
            volume = 0.095 if genre != "Ambient" else 0.055
            _add_tone(mix, start, note_duration, note, volume, "pluck", rng,
                      attack=0.008, release=min(0.16, note_duration * 0.45))

    _add_drums(mix, beat_times, genre, rng)
    # Soft fade-in/out, peak normalization and clipping protection.
    fade_n = min(int(0.6 * SAMPLE_RATE), total_samples // 4)
    peak = max((abs(x) for x in mix), default=0.0) or 1.0
    scale_factor = 0.88 / peak
    pcm = array("h")
    for i, value in enumerate(mix):
        fade = 1.0
        if fade_n:
            if i < fade_n:
                fade = i / fade_n
            elif i >= total_samples - fade_n:
                fade = (total_samples - i) / fade_n
        sample = max(-1.0, min(1.0, value * scale_factor * fade))
        pcm.append(int(sample * 32767))
    if pcm.itemsize != 2:
        raise RuntimeError("This Python platform does not support 16-bit audio samples.")
    # WAV PCM uses little-endian samples.
    if pcm.typecode == "h" and __import__("sys").byteorder != "little":
        pcm.byteswap()
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())
    return output.getvalue()
