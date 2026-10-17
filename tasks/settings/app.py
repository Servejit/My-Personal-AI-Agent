"""Independent Settings task UI. Edit this file to change only this task."""
from core.services import *


def render():
    page = "Settings"
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
