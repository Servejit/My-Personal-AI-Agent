"""Independent Chat task UI. Edit this file to change only this task."""
from core.services import *

TASK_NAME = "Chat"
TASK_ICON = "💬"
from tasks import _poster_renderer


def render():
    page = "Chat"
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
            audio_request = any(term in low for term in [
                'mp3', 'sung song', 'sung audio', 'generate audio', 'make audio',
                'create audio', 'song with voice', 'with vocals', 'sing this',
                'sing it', 'generate music', 'create music', 'make a song with',
                'ਗੀਤ ਦੀ ਆਵਾਜ਼', 'ਆਡੀਓ', 'ਐਮਪੀ3', 'ਗਾ ਕੇ'
            ])
            poster_request = any(term in low for term in [
                'poster', 'make a flyer', 'create a flyer', 'design a flyer',
                'generate a flyer', 'make an advertisement', 'create an advertisement',
                'design an ad', 'make an ad', 'create an ad'
            ])
            if poster_request:
                try:
                    poster_plugin = _poster_renderer
                    if poster_plugin is None:
                        raise RuntimeError("Poster Maker task is not loaded. Check tasks/poster_maker.py.")
                    poster_brief = {
                        "title": prompt[:100].strip(),
                        "subtitle": "",
                        "content": prompt,
                        "footer": "",
                        "theme": "Midnight blue",
                        "format": "Portrait (4:5)",
                    }
                    try:
                        brief_text = generate_with_gemini(
                            "Turn the user's command into concise, polished copy for a poster. Return ONLY valid JSON with keys title, subtitle, content, footer, theme, format. "
                            "Keep title under 8 words, subtitle under 14 words, and content concise enough for a social poster. "
                            "Preserve names, dates, prices, contact details and facts supplied by the user; never invent missing details. "
                            "Choose theme from: Midnight blue, Sunset orange, Forest green, Royal purple, Clean white. "
                            "Choose format exactly Portrait (4:5) or Square (1:1). "
                            "If the user asks for a particular colour/style, select the closest theme. "
                            "User command: " + prompt,
                            history=st.session_state.chat_history[:-1],
                            system_instruction="You are a professional poster copywriter. Return valid JSON only, with no markdown fences."
                        )
                        import re
                        match = re.search(r"\{.*\}", brief_text, flags=re.DOTALL)
                        if match:
                            parsed = json.loads(match.group(0))
                            if isinstance(parsed, dict):
                                for key in poster_brief:
                                    if parsed.get(key) is not None:
                                        poster_brief[key] = str(parsed[key]).strip()
                    except Exception:
                        # The poster still works locally if the text AI is unavailable.
                        pass
                    if poster_brief["theme"] not in {
                        "Midnight blue", "Sunset orange", "Forest green", "Royal purple", "Clean white"
                    }:
                        poster_brief["theme"] = "Midnight blue"
                    if poster_brief["format"] not in {"Portrait (4:5)", "Square (1:1)"}:
                        poster_brief["format"] = "Portrait (4:5)"
                    poster_bytes = poster_plugin._render_poster(
                        poster_brief["content"] or prompt,
                        poster_brief["title"],
                        poster_brief["subtitle"],
                        poster_brief["theme"],
                        poster_brief["format"],
                        poster_brief["footer"],
                    )
                    st.session_state["chat_generated_poster_png"] = poster_bytes
                    st.session_state["chat_generated_poster_title"] = poster_brief["title"] or "Your poster"
                    st.session_state["chat_generated_poster_command"] = prompt
                    response = "Your poster is ready below. Preview it and use Download poster (PNG) to save the generated image."
                except Exception as exc:
                    response = f"I couldn't generate the poster: {exc}"
            elif low.startswith('calculate '):
                try: response = f'Result: **{safe_calculate(prompt[10:].strip())}**'
                except Exception as exc: response = f'I could not calculate that: {exc}'
            elif low in {'help', '/help'}:
                response = 'Ask me a question, request a Punjabi song, or ask for a sung MP3 directly here. You can also use the built-in calculator, File Analyst, and Notes & Tasks.'
            elif audio_request:
                try:
                    with st.spinner('Creating lyrics and generating your sung MP3. The free public music service may take several minutes...'):
                        lyrics = generate_with_gemini(
                            'Create original, singable Punjabi song lyrics based on this user request. Use Gurmukhi Punjabi unless another language/script is explicitly requested. Include a short title, [Verse 1], [Chorus], [Verse 2], and [Bridge] if appropriate. Make the lyrics coherent, rhythmic, and suitable for singing. Do not imitate a specific artist. User request: ' + prompt,
                            history=st.session_state.chat_history[:-1],
                            system_instruction='You are a professional Punjabi songwriter. Return only an original song title and complete singable lyrics. Use natural Punjabi and a memorable chorus.'
                        )
                        st.session_state['chat_generated_song_lyrics'] = lyrics
                        audio_bytes = generate_sung_mp3_with_ace_step(
                            lyrics,
                            'Punjabi pop and folk fusion, memorable melody, lead vocals with instrumental accompaniment, polished studio mix. ' + prompt[:500],
                            120,
                            'Punjabi'
                        )
                        st.session_state['chat_generated_song_mp3'] = audio_bytes
                    response = 'Your song lyrics and sung MP3 are ready below. Use the audio player to listen and the download button to save the MP3.'
                except Exception as exc:
                    response = (
                        'I tried to create the song directly in chat, but the audio generation did not finish. '
                        'If lyrics were generated, they are shown below. You can retry your request.\n\n'
                        f'**Details:** {exc}'
                    )
            else:
                try:
                    with st.spinner('Thinking...'):
                        response = generate_with_gemini(
                            prompt,
                            history=st.session_state.chat_history[:-1],
                            system_instruction=(
                                'You are a helpful personal assistant. For all general questions, explanations, summaries, planning, coding, and other everyday tasks, respond in clear natural English by default, even if the user provides mixed-language input. '
                                'Only use another language when the user explicitly requests it or when the task itself specifically requires it, such as writing Punjabi song lyrics. '
                                'When asked for Punjabi lyrics, follow the requested script: Gurmukhi Punjabi or Roman Punjabi. Use natural, idiomatic Punjabi, a clear song structure, consistent rhyme and rhythm. '
                                'If the user explicitly asks for MP3/audio/vocals/music generation, the app handles that request directly; do not redirect them to another page. '
                                'Never claim audio was generated unless the app actually generated it.'
                            ),
                        )
                except Exception as exc:
                    response = f'**AI connection problem**\n\n{exc}'
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        if st.session_state.get('chat_generated_poster_png'):
            st.markdown("### 🖼️ Generated poster")
            st.caption(st.session_state.get('chat_generated_poster_title', 'Your poster'))
            st.image(st.session_state['chat_generated_poster_png'], use_container_width=True)
            st.download_button(
                '⬇️ Download generated poster (PNG)',
                data=st.session_state['chat_generated_poster_png'],
                file_name='ai_agent_generated_poster.png',
                mime='image/png',
                use_container_width=True,
                key='chat_generated_poster_download',
            )
        if st.session_state.get('chat_generated_song_lyrics'):
            with st.expander('🎵 Latest song lyrics', expanded=True):
                st.markdown(st.session_state['chat_generated_song_lyrics'])
                st.download_button(
                    'Download lyrics (.txt)',
                    st.session_state['chat_generated_song_lyrics'],
                    file_name='chat_song_lyrics.txt',
                    mime='text/plain',
                    key='download_chat_song_lyrics',
                    use_container_width=True
                )
        if st.session_state.get('chat_generated_song_mp3'):
            st.markdown('### 🎤 Your sung MP3')
            st.audio(st.session_state['chat_generated_song_mp3'], format='audio/mpeg')
            st.download_button(
                '⬇️ Download sung MP3',
                data=st.session_state['chat_generated_song_mp3'],
                file_name='chat_generated_song.mp3',
                mime='audio/mpeg',
                key='download_chat_song_mp3',
                use_container_width=True
            )
        if st.button('Clear chat history', use_container_width=True): st.session_state.pending_action = {'type': 'clear_chat'}
        if st.session_state.pending_action and st.session_state.pending_action.get('type') == 'clear_chat':
            st.warning('Confirm clearing this chat history?')
            yes, no = st.columns(2)
            with yes:
                if st.button('Confirm clear', type='primary', use_container_width=True):
                    st.session_state.chat_history = []; st.session_state.pending_action = None; st.rerun()
            with no:
                if st.button('Cancel', use_container_width=True): st.session_state.pending_action = None; st.rerun()
