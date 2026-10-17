"""AI Music Studio: local procedural music and experimental vowel synthesis.

No hosted music API, ACE-Step, Suno, model download, or network request is used.
The optional vocal layer is a robotic formant tone, not intelligible singing.
"""
import streamlit as st

from core.procedural_music import generate_instrumental

TASK_NAME = "AI Music Studio"
TASK_ICON = "🎧"


def render():
    st.title("🎧 AI Music Studio")
    st.caption("Your own Python music engine • free • local • no external AI APIs")
    st.info(
        "This studio creates original music locally using a Python synthesizer. It can "
        "also add an experimental vowel-like synthetic vocal tone guided by your lyrics. "
        "That voice layer is robotic and does not pronounce words intelligibly; it is "
        "not realistic AI singing. No API, model download or separate server is needed."
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
