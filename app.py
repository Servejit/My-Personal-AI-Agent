import os
import json
import ast
import operator
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
APP_NAME = 'My Personal AI Agent'
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
NOTES_FILE = DATA_DIR / 'notes.json'

st.set_page_config(page_title=APP_NAME, page_icon='🤖', layout='wide')

st.markdown('''
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1150px;}
[data-testid='stSidebar'] {border-right: 1px solid rgba(128,128,128,.2);}
.small-muted {color: #888; font-size: .9rem;}
</style>
''', unsafe_allow_html=True)


def get_gemini_api_key():
    """Read the Gemini key from environment variables or Streamlit secrets."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    try:
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        return ""

def generate_with_gemini(prompt, history=None, system_instruction=None):
    """Generate text with Gemini's API. Requires a user-provided API key."""
    import requests
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini is not connected. Create a free API key at https://aistudio.google.com/apikey, "
            "then add it to your Codespace as GEMINI_API_KEY. Do not paste the key into chat or source code."
        )
    contents = []
    for item in (history or [])[-8:]:
        if item.get("role") in ("user", "assistant") and item.get("content"):
            contents.append({
                "role": "model" if item["role"] == "assistant" else "user",
                "parts": [{"text": str(item["content"])[:12000]}],
            })
    contents.append({"role": "user", "parts": [{"text": str(prompt)[:12000]}]})
    payload = {"contents": contents, "generationConfig": {"temperature": 0.85, "maxOutputTokens": 2500}}
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
    try:
        response = requests.post(
            url, params={"key": api_key}, json=payload,
            headers={"Content-Type": "application/json"}, timeout=90
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach Gemini: {exc}") from exc
    if response.status_code != 200:
        try:
            detail = response.json().get("error", {}).get("message", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"Gemini API error ({response.status_code}): {detail}")
    try:
        data = response.json()
        parts = data["candidates"][0]["content"]["parts"]
        answer = "\\n".join(part.get("text", "") for part in parts if part.get("text"))
        if not answer.strip():
            raise RuntimeError("Gemini returned an empty response. Please try again.")
        return answer.strip()
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError("Gemini returned an unexpected response. Please try again.") from exc


def generate_sung_mp3_with_ace_step(lyrics, style, duration_seconds=120, language='Punjabi'):
    """Generate a sung song through the public ACE-Step hosted API.

    The public demo is free to try but is community-hosted and may be busy,
    sleeping, or unavailable. No API key is required by this app.
    """
    import time
    from urllib.parse import urljoin

    import requests

    base_url = "https://ace-step-ace-step-v1-5.hf.space"
    language_codes = {
        "Punjabi": "pa", "Hindi": "hi", "English": "en",
        "Spanish": "es", "Bengali": "bn",
    }
    payload = {
        "caption": (
            f"{language} song, {style}, full song with lead vocals and instrumental "
            "accompaniment, rhythmic drums, bass, polished studio mix, natural pronunciation"
        ),
        "lyrics": str(lyrics),
        "thinking": True,
        "vocal_language": language_codes.get(language, language.lower()),
        "audio_format": "mp3",
        "audio_duration": int(duration_seconds),
        "inference_steps": 8,
        "use_random_seed": True,
        "task_type": "text2music",
    }

    try:
        response = requests.post(
            f"{base_url}/v1/music/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        response.raise_for_status()
        task = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Could not submit the song to the free ACE-Step service. "
            "The public demo may be sleeping or unavailable. Try again later. "
            f"Details: {exc}"
        ) from exc
    except ValueError as exc:
        raise RuntimeError("The music service returned an invalid response.") from exc

    job_id = task.get("job_id") or task.get("task_id")
    if not job_id:
        raise RuntimeError(
            "The music service did not return a job ID. "
            f"Response: {str(task)[:500]}"
        )

    progress = None
    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        try:
            status_response = requests.get(
                f"{base_url}/v1/jobs/{job_id}", timeout=30
            )
            status_response.raise_for_status()
            status_data = status_response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"Could not check music-generation status: {exc}") from exc

        status = str(status_data.get("status", "")).lower()
        if status == "failed":
            raise RuntimeError(
                "The music service reported a generation failure: "
                + str(status_data.get("error") or status_data.get("result") or "Unknown error")[:700]
            )
        if status in {"succeeded", "success", "completed"}:
            result = status_data.get("result") or {}
            audio_path = result.get("first_audio_path")
            if not audio_path:
                paths = result.get("audio_paths") or []
                audio_path = paths[0] if paths else None
            if isinstance(audio_path, dict):
                audio_path = audio_path.get("url") or audio_path.get("path")
            if not audio_path:
                raise RuntimeError(
                    "Generation finished, but the service returned no audio path."
                )

            if str(audio_path).startswith(("http://", "https://")):
                audio_url = str(audio_path)
            else:
                audio_url = f"{base_url}/v1/audio"
                audio_response = requests.get(
                    audio_url, params={"path": str(audio_path)}, timeout=180
                )
                audio_response.raise_for_status()
                if not audio_response.content:
                    raise RuntimeError("The generated audio download was empty.")
                return audio_response.content

            audio_response = requests.get(audio_url, timeout=180)
            audio_response.raise_for_status()
            if not audio_response.content:
                raise RuntimeError("The generated audio download was empty.")
            return audio_response.content

        # Surface a useful error if the service uses an unexpected status.
        if status and status not in {"queued", "running", "pending", "processing"}:
            raise RuntimeError(
                f"Unexpected music job status: {status}. "
                f"{str(status_data)[:400]}"
            )
        time.sleep(3)

    raise RuntimeError(
        "Music generation took longer than 15 minutes. The public demo may be busy; please try again later."
    )


