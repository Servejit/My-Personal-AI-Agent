"""Copy this file to a new filename such as my_task.py.

Files starting with "_" are templates and are not loaded as tasks.
Keep imports and session-state keys local to your task where possible.
"""

import streamlit as st

TASK_NAME = "Example Task"
TASK_ICON = "🧩"


def render():
    """Render this task's own Streamlit UI."""
    st.write("This is a starter template. Copy _template.py to a new .py file.")
    st.write("Give your task a unique TASK_NAME and implement its UI inside render().")
    # Use namespaced session-state keys, e.g.:
    # key = "my_task:input"
    # value = st.text_input("Example input", key=key)
