"""Original from-scratch procedural music composer.

This is not Suno source code and does not use a trained text-to-music model.
It creates a structured instrumental arrangement with optional experimental tones.
"""
import streamlit as st
from pathlib import Path
import tempfile

from core.procedural_music import generate_instrumental

TASK_NAME = "AI Music Studio"
TASK_ICON = "🎧"


def render():
    st.title("🎧 AI Music Studio")
    st.caption("Original Python composition engine • free • local • no external AI APIs")
    st.info(
        "This is original code written for this project, not copied Suno code. The arranger now "
        "shapes an instrumental track across intro, verse, chorus, final chorus and outro. "
        "It does not yet create realistic singing or intelligibly sing lyrics: matching Suno "
        "quality requires a trained audio-generation model and substantial training data/GPU. "
        "No paid API or model download is used by this local version."
    )

    with st.form("python_music_studio_form"):
        title = st.text_input("Song idea / title", value="A New Beginning")
        description = st.text_area(
            "Describe the sound you want",
            value="A hopeful, cinematic melody that starts gently and builds into an uplifting rhythm.",
            help="The text changes the generated variation, but the engine does not semantically understand the prompt like a trained music AI.",
        )
        col1, col2 = st.columns(2)
        with col1:
            genre = st.selectbox(
                "Genre",
                ["Pop", "Cinematic", "Lo-fi", "EDM", "Punjabi-inspired", "Ambient"],
            )
            mood = st.selectbox(
                "Mood",
                ["Uplifting", "Happy", "Emotional", "Dark", "Peaceful", "Energetic"],
            )
            duration = st.slider("Duration (seconds)", min_value=8, max_value=60, value=30)
        with col2:
            bpm = st.slider("Tempo (BPM)", min_value=60, max_value=160, value=100)
            seed = st.number_input("Variation seed", min_value=0, max_value=999999, value=7, step=1)
            st.caption("Change the seed to create a different melody.")
        lyrics = st.text_area(
            "Lyrics / song notes (optional)",
            placeholder="Paste lyrics. Optional experimental vocal mode uses vowel sounds only; it will not sing the words intelligibly.",
            height=120,
        )
        add_vocal = st.checkbox(
            "Add experimental synthetic vocal layer (robotic vowel sounds)",
            value=False,
            help="Uses a formant synthesizer written in Python. It does not create intelligible words or realistic human singing.",
        )
        make_track = st.form_submit_button(
            "🎼 Generate original music", type="primary", use_container_width=True
        )

    if make_track:
        if not title.strip():
            st.error("Please enter a song title or idea.")
            return
        if add_vocal and not lyrics.strip():
            st.error("Enter some lyrics to drive the experimental vowel layer, or turn that option off.")
            return
        with st.spinner("Composing with the built-in Python engine…"):
            try:
                audio_bytes = generate_instrumental(
                    title=title.strip(),
                    genre=genre,
                    mood=mood,
                    duration=duration,
                    bpm=bpm,
                    seed=int(seed),
                    prompt=description.strip(),
                    lyrics=lyrics.strip() if add_vocal else "",
                )
            except Exception as exc:
                st.error(f"Music generation failed: {exc}")
                return
        st.session_state["python_music_result"] = {
            "audio": audio_bytes,
            "title": title.strip(),
            "genre": genre,
            "mood": mood,
            "duration": duration,
            "bpm": bpm,
            "description": description.strip(),
            "lyrics": lyrics.strip(),
            "vocal_layer": bool(add_vocal),
            "seed": int(seed),
        }

    result = st.session_state.get("python_music_result")
    if result:
        st.divider()
        st.subheader(f"🎵 {result['title']}")
        vocal_label = " • experimental vowel layer" if result.get("vocal_layer") else ""
        st.caption(
            f"{result['genre']} • {result['mood']} • {result['duration']} seconds • "
            f"{result['bpm']} BPM • seed {result['seed']}{vocal_label}"
        )
        st.audio(result["audio"], format="audio/wav")
        safe_name = "".join(
            c.lower() if c.isalnum() else "_" for c in result["title"]
        ).strip("_")
        safe_name = safe_name[:60] or "original_music"
        st.download_button(
            "⬇️ Download WAV music",
            data=result["audio"],
            file_name=f"{safe_name}.wav",
            mime="audio/wav",
            use_container_width=True,
        )
        if result.get("description"):
            with st.expander("Your original brief"):
                st.write(result["description"])
        if result.get("lyrics"):
            label = (
                "Lyrics used to guide the experimental vocal layer"
                if result.get("vocal_layer")
                else "Saved lyrics / notes (not sung)"
            )
            with st.expander(label):
                st.text(result["lyrics"])
                if result.get("vocal_layer"):
                    st.caption(
                        "Only vowel-shaped tones are synthesized. Consonants and words are not intelligible."
                    )
        st.caption("To make another version, change the Variation seed and generate again.")


    st.divider()
    st.subheader("🧠 Train your own neural music model")
    st.caption("Experimental: trains a small Transformer from MIDI note sequences you provide. It does not train on audio and does not generate realistic singing.")
    st.warning(
        "This is a from-scratch learning prototype, not Suno-quality generation. "
        "It currently learns note-pitch patterns from MIDI files and renders a simple synthesized melody. "
        "Training needs optional PyTorch, mido and NumPy dependencies plus your own MIDI training examples."
    )
    midi_uploads = st.file_uploader(
        "Upload MIDI training files (.mid / .midi)",
        type=["mid", "midi"],
        accept_multiple_files=True,
        key="neural_music_midi_uploads",
        help="Use MIDI files you have permission to use. More varied, clean MIDI examples generally help.",
    )
    neural_epochs = st.slider(
        "Training epochs", min_value=1, max_value=30, value=5, step=1,
        key="neural_music_epochs",
    )
    if st.button("🧠 Train model from my MIDI files", key="train_neural_music_button"):
        if not midi_uploads:
            st.error("Upload at least one MIDI file first.")
        else:
            try:
                from core.neural_music_model import train_from_midi_files
                with tempfile.TemporaryDirectory(prefix="music_midi_") as tmp:
                    midi_paths = []
                    for index, uploaded in enumerate(midi_uploads):
                        safe_name = Path(uploaded.name).name
                        path = Path(tmp) / f"{index}_{safe_name}"
                        path.write_bytes(uploaded.getvalue())
                        midi_paths.append(path)
                    with st.spinner("Training the small neural model on CPU/GPU available to this Codespace…"):
                        training_result = train_from_midi_files(
                            midi_paths,
                            output_path="models/music_transformer.pt",
                            epochs=neural_epochs,
                            sequence_length=64,
                        )
                st.session_state["neural_music_training_result"] = training_result
                st.success(
                    f"Training finished: {training_result['files']} MIDI file(s), "
                    f"{training_result['windows']} training windows, "
                    f"final loss {training_result['final_loss']:.4f}."
                )
                st.caption(f"Checkpoint saved at {training_result['checkpoint']}.")
            except Exception as exc:
                st.error(f"Training could not start or finish: {exc}")
                st.info("Install optional packages in the Codespaces terminal: pip install -r requirements-neural.txt")

    checkpoint_path = Path("models/music_transformer.pt")
    if checkpoint_path.exists():
        st.markdown("**Your trained model is available in this Codespace.**")
        neural_length = st.slider(
            "Generated melody notes", min_value=32, max_value=256, value=96, step=16,
            key="neural_music_length",
        )
        neural_temperature = st.slider(
            "Variation", min_value=0.3, max_value=1.5, value=0.9, step=0.1,
            key="neural_music_temperature",
        )
        neural_seed = st.number_input(
            "Neural model seed", min_value=0, max_value=999999, value=7, step=1,
            key="neural_music_seed",
        )
        if st.button("🎹 Generate neural melody preview", key="generate_neural_music_button"):
            try:
                from core.neural_music_model import generate_pitch_sequence, render_pitch_sequence_wav
                with st.spinner("Generating a new melody from your trained model…"):
                    notes = generate_pitch_sequence(
                        checkpoint_path,
                        length=neural_length,
                        temperature=neural_temperature,
                        seed=int(neural_seed),
                    )
                    output_path = "models/neural_music_preview.wav"
                    render_pitch_sequence_wav(notes, output_path=output_path, bpm=bpm if "bpm" in locals() else 100)
                    st.session_state["neural_music_preview_bytes"] = Path(output_path).read_bytes()
                    st.session_state["neural_music_preview_notes"] = len(notes)
            except Exception as exc:
                st.error(f"Neural generation failed: {exc}")
                st.info("Check that requirements-neural.txt is installed and the checkpoint was trained successfully.")
        if st.session_state.get("neural_music_preview_bytes"):
            st.audio(st.session_state["neural_music_preview_bytes"], format="audio/wav")
            st.download_button(
                "⬇️ Download neural melody preview (WAV)",
                data=st.session_state["neural_music_preview_bytes"],
                file_name="neural_music_preview.wav",
                mime="audio/wav",
                key="download_neural_music_preview",
            )