def load_notes():
    try:
        if NOTES_FILE.exists():
            data = json.loads(NOTES_FILE.read_text(encoding='utf-8'))
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        pass
    return []

def save_notes(notes):
    NOTES_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding='utf-8')

def safe_calculate(expression):
    '''Evaluate basic arithmetic only; never execute arbitrary Python.'''
    allowed_ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}
    def walk(node):
        if isinstance(node, ast.Expression): return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 8: raise ValueError('Powers above 8 are not allowed.')
            result = allowed_ops[type(node.op)](left, right)
            if abs(result) > 1e100: raise ValueError('Result is too large.')
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops: return allowed_ops[type(node.op)](walk(node.operand))
        raise ValueError('Use numbers and basic operators only: + - * / // % ** and parentheses.')
    if len(expression) > 120: raise ValueError('Expression is too long.')
    return walk(ast.parse(expression, mode='eval'))

def dataframe_summary(df):
    lines = [f'Rows: {len(df):,}', f'Columns: {len(df.columns):,}', 'Column names: ' + ', '.join(str(c) for c in df.columns[:60])]
    if len(df.columns) > 60: lines.append('(Only the first 60 column names are shown.)')
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if not missing.empty:
        lines.append('\nMissing values by column:')
        lines.extend(f'- {col}: {int(count)}' for col, count in missing.head(20).items())
    numeric = df.select_dtypes(include='number')
    if not numeric.empty:
        lines.append('\nNumeric summary:')
        lines.append(numeric.describe().round(3).to_string())
    return '\n'.join(lines)

if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'pending_action' not in st.session_state: st.session_state.pending_action = None
if 'notes' not in st.session_state: st.session_state.notes = load_notes()

with st.sidebar:
    st.title('🤖 Personal Agent')
    st.caption('Free-first • Human approval for important actions')
    page = st.radio('Workspace', ['Chat', 'AI Music Studio', 'Punjabi Song Generator', 'File Analyst', 'Calculator', 'Notes & Tasks', 'Settings'], label_visibility='collapsed')
    st.divider()
    st.markdown('**Current capabilities**')
    st.write('✓ AI music studio: lyrics + sung MP3')
    st.write('✓ Basic conversational helper')
    st.write('✓ CSV / Excel analysis')
    st.write('✓ Safe arithmetic calculator')
    st.write('✓ Local notes and task list')
    st.write('✓ Confirmation before deleting notes')
    st.caption('Gemini AI: connected' if get_gemini_api_key() else 'Gemini AI: API key needed')

st.title('🤖 My Personal AI Agent')
st.caption('Punjabi song writing and chat use Gemini when GEMINI_API_KEY is configured. The Gemini API offers a limited free tier; usage limits and availability can change.')

