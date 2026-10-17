"""Local-first Suno-style music studio powered by a self-hosted ACE-Step 1.5 engine."""
import json
import os
import time
from urllib.parse import urlparse

import requests
import streamlit as st


TASK_NAME = "AI Music Studio"
TASK_ICON = "🎧"


def _local_music_base():
    return os.getenv("ACESTEP_API_BASE", "http://127.0.0.1:8001").strip().rstrip("/")


def _local_music_status():
    base = _local_music_base()
    try:
        response = requests.get(f"{base}/health", timeout=2)
        if response.ok:
            return True, f"Local music engine reachable at {base}"
    except requests.RequestException:
        pass
    return False, f"Local ACE-Step engine not running at {base}. No external music API will be used."


def _offline_lyrics(idea, language, genre, mood, voice, notes):
    """Simple offline lyric starter; no model or network access."""
    topic = idea.strip().rstrip(".")
    if language == "Punjabi":
        verses = [
            f"{topic} da supna dil vich sajaya,",
            "Hausle naal har raah banaya,",
            "Dig ke vi main fer uth jaana,",
            "Mehnat naal apna mukaam banana.",
            "",
            "[Chorus]",
            "Chalde rehna, rukna nahi,",
            "Supne apne bhulna nahi,",
            "Dil di awaaz nu geet bana ke,",
            "Manzil wal nu turde jaana.",
            "",
            "[Verse 2]",
            "Mitti di khushboo, apne lok,",
            "Dil vich umeed te akhan vich noor,",
            "Ajj di mehnat kal rang laave,",
            "Sachcha iraada manzil paave.",
        ]
    elif language == "Hindi":
        verses = [
            f"{topic} का सपना दिल में सजाया,",
            "हौसलों ने हर रास्ता दिखाया,",
            "गिरकर भी फिर उठ जाना है,",
            "मेहनत से मुकाम बनाना है।",
            "",
            "[Chorus]",
            "चलते रहना, रुकना नहीं,",
            "अपने सपनों से मुड़ना नहीं,",
            "दिल की धुन को गीत बनाकर,",
            "मंज़िल की ओर बढ़ते जाना।",
            "",
            "[Verse 2]",
            "नई सुबह का रंग निराला,",
            "दिल में उम्मीद का उजियाला,",
            "आज की मेहनत रंग लाएगी,",
            "कल खुशियों की धुन गाएगी।",
        ]
    else:
        verses = [
            f"I have a dream about {topic},",
            "A little hope to guide my way,",
            "When I fall, I rise again,",
            "I turn the struggle into song.",
            "",
            "[Chorus]",
            "Keep moving, don't let go,",
            "Plant the dream and watch it grow,",
            "Every heartbeat, every sound,",
            "Lifts me up when I am down.",
            "",
            "[Verse 2]",
            "Every road has stories to tell,",
            "Every storm will break as well,",
            "Step by step, I find my way,",
            "I will meet a brighter day.",
        ]
    return f"# {topic.title()}\n\n[Style: {genre}; Mood: {mood}; Vocal: {voice}]\n\n" + "\n".join(verses) + (f"\n\n[Notes: {notes.strip()}]" if notes.strip() else "")


