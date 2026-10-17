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
    page = st.radio('Workspace', ['Chat', 'File Analyst', 'Calculator', 'Notes & Tasks', 'Settings'], label_visibility='collapsed')
    st.divider()
    st.markdown('**Current capabilities**')
    st.write('✓ Basic conversational helper')
    st.write('✓ CSV / Excel analysis')
    st.write('✓ Safe arithmetic calculator')
    st.write('✓ Local notes and task list')
    st.write('✓ Confirmation before deleting notes')
    st.caption('A language-model connection is not configured yet.')

st.title('🤖 My Personal AI Agent')
st.caption('A starter workspace you can extend step by step. No paid AI API is required for the built-in tools.')

if page == 'Chat':
    st.subheader('Chat with your assistant')
    st.info('This first version includes local tools and a basic helper, but does not yet have an AI language model connected. The next step will be adding a genuinely free/local model option.')
    for item in st.session_state.chat_history:
        with st.chat_message(item['role']): st.markdown(item['content'])
    prompt = st.chat_input('Ask me something, or try: calculate 125 * 8')
    if prompt:
        st.session_state.chat_history.append({'role': 'user', 'content': prompt})
        low = prompt.lower().strip()
        if low.startswith('calculate '):
            try: response = f'Result: **{safe_calculate(prompt[10:].strip())}**'
            except Exception as exc: response = f'I could not calculate that: {exc}'
        elif low in {'help', '/help'}:
            response = 'Try calculate 125 * 8, upload a spreadsheet in File Analyst, or add a note in Notes & Tasks. A generative AI model is not connected yet.'
        elif any(word in low for word in ['hello', 'hi', 'hey', 'sat sri akal', 'namaste']):
            response = 'Hello! I am your personal agent starter. I can use the built-in calculator, analyze a file, and manage notes. What would you like to try?'
        else:
            response = 'I received your message, but a language model is not connected yet, so I cannot provide a full AI-generated answer. Use Calculator, File Analyst, and Notes & Tasks from the sidebar. We will add a free/local AI model in a later step.'
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
    st.write(f"OPENAI_API_KEY configured: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    st.caption('This starter does not use OPENAI_API_KEY; the indicator only checks whether that environment variable exists.')

st.divider()
st.caption('Personal AI Agent starter • Built-in tools run in the app • Important actions require confirmation')