if page == 'Chat':
    st.subheader('Chat with your assistant')
    if get_gemini_api_key():
        st.success('AI model connected through Gemini.')
    else:
        st.warning('AI model not connected yet. Add GEMINI_API_KEY in Codespaces Secrets to enable chat and Punjabi song writing.')
        st.markdown('[Get a Gemini API key](https://aistudio.google.com/apikey) · The API has a limited free tier; check current limits before use.')
    for item in st.session_state.chat_history:
        with st.chat_message(item['role']): st.markdown(item['content'])
    prompt = st.chat_input('Ask a question or request a Punjabi song')
    if prompt:
        st.session_state.chat_history.append({'role': 'user', 'content': prompt})
        low = prompt.lower().strip()
        if low.startswith('calculate '):
            try: response = f'Result: **{safe_calculate(prompt[10:].strip())}**'
            except Exception as exc: response = f'I could not calculate that: {exc}'
        elif low in {'help', '/help'}:
            response = 'Ask me a question, request a Punjabi song, or use Punjabi Song Generator. You can also use the built-in calculator, File Analyst, and Notes & Tasks.'
        else:
            try:
                with st.spinner('Thinking...'):
                    response = generate_with_gemini(
                        prompt,
                        history=st.session_state.chat_history[:-1],
                        system_instruction=(
                            'You are a helpful personal assistant. You are especially good at writing original Punjabi songs. '
                            'When asked for Punjabi lyrics, follow the requested script: Gurmukhi Punjabi or Roman Punjabi. '
                            'Use natural, idiomatic Punjabi, a clear song structure (Mukhda/Chorus and Antara/Verses), '
                            'consistent rhyme and rhythm, and avoid translating word-for-word from English. '
                            'Do not claim you have generated audio; provide lyrics only unless asked otherwise. If the user asks for a sung MP3, music, beats, or audio generation, explain briefly that chat is text-only and direct them to the separate Punjabi Song Generator page and its Generate sung MP3 button. Do not tell them they must use Suno or Udio, because the app includes a best-effort free MP3 generation feature.'
                        ),
                    )
            except Exception as exc:
                response = f'**AI connection problem**\n\n{exc}'
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        st.rerun()
    if st.button('Clear chat history', use_container_width=True): st.session_state.pending_action = {'type': 'clear_chat'}
    if st.session_state.pending_action and st.session_state.pending_action.get('type') == 'clear_chat':
        st.warning('Confirm clearing this chat history?')
        yes, no = st.columns(2)
        with yes:
            if st.button('Confirm clear', type='primary', use_container_width=True):
                st.session_state.chat_history = []; st.session_state.pending_action = None; st.rerun()
        with no:
            if st.button('Cancel', use_container_width=True): st.session_state.pending_action = None; st.rerun()


elif page == 'Punjabi Song Generator':
    st.subheader('🎵 Punjabi Song Generator')
    st.write('Write original Punjabi lyrics, then use the sung-MP3 generator below to create vocals and instrumental accompaniment.')
    if not get_gemini_api_key():
        st.warning('Connect Gemini first to generate songs.')
        st.markdown('1. Open [Google AI Studio API keys](https://aistudio.google.com/apikey).')
        st.markdown('2. Create an API key using the free tier if available for your account.')
        st.markdown('3. In your GitHub Codespace, open the **Secrets** panel and add a secret named `GEMINI_API_KEY` with your key as its value.')
        st.markdown('4. Restart the Streamlit app. Never put the key in app.py or a public GitHub file.')
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
        elif not get_gemini_api_key():
            st.error('Gemini API key is missing. Follow the setup steps above.')
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
        st.write('This uses the public open-source ACE-Step music demo. It attempts to sing your lyrics with music and beats. The demo is free to try, but its queue and availability are controlled by its host; no free uptime is guaranteed.')
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
                st.markdown('[Open ACE-Step music demo directly](https://huggingface.co/spaces/ACE-Step/Ace-Step-v1.5)')
        if st.session_state.get('last_song_mp3'):
            st.audio(st.session_state['last_song_mp3'], format='audio/mpeg')
            st.download_button(
                '⬇️ Download sung song (.mp3)',
                data=st.session_state['last_song_mp3'],
                file_name='punjabi_song.mp3',
                mime='audio/mpeg',
                use_container_width=True
            )


elif page == 'AI Music Studio':
    st.subheader('🎧 AI Music Studio')
    st.markdown('Create a song from an idea, similar to an AI music studio: describe the song, choose a genre and language, generate or paste lyrics, then request a sung MP3 with vocals and accompaniment.')
    st.info('Audio is generated by a public ACE-Step demo. It is free to try, but may be slow, queued, or unavailable. This is not an official Suno service and cannot guarantee Suno-level results.')

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


elif page == 'File Analyst':
    st.subheader('File Analyst')
    st.write('Upload a CSV or Excel workbook. Files are processed by this app and are not automatically sent to an external AI service.')
    uploaded = st.file_uploader('Choose a file', type=['csv', 'xlsx', 'xls'])
    if uploaded:
        try:
            if uploaded.name.lower().endswith('.csv'): df = pd.read_csv(uploaded)
            else:
                workbook = pd.ExcelFile(uploaded)
                selected_sheet = st.selectbox('Select worksheet', workbook.sheet_names)
                df = pd.read_excel(workbook, sheet_name=selected_sheet)
            st.success('File loaded successfully.')
            m1, m2, m3 = st.columns(3)
            m1.metric('Rows', f'{len(df):,}'); m2.metric('Columns', f'{len(df.columns):,}'); m3.metric('Missing cells', f'{int(df.isna().sum().sum()):,}')
            st.dataframe(df.head(100), use_container_width=True)
            with st.expander('Summary and data quality'): st.text(dataframe_summary(df))
            numeric_columns = df.select_dtypes(include='number').columns.tolist()
            if numeric_columns:
                selected_numeric = st.selectbox('Numeric column to analyze', numeric_columns)
                values = pd.to_numeric(df[selected_numeric], errors='coerce').dropna()
                if not values.empty:
                    a, b, c, d = st.columns(4)
                    a.metric('Average', f'{values.mean():,.4f}'); b.metric('Median', f'{values.median():,.4f}'); c.metric('Minimum', f'{values.min():,.4f}'); d.metric('Maximum', f'{values.max():,.4f}')
            st.download_button('Download current sheet as CSV', df.to_csv(index=False).encode('utf-8'), file_name='analyzed_data.csv', mime='text/csv')
        except Exception as exc: st.error(f'Could not read this file: {exc}')

