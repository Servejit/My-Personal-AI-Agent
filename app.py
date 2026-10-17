"""Launcher for My Personal AI Agent.
Each built-in task lives in its own tasks/<task_name>/app.py module.
"""
from pathlib import Path
import importlib.util
import streamlit as st
from dotenv import load_dotenv
from core.services import get_gemini_api_key, load_task_plugins

load_dotenv()
APP_NAME = "My Personal AI Agent"
ROOT_DIR = Path(__file__).resolve().parent
st.set_page_config(page_title=APP_NAME, page_icon="🤖", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1150px;}
[data-testid='stSidebar'] {border-right: 1px solid rgba(128,128,128,.2);}
.small-muted {color: #888; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

def load_builtin_tasks():
    tasks = []
    errors = []
    tasks_root = ROOT_DIR / "tasks"
    for task_dir in sorted(tasks_root.iterdir()):
        task_file = task_dir / "app.py"
        if not task_dir.is_dir() or not task_file.is_file():
            continue
        try:
            module_name = "personal_agent_builtin_" + task_dir.name
            spec = importlib.util.spec_from_file_location(module_name, task_file)
            if spec is None or spec.loader is None:
                raise ImportError("Could not load this task module.")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            render = getattr(module, "render", None)
            if not callable(render):
                raise ValueError("The task app must define render().")
            name = str(getattr(module, "TASK_NAME", task_dir.name.replace("_", " ").title())).strip()
            icon = str(getattr(module, "TASK_ICON", "🧩"))
            tasks.append({"name": name, "icon": icon, "render": render, "file": str(task_file.relative_to(ROOT_DIR))})
        except Exception as exc:
            errors.append(f"{task_file}: {exc}")
    return tasks, errors

BUILTIN_TASKS, BUILTIN_ERRORS = load_builtin_tasks()
PLUGIN_TASKS, PLUGIN_ERRORS = load_task_plugins()
TASKS = BUILTIN_TASKS + PLUGIN_TASKS
TASK_MAP = {task["name"]: task for task in TASKS}
if len(TASK_MAP) != len(TASKS):
    st.error("Two tasks have the same name. Give every task a unique TASK_NAME.")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

with st.sidebar:
    st.title("🤖 Personal Agent")
    st.caption("Free-first • Human approval for important actions")
    page = st.radio("Workspace", list(TASK_MAP), label_visibility="collapsed")
    st.divider()
    st.markdown("**Independent task apps**")
    for task in TASKS:
        st.write(f"{task['icon']} {task['name']}")
    st.caption("Gemini AI: connected" if get_gemini_api_key() else "Gemini AI: API key needed")
    for error in BUILTIN_ERRORS + PLUGIN_ERRORS:
        st.warning(error)

st.title("🤖 My Personal AI Agent")
st.caption("Each task has its own app.py. Shared services are kept in core/services.py.")
selected = TASK_MAP[page]
st.subheader(f"{selected['icon']} {selected['name']}")
st.caption(f"Task file: {selected.get('file', 'tasks/' + page.lower().replace(' ', '_') + '.py')}")
try:
    selected["render"]()
except Exception as exc:
    st.error(f"Task '{selected['name']}' encountered an error: {exc}")
    st.info("Other tasks are separate. Fix this task's app.py and reload the app.")
st.divider()
st.caption("Personal AI Agent • Separate task apps • Shared services • Important actions require confirmation")
