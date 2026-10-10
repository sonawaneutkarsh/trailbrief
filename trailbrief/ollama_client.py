"""Minimal Ollama client — plain HTTP, no SDK needed."""

from __future__ import annotations

import json
import urllib.request
import urllib.error


class OllamaError(RuntimeError):
    """Raised when the local model can't produce a briefing."""


def generate(
    prompt: str,
    model: str = "gemma3",
    host: str = "http://localhost:11434",
    timeout: int = 120,
) -> str:
    """Call /api/generate on a local Ollama server (non-streaming)."""
    payload = json.dumps(
        {"model": model, "prompt": prompt, "stream": False}
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{host.rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise OllamaError(
            f"could not reach Ollama at {host} — is it running? ({exc})"
        ) from exc
    except (json.JSONDecodeError, TimeoutError) as exc:
        raise OllamaError(f"bad response from Ollama: {exc}") from exc

    text = (body.get("response") or "").strip()
    if not text:
        raise OllamaError("Ollama returned an empty response")
    return text


def model_available(model: str = "gemma3", host: str = "http://localhost:11434") -> bool:
    """Quick check: is the host up and does it know this model?"""
    try:
        with urllib.request.urlopen(
            f"{host.rstrip('/')}/api/tags", timeout=5
        ) as resp:
            tags = json.loads(resp.read().decode("utf-8")).get("models", [])
    except Exception:
        return False
    names = {m.get("name", "").split(":")[0] for m in tags}
    return model.split(":")[0] in names