elif page == 'Calculator':
    st.subheader('Safe Calculator')
    st.write('Supports numbers, parentheses, +, -, *, /, //, %, and **. Arbitrary Python code is not executed.')
    expression = st.text_input('Expression', placeholder='(125 * 8) / 4')
    if st.button('Calculate', type='primary'):
        try:
            result = safe_calculate(expression)
            st.success(f'Result: {result:,}' if isinstance(result, int) else f'Result: {result}')
        except Exception as exc: st.error(str(exc))

elif page == 'Notes & Tasks':
    st.subheader('Notes & Tasks')
    with st.form('add_note_form', clear_on_submit=True):
        title = st.text_input('Title', placeholder='Example: Learn AI agents')
        body = st.text_area('Details (optional)')
        kind = st.selectbox('Type', ['Task', 'Note', 'Idea'])
        submitted = st.form_submit_button('Add')
    if submitted:
        if not title.strip(): st.error('Please enter a title.')
        else:
            st.session_state.notes.append({'id': datetime.now().strftime('%Y%m%d%H%M%S%f'), 'title': title.strip(), 'body': body.strip(), 'kind': kind, 'created_at': datetime.now().isoformat(timespec='seconds'), 'done': False})
            save_notes(st.session_state.notes); st.success('Saved.'); st.rerun()
    if not st.session_state.notes: st.caption('No notes or tasks yet.')
    for note in list(st.session_state.notes):
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"**{note.get('title', 'Untitled')}** · {note.get('kind', 'Note')}")
                if note.get('body'): st.write(note['body'])
                st.caption(f"Created: {note.get('created_at', '')}")
            with c2:
                new_done = st.checkbox('Done', value=bool(note.get('done')), key=f"done_{note['id']}")
                if new_done != bool(note.get('done')): note['done'] = new_done; save_notes(st.session_state.notes); st.rerun()
                if st.button('Delete', key=f"delete_{note['id']}"): st.session_state.pending_action = {'type': 'delete_note', 'id': note['id']}
            pending = st.session_state.pending_action
            if pending and pending.get('type') == 'delete_note' and pending.get('id') == note['id']:
                st.warning('Delete this item permanently from the saved notes file?')
                yes, no = st.columns(2)
                with yes:
                    if st.button('Confirm delete', key=f"confirm_delete_{note['id']}", type='primary'):
                        st.session_state.notes = [n for n in st.session_state.notes if n['id'] != note['id']]
                        save_notes(st.session_state.notes); st.session_state.pending_action = None; st.rerun()
                with no:
                    if st.button('Cancel delete', key=f"cancel_delete_{note['id']}"): st.session_state.pending_action = None; st.rerun()

elif page == 'Settings':
    st.subheader('Settings and privacy')
    st.markdown('''
- **AI provider:** Not configured yet. No paid API is called by this starter app.
- **File handling:** Uploaded files are analyzed in memory; do not upload sensitive data to a public deployment.
- **Notes:** Saved to `data/notes.json` in the app working directory. Hosted deployments may not preserve local files across restarts.
- **Approval:** Deleting saved notes and clearing chat history require confirmation.
- **Secrets:** Never paste API keys or passwords into source code or public GitHub files. Use Codespaces or deployment secrets when needed.
''')
    st.markdown('### Environment')
    st.write(f'Python version: `{os.sys.version.split()[0]}`')
    st.write(f"Gemini API key configured: {'Yes' if get_gemini_api_key() else 'No'}")
    st.markdown('To connect the model, create a key at [Google AI Studio](https://aistudio.google.com/apikey), then add it as the Codespaces secret **GEMINI_API_KEY**. Do not commit the key to GitHub.')
    st.caption('The Gemini API has a limited free tier for eligible models/accounts; quotas and terms may change. Check Google AI Studio pricing and limits before use.')

st.divider()
st.caption('Personal AI Agent starter • Built-in tools run in the app • Important actions require confirmation')
