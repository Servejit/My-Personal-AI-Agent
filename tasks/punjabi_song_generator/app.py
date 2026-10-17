"""Independent Punjabi Song Generator task UI. Edit this file to change only this task."""
from core.services import *

TASK_NAME = "Punjabi Song Generator"
TASK_ICON = "🎵"


def _offline_lyrics(topic, script, genre, mood, length_choice, notes):
    """Create usable lyrics entirely in Python; no model, API, or network needed."""
    topic = topic.strip()
    notes = notes.strip()
    roman = script == "Roman Punjabi (English letters)"
    mixed = script == "Punjabi with a little Hindi"

    if roman:
        hook = [
            f"{topic} da supna akhan vich sajaya,",
            "Dilan de hausle naal raah banaya,",
            "Dig ke vi main fer khad jaana,",
            "Mehnat de naal ik din manzil paana.",
        ]
        verse_a = [
            f"{topic} di gall har saah sunaave,",
            "Chann vi raat nu raah dikhave,",
            "Aukhe vele hausla rakhna,",
            "Apne dil di sun ke chalna.",
        ]
        verse_b = [
            "Mitti di khushboo, yaadan puraniyan,",
            "Dil vich vasdiyan gallan suhaniyan,",
            "Sacha iraada, akhan vich noor,",
            "Chalde rehna, manzil nahi door.",
        ]
        bridge = [
            "Hawa de naal vi deep jagaavaange,",
            "Apni kahani aap likhaavaange,",
            "Ajj da vaada kal nibhauna,",
            "Himmat naal har mod langhauna.",
        ]
    elif mixed:
        hook = [
            f"{topic} का सपना दिल में सजाया,",
            "हौसले ने हर रास्ता दिखाया,",
            "गिरकर भी फिर उठ जाना है,",
            "मेहनत से मुकाम बनाना है।",
        ]
        verse_a = [
            f"{topic} की धुन दिल में बजती जाए,",
            "हर मुश्किल नया सबक सिखाए,",
            "दिल में उम्मीद, कदमों में जान,",
            "चलते रहना है अपनी शान।",
        ]
        verse_b = [
            "मिट्टी की खुशबू, अपने लोग,",
            "दिल में सपने, आँखों में जोग,",
            "सच्ची लगन से दिन बदलेंगे,",
            "मेहनत के रंग एक दिन खिलेंगे।",
        ]
        bridge = [
            "रुकना नहीं, आगे बढ़ना,",
            "अपने वादे पर कायम रहना,",
            "आज की मेहनत कल का नूर,",
            "मंज़िल होगी अब नहीं दूर।",
        ]
    else:
        hook = [
            f"{topic} ਦਾ ਸੁਪਨਾ ਦਿਲ ਵਿੱਚ ਸਜਾਇਆ,",
            "ਹੌਸਲੇ ਨਾਲ ਹਰ ਰਾਹ ਬਣਾਇਆ,",
            "ਡਿੱਗ ਕੇ ਵੀ ਮੈਂ ਫੇਰ ਉੱਠ ਜਾਣਾ,",
            "ਮਿਹਨਤ ਨਾਲ ਆਪਣਾ ਮੁਕਾਮ ਬਣਾਉਣਾ।",
        ]
        verse_a = [
            f"{topic} ਦੀ ਗੱਲ ਮੇਰੇ ਸਾਹਾਂ ਵਿੱਚ ਵੱਸਦੀ,",
            "ਉਮੀਦ ਦੀ ਲੌ ਹਰ ਰਾਤ ਵਿੱਚ ਹੱਸਦੀ,",
            "ਔਖੇ ਵੇਲੇ ਦਿਲ ਨਾ ਹਾਰੀਂ,",
            "ਆਪਣੀ ਮੰਜ਼ਿਲ ਆਪ ਸਵਾਰੀਂ।",
        ]
        verse_b = [
            "ਮਿੱਟੀ ਦੀ ਖੁਸ਼ਬੂ, ਯਾਦਾਂ ਪੁਰਾਣੀਆਂ,",
            "ਦਿਲ ਵਿੱਚ ਵੱਸਦੀਆਂ ਗੱਲਾਂ ਸੁਹਾਣੀਆਂ,",
            "ਸੱਚੀ ਲਗਨ ਨਾਲ ਦਿਨ ਬਦਲਣਗੇ,",
            "ਸੁੱਕੇ ਰਾਹਾਂ ਉੱਤੇ ਫੁੱਲ ਖਿੜਨਗੇ।",
        ]
        bridge = [
            "ਹਵਾ ਦੇ ਨਾਲ ਵੀ ਦੀਵੇ ਜਗਾਵਾਂਗੇ,",
            "ਆਪਣੀ ਕਹਾਣੀ ਆਪ ਲਿਖਾਵਾਂਗੇ,",
            "ਅੱਜ ਦਾ ਵਾਅਦਾ ਕੱਲ੍ਹ ਨਿਭਾਉਣਾ,",
            "ਹਿੰਮਤ ਨਾਲ ਹਰ ਮੋੜ ਲੰਘਾਉਣਾ।",
        ]

    if genre == "Romantic":
        hook = ([f"{topic} ਤੇਰਾ ਨਾਂ ਲੈ ਕੇ ਮੁਸਕਾਵੇ,", "ਦਿਲ ਹਰ ਪਲ ਤੇਰੇ ਕੋਲ ਆਵੇ,", "ਚੰਨ ਤਾਰਿਆਂ ਤੋਂ ਇਹੀ ਮੰਗਾਂ,", "ਤੇਰੇ ਨਾਲ ਹਰ ਰੁੱਤ ਮੈਂ ਲੰਘਾਂ।"] if not roman and not mixed else
                [f"{topic}, tera naa dil gungunaave,", "Har ik pal tera khayal sataave,", "Chann sitare gawahi paavan,", "Tere naal main duniya sajaavan."] if roman else
                [f"{topic} तेरा नाम दिल गुनगुनाए,", "हर पल तेरा खयाल पास आए,", "चाँद सितारे गवाही दें,", "तेरे संग हर मौसम रंगीन रहे।"])
    elif genre == "Sad / emotional":
        hook = (["ਚੁੱਪ ਰਾਤਾਂ ਵਿੱਚ ਯਾਦ ਤੇਰੀ ਆਵੇ,", "ਦਿਲ ਦੀ ਧੜਕਣ ਤੈਨੂੰ ਬੁਲਾਵੇ,", "ਹੱਸਦੇ ਚਿਹਰੇ ਪਿੱਛੇ ਦਰਦ ਲੁਕਾਇਆ,", "ਵਕਤ ਨੇ ਸਾਨੂੰ ਕਿੰਨਾ ਅਜ਼ਮਾਇਆ।"] if not roman and not mixed else
                ["Chup raatan vich yaad teri aave,", "Dil di dhadkan tainu bulaave,", "Hassde chehre pichhe dard lukaya,", "Waqt ne sanu kinna azmaya."] if roman else
                ["खामोश रातों में याद तेरी आए,", "दिल हर धड़कन में तुझे बुलाए,", "हँसते चेहरे के पीछे दर्द छुपाया,", "वक़्त ने हमें कितना आज़माया।"])
    elif genre in ("Bhangra", "Modern Punjabi pop") or mood == "Energetic":
        hook = (["ਢੋਲ ਵੱਜੇ, ਸਾਰੀ ਦੁਨੀਆ ਨੱਚੇ,", "ਦਿਲ ਦੀ ਧੁਨ ਤੇ ਕਦਮ ਵੀ ਨੱਚਣ,", "ਅੱਜ ਦੀ ਰਾਤ ਖੁਸ਼ੀਆਂ ਮਨਾਈਏ,", "ਹੱਸਦੇ ਗਾਉਂਦੇ ਰੰਗ ਜਮਾਈਏ।"] if not roman and not mixed else
                ["Dhol vajje, saari duniya nachdi,", "Dil di dhun te har rooh nachdi,", "Ajj di raat khushiyan manaiye,", "Hassde gaunde rang jamaiye."] if roman else
                ["ढोल बजे, सारी दुनिया नाचे,", "दिल की धुन पर हर कदम नाचे,", "आज की रात खुशियाँ मनाएँ,", "हँसते-गाते रंग जमाएँ।"])

    title = topic.title()
    lines = [f"# {title}", "", f"*Style: {genre} · Mood: {mood}*", ""]
    if notes:
        lines.extend([f"*Your note: {notes}*", ""])
    lines.extend(["## ਮੁੱਖੜਾ / Chorus" if not roman and not mixed else "## Mukhda / Chorus",
                  *hook, "", "## ਅੰਤਰਾ 1 / Verse 1", *verse_a, "", "## ਮੁੱਖੜਾ / Chorus", *hook])
    verse_count = 2 if length_choice.startswith("Short") else 3 if length_choice.startswith("Medium") else 4
    for idx in range(2, verse_count + 1):
        lines.extend(["", f"## ਅੰਤਰਾ {idx} / Verse {idx}", *(verse_b if idx % 2 == 0 else bridge)])
        if idx < verse_count:
            lines.extend(["", "## ਮੁੱਖੜਾ / Chorus", *hook])
    lines.extend(["", "## Outro", bridge[0], bridge[1]])
    lines.extend(["", "> Offline template lyrics generated on this device/server with Python. No AI API or network request was used."])
    return "\n".join(lines)