def _local_generate_music(prompt, lyrics, language, duration, bpm, seed):
    """Generate via the locally running ACE-Step REST server only."""
    base = _local_music_base()
    parsed_base = urlparse(base)
    if parsed_base.scheme not in ("http", "https") or not parsed_base.hostname:
        raise RuntimeError("ACESTEP_API_BASE must be a valid local server URL.")
    if parsed_base.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise RuntimeError("For privacy, this studio only accepts a localhost ACE-Step server. It will not send lyrics to a remote host.")

    payload = {
        "prompt": prompt,
        "lyrics": lyrics,
        "thinking": True,
        "vocal_language": {"Punjabi": "pa", "Hindi": "hi", "English": "en", "Bengali": "bn", "Spanish": "es"}.get(language, "en"),
        "audio_format": "mp3",
        "audio_duration": int(duration),
        "bpm": int(bpm),
        "inference_steps": 8,
        "use_random_seed": int(seed) < 0,
        "seed": int(seed),
        "batch_size": 1,
        "task_type": "text2music",
        "model": os.getenv("ACESTEP_MODEL", "acestep-v15-turbo"),
    }
    try:
        response = requests.post(f"{base}/release_task", json=payload, timeout=45)
        response.raise_for_status()
        envelope = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not submit to your local ACE-Step server at {base}: {exc}") from exc
    data = envelope.get("data") or {}
    task_id = data.get("task_id")
    if envelope.get("code", 200) != 200 or not task_id:
        raise RuntimeError(str(envelope.get("error") or envelope)[:600])

    deadline = time.monotonic() + max(300, int(duration) * 10)
    last_status = "queued"
    while time.monotonic() < deadline:
        try:
            poll = requests.post(f"{base}/query_result", json={"task_id_list": [task_id]}, timeout=30)
            poll.raise_for_status()
            result_envelope = poll.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"Could not query your local music job: {exc}") from exc

        rows = result_envelope.get("data") or []
        if not rows:
            time.sleep(3)
            continue
        row = rows[0]
        status = row.get("status")
        last_status = str(status)
        if status == 2:
            raise RuntimeError(str(row.get("error") or row.get("result") or "ACE-Step reports that generation failed.")[:700])
        if status == 1:
            raw_result = row.get("result") or ""
            try:
                parsed = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
            except json.JSONDecodeError:
                parsed = []
            if isinstance(parsed, dict):
                parsed = [parsed]
            file_path = next((item.get("file") for item in parsed if isinstance(item, dict) and item.get("file")), None) if isinstance(parsed, list) else None
            if not file_path:
                raise RuntimeError(f"Local model finished but did not return an audio file: {str(raw_result)[:500]}")
            file_url = file_path if file_path.startswith("http://") or file_path.startswith("https://") else f"{base}{file_path if file_path.startswith('/') else '/' + file_path}"
            parsed_file = urlparse(file_url)
            if parsed_file.hostname not in ("localhost", "127.0.0.1", "::1"):
                raise RuntimeError("The local engine returned a non-local audio URL. Download blocked for privacy.")
            try:
                audio_response = requests.get(file_url, timeout=180)
                audio_response.raise_for_status()
            except requests.RequestException as exc:
                raise RuntimeError(f"Could not download the generated audio from the local engine: {exc}") from exc
            if not audio_response.content:
                raise RuntimeError("The local music engine returned an empty audio file.")
            return audio_response.content
        time.sleep(3)
    raise TimeoutError(f"Local music generation timed out. Last task status: {last_status}")


