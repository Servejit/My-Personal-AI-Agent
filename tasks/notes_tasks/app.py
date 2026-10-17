"""Independent Notes & Tasks task UI. Edit this file to change only this task."""
from core.services import *


def render():
    page = "Notes & Tasks"
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