def render():
    page = "Punjabi Song Generator"
    if page == 'Punjabi Song Generator':
        st.subheader('🎵 Punjabi Song Generator')
        st.write('Generate Punjabi lyrics offline with the built-in Python lyric writer. No API key or external AI service is required.')
        from core.local_ai import local_model_status
        local_status = local_model_status()
        if local_status.get('ready'):
            st.info('A local GGUF model is configured. The app will use it for richer lyrics; the offline writer remains the fallback.')
        else:
            st.caption('Offline mode is ready now. You do not need to install a model to generate template-based lyrics.')
        with st.form('punjabi_song_form'):
            song_topic = st.text_input('Song topic / story', placeholder='Example: hard work, love, village life, friendship')
            script = st.selectbox('Lyrics script', ['Punjabi (Gurmukhi)', 'Roman Punjabi (English letters)', 'Punjabi with a little Hindi'])
            genre = st.selectbox('Music style', ['Modern Punjabi pop', 'Bhangra', 'Romantic', 'Sad / emotional', 'Motivational', 'Folk', 'Hip-hop / rap', 'Sufi'])
            mood = st.selectbox('Mood', ['Energetic', 'Emotional', 'Hopeful', 'Romantic', 'Powerful', 'Peaceful'])
            length_choice = st.selectbox('Length', ['Short (1 chorus + 2 verses)', 'Medium (1 chorus + 3 verses)', 'Long (1 chorus + 4 verses)'])
            notes = st.text_area('Extra details (optional)', placeholder='Singer perspective, rhyme words, setting, clean language, hook line...')
            make_song = st.form_submit_button('Generate Punjabi Song', type='primary', use_container_width=True)
        if make_song:
            if not song_topic.strip():
                st.error('Please enter a song topic or story.')
            else:
                song_prompt = (
                    f'Write a completely original Punjabi song. Topic/story: {song_topic.strip()}. '
                    f'Language/script: {script}. Genre: {genre}. Mood: {mood}. Structure/length: {length_choice}. '
                    f'Additional requirements: {notes.strip() or "Use natural Punjabi, memorable hook, strong rhymes, singable rhythm."} '
                    'Return a title, a memorable Mukhda/Chorus, clearly labelled Antara/Verse sections, and an optional short outro. '
                    'Keep the language natural and culturally fluent; do not use placeholder lines or repeat whole verses. '
                    'Do not imitate a living artist or copy existing song lyrics. Output lyrics only, no audio.'
                )
                try:
                    with st.spinner('Writing your Punjabi song...'):
                        if local_status.get('ready'):
                            result = generate_with_gemini(
                                song_prompt,
                                system_instruction='You are an expert Punjabi lyricist. Write original, idiomatic, singable Punjabi lyrics with memorable hooks, coherent storytelling, natural rhyme and rhythm. Respect the requested script exactly.',
                            )
                        else:
                            result = _offline_lyrics(song_topic, script, genre, mood, length_choice, notes)
                    st.session_state['last_punjabi_song'] = result
                    st.success('Song lyrics generated without any external API.')
                except Exception as exc:
                    # If a local model fails to load or generate, keep the offline path usable.
                    try:
                        result = _offline_lyrics(song_topic, script, genre, mood, length_choice, notes)
                        st.session_state['last_punjabi_song'] = result
                        st.warning(f'Local model unavailable; used the offline lyric writer instead. Details: {exc}')
                    except Exception as fallback_exc:
                        st.error(f'Could not generate the song offline: {fallback_exc}')
        if st.session_state.get('last_punjabi_song'):
            st.markdown('### Your Punjabi song')
            st.markdown(st.session_state['last_punjabi_song'])
            st.download_button('Download lyrics (.txt)', st.session_state['last_punjabi_song'], file_name='punjabi_song_lyrics.txt', mime='text/plain', use_container_width=True)

            st.markdown('### 🎤 Turn these lyrics into a sung MP3')
            st.warning('Sung MP3 generation is not available offline in this version. It requires installing and running a separate local music-generation model. This button will not contact an external service.')
            mp3_style = st.selectbox(
                'Song sound',
                ['Punjabi Bhangra / upbeat pop', 'Romantic Punjabi melody', 'Sad / emotional Punjabi song',
                 'Motivational Punjabi anthem', 'Punjabi folk', 'Punjabi hip-hop / rap'],
                key='mp3_song_style'
            )
            mp3_duration = st.select_slider(
                'Approximate song length',
                options=[30, 60, 90, 120, 150, 180],
                value=120,
                format_func=lambda seconds: f'{seconds} seconds',
                key='mp3_song_duration'
            )
            st.button('🎵 Generate sung MP3 (offline model not installed)', disabled=True, use_container_width=True)
