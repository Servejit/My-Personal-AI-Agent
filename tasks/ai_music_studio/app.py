"""Independent AI Music Studio task UI. Edit this file to change only this task."""
from core.services import *

TASK_NAME = "AI Music Studio"
TASK_ICON = "🎧"


def render():
    page = "AI Music Studio"
    if page == 'AI Music Studio':
        st.subheader('🎧 AI Music Studio')
        st.markdown('Create a song from an idea, similar to an AI music studio: describe the song, choose a genre and language, generate or paste lyrics, then request a sung MP3 with vocals and accompaniment.')
        st.info('Local text generation requires a GGUF model. Sung MP3 generation currently uses a hosted ACE-Step service and is disabled by default; a local singing model requires separate large model weights and suitable hardware. See LOCAL_AI.md.')
    
        with st.form('ai_music_studio_form'):
            music_idea = st.text_area('Describe your song', placeholder='Example: A powerful Punjabi motivational anthem about a young person overcoming hardship, with dhol, tumbi, modern bass and a memorable chorus.', height=100)
            music_language = st.selectbox('Song language', ['Punjabi', 'Hindi', 'English', 'Bengali', 'Spanish'])
            music_genre = st.selectbox('Genre / sound', ['Punjabi Bhangra pop', 'Bollywood cinematic', 'Romantic ballad', 'Sad acoustic', 'Motivational anthem', 'Folk', 'Hip-hop / rap', 'EDM pop', 'Rock', 'Lo-fi chill'])
            music_mood = st.selectbox('Mood', ['Energetic', 'Romantic', 'Emotional', 'Hopeful', 'Powerful', 'Peaceful', 'Dark / dramatic'])
            music_voice = st.selectbox('Vocal arrangement', ['Lead vocal with backing harmonies', 'Male-sounding lead vocal', 'Female-sounding lead vocal', 'Duet', 'Mostly instrumental with light vocals'])
            music_duration = st.select_slider('Approximate duration', options=[30, 60, 90, 120, 150, 180], value=120, format_func=lambda seconds: f'{seconds} seconds')
            lyrics_mode = st.radio('Lyrics', ['Write lyrics from my idea', 'I will provide my own lyrics'], horizontal=False)
            custom_lyrics = st.text_area('Your lyrics (used when the second option is selected)', placeholder='Paste lyrics here, including verse and chorus labels.', height=140)
            make_full_song = st.form_submit_button('🎵 Create full song (lyrics + music)', type='primary', use_container_width=True)
    
        if make_full_song:
            if not music_idea.strip() and not (lyrics_mode == 'I will provide my own lyrics' and custom_lyrics.strip()):
                st.error('Describe your song or paste lyrics first.')
            elif lyrics_mode == 'I will provide my own lyrics' and not custom_lyrics.strip():
                st.error('Please paste your lyrics.')
            elif lyrics_mode == 'Write lyrics from my idea' and not get_gemini_api_key():
                st.error('To write lyrics automatically, add GEMINI_API_KEY in Codespaces Secrets. Or select “I will provide my own lyrics” and paste lyrics yourself.')
            else:
                lyrics_result = custom_lyrics.strip()
                if lyrics_mode == 'Write lyrics from my idea':
                    lyric_prompt = (
                        f'Write completely original, singable {music_language} song lyrics for this concept: {music_idea.strip()}. '
                        f'Genre: {music_genre}. Mood: {music_mood}. Vocal arrangement: {music_voice}. '
                        'Return a short title and clearly labelled sections such as [Verse 1], [Chorus], [Verse 2], [Bridge]. '
                        'Use a memorable repeated chorus, natural language, singable rhythm and a coherent story. '
                        'Do not imitate any specific living artist or copy existing song lyrics. Output only title and lyrics.'
                    )
                    try:
                        with st.spinner('Writing original lyrics...'):
                            lyrics_result = generate_with_gemini(
                                lyric_prompt,
                                system_instruction='You are a professional multilingual songwriter. Write original, natural, singable lyrics in the requested language and script. Keep the chorus memorable and avoid filler.'
                            )
                    except Exception as exc:
                        st.error(f'Could not write lyrics: {exc}')
                        lyrics_result = ''
                if lyrics_result:
                    st.session_state['studio_last_lyrics'] = lyrics_result
                    style_prompt = f'{music_genre}, {music_mood} mood, {music_voice}, full song with vocals and instrumental accompaniment, professional balanced mix. Song idea: {music_idea.strip()}'
                    try:
                        with st.spinner('Generating the sung song. The public demo may take several minutes...'):
                            st.session_state['studio_last_mp3'] = generate_sung_mp3_with_ace_step(
                                lyrics_result, style_prompt, music_duration, music_language
                            )
                        st.success('Song generation finished.')
                    except Exception as exc:
                        st.error(f'Lyrics are ready, but audio generation failed: {exc}')
                        st.markdown('[Open the public ACE-Step music demo](https://huggingface.co/spaces/ACE-Step/Ace-Step-v1.5)')
    
        if st.session_state.get('studio_last_lyrics'):
            st.markdown('### Lyrics')
            st.markdown(st.session_state['studio_last_lyrics'])
            st.download_button('Download lyrics (.txt)', st.session_state['studio_last_lyrics'], file_name='ai_song_lyrics.txt', mime='text/plain', use_container_width=True)
        if st.session_state.get('studio_last_mp3'):
            st.markdown('### Your generated song')
            st.audio(st.session_state['studio_last_mp3'], format='audio/mpeg')
            st.download_button('⬇️ Download song (.mp3)', data=st.session_state['studio_last_mp3'], file_name='ai_generated_song.mp3', mime='audio/mpeg', use_container_width=True)
