# Independent task apps

Every built-in workspace task has its own Streamlit UI file:

- `tasks/chat/app.py`
- `tasks/ai_music_studio/app.py`
- `tasks/punjabi_song_generator/app.py`
- `tasks/file_analyst/app.py`
- `tasks/calculator/app.py`
- `tasks/notes_tasks/app.py`
- `tasks/settings/app.py`
- `tasks/poster_maker.py` (existing optional plugin)

The root `app.py` is now only the launcher. Shared reusable services (Gemini access, audio generation, notes persistence, safe calculation, and file summaries) live in `core/services.py`. This avoids copying the same helpers into every task while allowing each task's interface and workflow to be edited independently.

## Add a new built-in task

1. Create a folder under `tasks/`, such as `tasks/weather/app.py`.
2. In that file, define `TASK_NAME = "Weather"`, `TASK_ICON = "🌦️"`, and a `render()` function.
3. Import shared helpers with `from core.services import ...` as needed.
4. Add any genuinely new dependencies to the root `requirements.txt`.
5. Reload Streamlit. The launcher discovers each `tasks/*/app.py` automatically.

The app modules share the same Python process and machine; this is code organization, not a security sandbox. Keep widget keys and session-state keys unique per task.
