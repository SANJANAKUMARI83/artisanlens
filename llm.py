# LLM wrapper using Google Gemini REST API (free tier via Google AI Studio).
# No SDK needed — just requests. Handles text, vision (image), and audio.
#
# Self-healing model selection: Google keeps renaming/retiring Gemini model
# ids (gemini-1.5-flash -> gemini-2.0-flash -> gemini-3.8-flash ...) and the
# newest "flash" model is often overloaded (503) on the free tier because
# everyone's demo traffic lands on it. Instead of hardcoding one name, we
# try a short list of candidates in order, and on a 404 (model doesn't
# exist) or 503 (overloaded) we automatically fall through to the next one.
# Whichever one succeeds first is cached for the rest of the process.
import os
import json
import base64
import io
import time
from PIL import Image

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Ordered oldest/most-stable -> newest. Older "-latest" aliases tend to have
# looser free-tier quota than the newest preview model, so we prefer them
# first for reliability, and still pick up new models automatically via
# the discovery step below.
FALLBACK_MODELS = [
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
    "gemini-3.8-flash",
]

AUDIO_MIME = {
    "mp3":  "audio/mp3",
    "wav":  "audio/wav",
    "m4a":  "audio/mp4",
    "ogg":  "audio/ogg",
    "webm": "audio/webm",
    "aac":  "audio/aac",
}

# Cache the model that last worked so we don't re-probe on every call.
_working_model = None
_discovered_models = None


# ── Internal helpers ──────────────────────────────────────────────────────────

def _api_key() -> str:
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        raise ValueError("GOOGLE_API_KEY is not set. Enter it in the sidebar.")
    return key


def _discover_models() -> list:
    """
    Ask Google which models actually exist right now and support
    generateContent. Used as an extra source of candidates so we're not
    solely dependent on our hardcoded FALLBACK_MODELS list staying current.
    Best-effort: returns [] on any failure.
    """
    global _discovered_models
    if _discovered_models is not None:
        return _discovered_models

    import requests
    try:
        resp = requests.get(
            f"{GEMINI_BASE}?key={_api_key()}",
            timeout=(10, 30),
        )
        resp.raise_for_status()
        models = resp.json().get("models", [])
        names = [
            m["name"].split("/")[-1]
            for m in models
            if "generateContent" in m.get("supportedGenerationMethods", [])
            and "flash" in m["name"]
        ]
        # Prefer non-preview/non-exp names first (more stable quota).
        names.sort(key=lambda n: ("preview" in n or "exp" in n, n))
        _discovered_models = names
    except Exception:
        _discovered_models = []
    return _discovered_models


def _candidate_models() -> list:
    ordered = []
    if _working_model:
        ordered.append(_working_model)
    for name in FALLBACK_MODELS:
        if name not in ordered:
            ordered.append(name)
    for name in _discover_models():
        if name not in ordered:
            ordered.append(name)
    return ordered


def _post(model: str, parts: list, system_prompt: str = ""):
    import requests

    payload: dict = {"contents": [{"parts": parts}]}
    if system_prompt:
        payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

    return requests.post(
        f"{GEMINI_BASE}/{model}:generateContent?key={_api_key()}",
        json=payload,
        timeout=(30, 120),
    )


def _call(parts: list, system_prompt: str = "") -> str:
    """
    Core Gemini REST call with automatic model fallback.
    Tries each candidate model; on 404 (model missing) or 503/429
    (overloaded/rate-limited) it moves to the next one. Any other error
    (e.g. bad request, auth) is raised immediately since retrying a
    different model won't fix it.
    """
    global _working_model

    last_error = None
    for model in _candidate_models():
        for attempt in range(2):  # one quick retry per model on 503
            resp = _post(model, parts, system_prompt)

            if resp.status_code == 200:
                try:
                    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError) as e:
                    last_error = RuntimeError(f"Unexpected Gemini response: {resp.text[:300]}")
                    break
                _working_model = model
                return text

            if resp.status_code == 404:
                last_error = RuntimeError(f"Gemini API error 404 ({model}): {resp.text[:300]}")
                break  # try next model, no point retrying same one

            if resp.status_code in (503, 429):
                last_error = RuntimeError(f"Gemini API error {resp.status_code} ({model}): {resp.text[:300]}")
                if attempt == 0:
                    time.sleep(2)  # brief pause, model may just be momentarily busy
                    continue
                break  # give up on this model, try next

            # Any other error (400, 401, 403, 500...) — not fixable by switching models.
            raise RuntimeError(f"Gemini API error {resp.status_code} ({model}): {resp.text[:300]}")

    raise last_error or RuntimeError("All Gemini model candidates failed.")


def _parse_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        lines = [l for l in text.split("\n") if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse failed: {e}\n\nRaw output:\n{raw}") from e


def _compress_image(image_bytes: bytes, max_mb: float = 4.0) -> bytes:
    """Compress image to fit within max_mb."""
    max_b = int(max_mb * 1024 * 1024)
    if len(image_bytes) <= max_b:
        return image_bytes
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        for quality in [85, 75, 65, 50]:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            if buf.tell() <= max_b:
                return buf.getvalue()
        # Still too big — shrink dimensions
        w, h = img.size
        while min(w, h) > 300:
            w, h = int(w * 0.75), int(h * 0.75)
            buf = io.BytesIO()
            img.resize((w, h), Image.LANCZOS).save(buf, format="JPEG", quality=75)
            if buf.tell() <= max_b:
                return buf.getvalue()
    except Exception:
        pass
    return image_bytes


# ── Public API ────────────────────────────────────────────────────────────────

def call_llm(user_prompt: str, system_prompt: str = "") -> str:
    """Text-only call; returns raw string."""
    return _call([{"text": user_prompt}], system_prompt)


def call_llm_json(user_prompt: str, system_prompt: str = "") -> dict:
    """Text-only call; returns parsed dict."""
    return _parse_json(call_llm(user_prompt, system_prompt))


def call_llm_vision_json(
    user_prompt: str,
    image_bytes: bytes,
    system_prompt: str = "",
) -> dict:
    """Vision call — image passed as inline base64; returns parsed dict."""
    compressed = _compress_image(image_bytes)
    b64 = base64.b64encode(compressed).decode("utf-8")

    parts = [
        {"text": user_prompt},
        {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
    ]
    return _parse_json(_call(parts, system_prompt))


def transcribe_audio(audio_bytes: bytes, filename: str = "voice.mp3") -> str:
    """
    Transcribe a voice note (Hindi or English) using Gemini's native audio understanding.
    Audio is passed inline as base64 — no file upload or separate Whisper call needed.
    """
    ext  = filename.rsplit(".", 1)[-1].lower()
    mime = AUDIO_MIME.get(ext, "audio/mp3")
    b64  = base64.b64encode(audio_bytes).decode("utf-8")

    parts = [
        {
            "text": (
                "Transcribe this audio exactly as spoken. "
                "If the speaker is using Hindi or Hinglish, write the transcription in English. "
                "Return only the transcribed text — no commentary, no labels."
            )
        },
        {"inline_data": {"mime_type": mime, "data": b64}},
    ]
    return _call(parts).strip()
