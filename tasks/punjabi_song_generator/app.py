"""Independent Punjabi Song Generator task UI. Edit this file to change only this task."""
from core.services import *

TASK_NAME = "Punjabi Song Generator"
TASK_ICON = "🎵"


def render():
    page = "Punjabi Song Generator"
    if page == 'Punjabi Song Generator':
        st.subheader('🎵 Punjabi Song Generator')
        st.write('Write original Punjabi lyrics, then use the sung-MP3 generator below to create vocals and instrumental accompaniment.')
        from core.local_ai import local_model_status
        if not local_model_status().get('ready'):
            st.warning('Configure a local GGUF language model to generate lyrics without an external API.')
            st.markdown('[Follow LOCAL_AI.md setup instructions](https://github.com/Servejit/My-Personal-AI-Agent/blob/main/LOCAL_AI.md). External AI is disabled by default.')
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
            elif not local_model_status().get('ready'):
                st.error('Local AI is not ready. Configure LOCAL_MODEL_PATH and install requirements-local.txt; see LOCAL_AI.md.')
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
                        result = generate_with_gemini(
                            song_prompt,
                            system_instruction='You are an expert Punjabi lyricist. Write original, idiomatic, singable Punjabi lyrics with memorable hooks, coherent storytelling, natural rhyme and rhythm. Respect the requested script exactly.',
                        )
                    st.session_state['last_punjabi_song'] = result
                    st.success('Song lyrics generated.')
                except Exception as exc:
                    st.error(f'Could not generate the song: {exc}')
        if st.session_state.get('last_punjabi_song'):
            st.markdown('### Your Punjabi song')
            st.markdown(st.session_state['last_punjabi_song'])
            st.download_button('Download lyrics (.txt)', st.session_state['last_punjabi_song'], file_name='punjabi_song_lyrics.txt', mime='text/plain', use_container_width=True)
    
            st.markdown('### 🎤 Turn these lyrics into a sung MP3')
            st.write('Sung MP3 generation is disabled by default because the current implementation uses a hosted service. A fully local singing model needs separate model weights and suitable hardware; see LOCAL_AI.md.')
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
            if st.button('🎵 Generate sung MP3', type='primary', use_container_width=True):
                try:
                    with st.spinner('Generating singing and music on the free hosted demo. This may take several minutes...'):
                        st.session_state['last_song_mp3'] = generate_sung_mp3_with_ace_step(
                            st.session_state['last_punjabi_song'], mp3_style, mp3_duration
                        )
                    st.success('Your MP3 is ready.')
                except Exception as exc:
                    st.error(f'Could not generate MP3: {exc}')
                    st.caption('No external service is called unless ALLOW_EXTERNAL_AI=true is explicitly set.')
            if st.session_state.get('last_song_mp3'):
                st.audio(st.session_state['last_song_mp3'], format='audio/mpeg')
                st.download_button(
                    '⬇️ Download sung song (.mp3)',
                    data=st.session_state['last_song_mp3'],
                    file_name='punjabi_song.mp3',
                    mime='audio/mpeg',
                    use_container_width=True
                )
