"""AI Music Studio: original music generated locally with a Python synthesizer.

No ACE-Step, Suno, hosted inference API, model download, or network request is used.
This first version generates instrumental WAV audio; it does not synthesize realistic singing.
"""
import random
import streamlit as st

from core.procedural_music import generate_instrumental

TASK_NAME = "AI Music Studio"
TASK_ICON = "🎧"


def render():
    st.title("🎧 AI Music Studio")
    st.caption("Your own Python music engine • free • local • no external AI APIs")

    st.info(
        "This studio composes an original instrumental track using Python-generated "
        "chords, melody, bass and percussion. It needs no API key, model download or "
        "separate server. Realistic sung vocals are not available in this first version."
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
            placeholder="Paste lyrics here. They are kept as notes and are not sung by this instrumental engine.",
            height=120,
        )
        make_track = st.form_submit_button("🎼 Generate original instrumental", type="primary", use_container_width=True)

    if make_track:
        if not title.strip():
            st.error("Please enter a song title or idea.")
            return
        with st.spinner("Composing your track with the built-in Python engine…"):
            try:
                audio_bytes = generate_instrumental(
                    title=title.strip(),
                    genre=genre,
                    mood=mood,
                    duration=duration,
                    bpm=bpm,
                    seed=int(seed),
                    prompt=description.strip(),
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
            "seed": int(seed),
        }

    result = st.session_state.get("python_music_result")
    if result:
        st.divider()
        st.subheader(f"🎵 {result['title']}")
        st.caption(
            f"{result['genre']} • {result['mood']} • {result['duration']} seconds • "
            f"{result['bpm']} BPM • seed {result['seed']}"
        )
        st.audio(result["audio"], format="audio/wav")
        safe_name = "".join(c.lower() if c.isalnum() else "_" for c in result["title"]).strip("_")
        safe_name = safe_name[:60] or "original_instrumental"
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
            with st.expander("Saved lyrics / notes (not sung)"):
                st.text(result["lyrics"])
        st.caption("To make another version, change the Variation seed and generate again.")
