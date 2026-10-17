"""Independent Settings task UI. Edit this file to change only this task."""
from core.services import *

TASK_NAME = "Settings"
TASK_ICON = "⚙️"


def render():
    page = "Settings"
    if page == 'Settings':
        st.subheader('Settings and privacy')
        from core.local_ai import local_model_status
        local_status = local_model_status()
        st.markdown('''
    - **AI mode:** Local-only by default; external AI calls require explicit `ALLOW_EXTERNAL_AI=true`.
    - **Text generation:** Uses a local GGUF model when `LOCAL_MODEL_PATH` is configured.
    - **Image posters:** Rendered locally with Pillow; these are designed graphics, not photorealistic AI images.
    - **Music:** Sung MP3 generation needs a specialist model; the current hosted provider is disabled by default.
    - **File handling:** Uploaded files are analyzed in memory.
    - **Notes:** Saved to `data/notes.json`; hosted deployments may not preserve local files across rebuilds.
    - **Secrets:** Never commit keys or model weights to GitHub.
    ''')
        st.markdown('### Local model status')
        st.write('Ready' if local_status.get('ready') else 'Not configured')
        st.caption(local_status.get('reason', ''))
        if local_status.get('ready'):
            st.code(local_status.get('path', ''))
        st.markdown('### Environment')
        st.write(f'Python version: `{os.sys.version.split()[0]}`')
        st.write(f"External AI services enabled: {'Yes' if os.getenv('ALLOW_EXTERNAL_AI', '').strip().lower() in {'1', 'true', 'yes', 'on'} else 'No (local-only default)'}")
        st.markdown('Set `LOCAL_MODEL_PATH` to a downloaded GGUF file and install `requirements-local.txt` to enable local text generation. See [LOCAL_AI.md](https://github.com/Servejit/My-Personal-AI-Agent/blob/main/LOCAL_AI.md).')
        st.caption('External providers are opt-in only. Enabling them sends prompts/lyrics to those services.')
