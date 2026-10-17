"""Shared services used by the independent Personal AI Agent tasks."""
import os
import json
import ast
import operator
import importlib.util
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_FILE = DATA_DIR / "notes.json"

def load_task_plugins():
    """Load optional task modules from tasks/*.py without changing core tools."""
    tasks_dir = Path(__file__).resolve().parent.parent / "tasks"
    tasks_dir.mkdir(exist_ok=True)
    loaded = []
    errors = []
    reserved_names = {
        "Chat", "AI Music Studio", "Punjabi Song Generator", "File Analyst",
        "Calculator", "Notes & Tasks", "Settings",
    }
    for task_file in sorted(tasks_dir.glob("*.py")):
        if task_file.name.startswith("_") or task_file.name == "__init__.py":
            continue
        module_name = f"personal_agent_task_{task_file.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, task_file)
            if spec is None or spec.loader is None:
                raise ImportError("Could not create a module loader.")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            task_name = str(getattr(module, "TASK_NAME", "")).strip()
            render = getattr(module, "render", None)
            if not task_name:
                raise ValueError("Define a non-empty TASK_NAME in this task file.")
            if not callable(render):
                raise ValueError("Define a callable render() function in this task file.")
            if task_name.casefold() in {name.casefold() for name in reserved_names}:
                raise ValueError(f"The task name {task_name!r} is reserved for a built-in page.")
            if any(item["name"].casefold() == task_name.casefold() for item in loaded):
                raise ValueError(f"Another task already uses the name {task_name!r}.")
            loaded.append({
                "name": task_name,
                "icon": str(getattr(module, "TASK_ICON", "🧩")),
                "render": render,
                "module": module,
                "file": task_file.name,
            })
        except Exception as exc:
            errors.append(f"{task_file.name}: {exc}")
    return loaded, errors

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
