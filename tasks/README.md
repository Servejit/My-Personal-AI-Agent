# Adding independent tasks

The main app automatically discovers Python task files in this folder.

## Add a task

1. Copy `_template.py` to a new file, for example `weather_task.py`.
2. In that file, set a unique `TASK_NAME` and optional `TASK_ICON`.
3. Put the task UI and logic inside its `render()` function.
4. Save and restart Streamlit (or reload the app). The task appears in the Workspace sidebar automatically.

## Required interface

```python
import streamlit as st

TASK_NAME = "My New Task"
TASK_ICON = "🧩"

def render():
    st.subheader("My New Task")
    st.write("Task-specific UI and logic go here.")
```

## Language convention

- General-purpose tasks should use clear English for labels, instructions, messages, and generated responses by default.
- Use another language only when the user explicitly requests it or the task itself specifically requires it (for example, Punjabi song lyrics).

## Isolation rules

- Keep each task in its own file. Do not edit `app.py` just to add another plugin.
- Use unique, namespaced Streamlit widget keys such as `weather_task:location`.
- Use namespaced session-state keys such as `weather_task:results`.
- Use task-specific filenames for uploads and outputs. Do not overwrite another task's files.
- Do not change shared/core functions unless a feature genuinely needs them.
- Handle expected errors inside each task's `render()` function.
- Keep API keys in Codespaces/Streamlit secrets or environment variables, never in code.
- Treat external service limits, shared CPU/RAM, and app-wide dependencies as shared resources.

A broken plugin is reported in the sidebar warnings and isolated to that task's render area where possible; it should not require changing the built-in task logic. Python modules still share the same process, so this is code organization and fault containment, not a security sandbox.
