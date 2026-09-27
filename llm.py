# LLM wrapper using Google Gemini REST API (free tier via Google AI Studio).
# No SDK needed — just requests. Handles text, vision (image), and audio.
import os
import json
import base64
import io
from PIL import Image

GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_BASE  = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}"

AUDIO_MIME = {
    "mp3":  "audio/mp3",
    "wav":  "audio/wav",
    "m4a":  "audio/mp4",
    "ogg":  "audio/ogg",
    "webm": "audio/webm",
    "aac":  "audio/aac",
}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _api_key() -> str:
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        raise ValueError("GOOGLE_API_KEY is not set. Enter it in the sidebar.")
    return key


def _call(parts: list, system_prompt: str = "") -> str:
    """Core Gemini REST call. parts is a list of text/inline_data dicts."""
    import requests

    payload: dict = {"contents": [{"parts": parts}]}
    if system_prompt:
        payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

    resp = requests.post(
        f"{GEMINI_BASE}:generateContent?key={_api_key()}",
        json=payload,
        timeout=(30, 120),
    )
    try:
        resp.raise_for_status()
    except Exception:
        raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text[:300]}")

    try:
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response: {resp.text[:300]}") from e


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
