"""Optional fully local text inference using a downloaded GGUF model.

No model is downloaded automatically. Set LOCAL_MODEL_PATH to a local GGUF file
and install the optional llama-cpp-python dependency to enable offline generation.
"""
import os
from pathlib import Path

_model = None
_loaded_path = None

def get_local_model_path():
    value = os.getenv("LOCAL_MODEL_PATH", "").strip()
    if not value:
        return ""
    path = Path(value).expanduser()
    return str(path.resolve()) if path.is_file() else ""

def local_model_status():
    path = get_local_model_path()
    if not path:
        return {"ready": False, "reason": "LOCAL_MODEL_PATH is not set or does not point to an existing GGUF file."}
    try:
        import llama_cpp  # noqa: F401
    except ImportError:
        return {"ready": False, "reason": "llama-cpp-python is not installed. Install requirements-local.txt."}
    return {"ready": True, "reason": "Local GGUF model is available.", "path": path}

def generate_local_text(prompt, history=None, system_instruction=None, max_tokens=1200):
    """Run a prompt locally. The prompt and history are not sent to an AI API."""
    global _model, _loaded_path
    status = local_model_status()
    if not status["ready"]:
        raise RuntimeError(
            "Local AI model is not ready. " + status["reason"] +
            " See LOCAL_AI.md for setup. External AI APIs are disabled by default."
        )
    path = status["path"]
    if _model is None or _loaded_path != path:
        from llama_cpp import Llama
        # CPU-friendly default; users can adjust LOCAL_N_CTX for their machine.
        n_ctx = int(os.getenv("LOCAL_N_CTX", "4096"))
        _model = Llama(model_path=path, n_ctx=max(1024, min(n_ctx, 8192)), n_threads=max(1, int(os.getenv("LOCAL_N_THREADS", str(os.cpu_count() or 2)))), verbose=False)
        _loaded_path = path
    messages = [{"role": "system", "content": system_instruction or "You are a helpful personal assistant. Be accurate, clear, and concise."}]
    for item in (history or [])[-8:]:
        role = item.get("role")
        content = str(item.get("content", "")).strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content[:6000]})
    messages.append({"role": "user", "content": str(prompt)[:12000]})
    result = _model.create_chat_completion(
        messages=messages,
        temperature=0.7,
        max_tokens=max(64, min(int(max_tokens), 2048)),
    )
    answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not str(answer).strip():
        raise RuntimeError("The local model returned an empty response.")
    return str(answer).strip()