def render():
    st.subheader("🎧 AI Music Studio")
    st.caption("Suno-style creation workflow, powered by an open-source model running on your own machine. This app does not call Suno, Gemini, Hugging Face Spaces, or other hosted generation APIs.")

    online, status_text = _local_music_status()
    if online:
        st.success(status_text)
    else:
        st.warning(status_text)
        st.markdown("Install and start the local engine using the instructions below. Codespaces CPU-only instances may not have enough memory or GPU capacity for full-song generation.")

    with st.form("ai_music_studio_form"):
        mode = st.radio("Creation mode", ["Simple mode — describe the song", "Custom mode — control lyrics and sound"], horizontal=False)
        music_idea = st.text_area("Describe your song", placeholder="A cinematic Punjabi motivational anthem about rising after failure, dhol, tumbi, modern bass and a powerful chorus.", height=100)
        c1, c2 = st.columns(2)
        with c1:
            music_language = st.selectbox("Vocal language", ["Punjabi", "Hindi", "English", "Bengali", "Spanish"])
            music_genre = st.selectbox("Genre", ["Punjabi Bhangra pop", "Punjabi folk", "Bollywood cinematic", "Romantic ballad", "Sad acoustic", "Motivational anthem", "Hip-hop / rap", "EDM pop", "Rock", "Lo-fi chill", "Sufi"])
            music_mood = st.selectbox("Mood", ["Energetic", "Romantic", "Emotional", "Hopeful", "Powerful", "Peaceful", "Dark / dramatic"])
        with c2:
            music_voice = st.selectbox("Vocal arrangement", ["Lead vocal with backing harmonies", "Male-sounding lead vocal", "Female-sounding lead vocal", "Duet", "Mostly instrumental"])
            music_duration = st.select_slider("Duration", options=[30, 45, 60, 90, 120, 150, 180, 240], value=120, format_func=lambda n: f"{n} seconds")
            bpm = st.slider("Tempo (BPM)", min_value=60, max_value=180, value=112, step=1)
        lyrics_mode = st.radio("Lyrics", ["Generate offline starter lyrics", "Use my own lyrics", "Instrumental only"])
        custom_lyrics = st.text_area("Paste or edit lyrics", placeholder="[Verse 1]\nYour lyrics...\n\n[Chorus]\nYour hook...", height=170)
        notes = st.text_area("Extra creative direction (optional)", placeholder="Instruments, energy curve, intro/outro, pronunciation, mix...")
        seed = st.number_input("Seed (-1 = random)", min_value=-1, max_value=2147483647, value=-1, step=1)
        make_full_song = st.form_submit_button("🎵 Generate with local model", type="primary", use_container_width=True)

    if make_full_song:
        if not music_idea.strip() and lyrics_mode != "Instrumental only":
            st.error("Describe your song or enter lyrics first.")
        elif lyrics_mode == "Use my own lyrics" and not custom_lyrics.strip():
            st.error("Please paste your lyrics.")
        elif not online:
            st.error("Local music engine is offline. No remote fallback will be used.")
        else:
            lyrics = ""
            if lyrics_mode == "Use my own lyrics":
                lyrics = custom_lyrics.strip()
            elif lyrics_mode == "Generate offline starter lyrics":
                lyrics = _offline_lyrics(music_idea, music_language, music_genre, music_mood, music_voice, notes)
            prompt = ", ".join([
                music_genre, music_mood + " mood", music_voice, f"{music_language} vocals",
                f"{int(bpm)} BPM", "full song, polished studio mix, clear lead vocal, balanced instrumental accompaniment",
                music_idea.strip(), notes.strip()
            ])
            if lyrics_mode == "Instrumental only":
                lyrics = "[Instrumental]"
                prompt += ", instrumental only, no vocals"
            st.session_state["studio_last_lyrics"] = lyrics
            st.session_state["studio_last_prompt"] = prompt
            try:
                with st.spinner("Generating on your local ACE-Step model. This may take a while on CPU..."):
                    audio_bytes = _local_generate_music(prompt, lyrics, music_language, music_duration, bpm, seed)
                st.session_state["studio_last_mp3"] = audio_bytes
                st.success("Your song was generated by the local model. No external AI API was called.")
            except Exception as exc:
                st.error(f"Local generation failed: {exc}")

    if st.session_state.get("studio_last_prompt"):
        st.markdown("### Your creation settings")
        st.write(st.session_state["studio_last_prompt"])
    if st.session_state.get("studio_last_lyrics"):
        st.markdown("### Lyrics")
        st.text_area("Review / copy lyrics", value=st.session_state["studio_last_lyrics"], height=220, key="studio_lyrics_view")
        st.download_button("Download lyrics (.txt)", st.session_state["studio_last_lyrics"], file_name="song_lyrics.txt", mime="text/plain", use_container_width=True)
    if st.session_state.get("studio_last_mp3"):
        st.markdown("### Your generated song")
        st.audio(st.session_state["studio_last_mp3"], format="audio/mpeg")
        st.download_button("⬇️ Download MP3", data=st.session_state["studio_last_mp3"], file_name="my_local_ai_song.mp3", mime="audio/mpeg", use_container_width=True)

    with st.expander("Install the local music engine (one-time setup)"):
        st.markdown("ACE-Step 1.5 is an open-source local music model. Model weights download on first engine startup; that is a one-time download, not a hosted inference API. It needs substantial storage and is best with a compatible GPU. A free Codespace may not be suitable.")
        st.code(
            "curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            "git clone https://github.com/ace-step/ACE-Step-1.5.git\n"
            "cd ACE-Step-1.5\n"
            "uv sync\n"
            "uv run acestep-api",
            language="bash",
        )
        st.markdown("When the local engine is running, keep it on port 8001. If you run it somewhere else on the same machine, set ACESTEP_API_BASE to that local address. This app intentionally blocks remote hosts.")
        st.markdown("[Official ACE-Step 1.5 installation guide](https://github.com/ace-step/ACE-Step-1.5)")
