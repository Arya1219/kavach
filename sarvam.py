"""Thin Sarvam AI client: chat (LLM) + text-to-speech.

Set SARVAM_API_KEY in your environment. Model names can be overridden:
  SARVAM_CHAT_MODEL  (default: sarvam-105b-conversations)
  SARVAM_TTS_MODEL   (default: bulbul:v4-flash)
  SARVAM_TTS_SPEAKER (default: unset -> Sarvam's default voice)
"""
import base64
import os
import re
import time

import requests

BASE = "https://api.sarvam.ai"
CHAT_MODEL = os.getenv("SARVAM_CHAT_MODEL", "sarvam-105b-conversations")
TTS_MODEL = os.getenv("SARVAM_TTS_MODEL", "bulbul:v4-flash")
TTS_SPEAKER = os.getenv("SARVAM_TTS_SPEAKER", "")

LANG_CODES = {
    "hindi": "hi-IN",
    "hinglish": "hi-IN",
    "tamil": "ta-IN",
    "bengali": "bn-IN",
    "marathi": "mr-IN",
    "telugu": "te-IN",
    "kannada": "kn-IN",
    "malayalam": "ml-IN",
    "gujarati": "gu-IN",
    "punjabi": "pa-IN",
}


def have_key() -> bool:
    return bool(os.getenv("SARVAM_API_KEY"))


def _headers():
    return {
        "api-subscription-key": os.environ["SARVAM_API_KEY"],
        "Content-Type": "application/json",
    }


def _post(path, payload, timeout=60):
    r = requests.post(f"{BASE}{path}", json=payload, headers=_headers(), timeout=timeout)
    if not r.ok:
        raise RuntimeError(f"{r.status_code} {r.reason}: {r.text[:300]}")
    return r.json()


def chat(system: str, user: str, temperature: float = 0.8, max_tokens: int = 1500, retries: int = 3) -> str:
    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    last = None
    for i in range(retries):
        try:
            data = _post("/v1/chat/completions", payload)
            text = data["choices"][0]["message"]["content"] or ""
            # strip any reasoning block
            text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
            return text
        except Exception as e:  # noqa: BLE001
            last = e
            if "400" in str(e)[:5] or "422" in str(e)[:5]:
                break  # bad request will not fix itself on retry
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"Sarvam chat failed: {last}")


def _mime(path: str) -> str:
    import mimetypes
    guess = mimetypes.guess_type(path)[0]
    if guess and guess.startswith("audio"):
        return guess
    ext = os.path.splitext(path)[1].lower()
    return {".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".webm": "audio/webm",
            ".ogg": "audio/ogg", ".flac": "audio/flac", ".aac": "audio/aac"}.get(ext, "audio/wav")


def stt(path: str) -> str:
    """Transcribe an audio file (voice note / call snippet) with Sarvam speech-to-text.
    Language is auto-detected."""
    last = None
    for model in ("saaras:v4", "saaras:v3"):
        try:
            with open(path, "rb") as f:
                r = requests.post(
                    f"{BASE}/speech-to-text",
                    headers={"api-subscription-key": os.environ["SARVAM_API_KEY"]},
                    files={"file": (os.path.basename(path), f, _mime(path))},
                    data={"model": model, "language_code": "unknown"},
                    timeout=90,
                )
            if not r.ok:
                raise RuntimeError(f"{r.status_code} {r.reason}: {r.text[:300]}")
            return (r.json().get("transcript") or "").strip()
        except Exception as e:  # noqa: BLE001
            last = e
    raise RuntimeError(f"Sarvam STT failed: {last}")


def tts(text: str, lang: str = "hindi") -> bytes:
    """Return WAV bytes for `text` spoken in `lang`. Tries a few request shapes/models."""
    code = LANG_CODES.get(lang.lower(), "hi-IN")
    text = text[:450]
    models = [TTS_MODEL] + [m for m in ("bulbul:v3", "bulbul:v2") if m != TTS_MODEL]
    last = None
    for model in models:
        for lang_key in ("target_language_code", "language_code"):
            payload = {"text": text, lang_key: code, "model": model}
            if TTS_SPEAKER:
                payload["speaker"] = TTS_SPEAKER
            try:
                data = _post("/text-to-speech", payload)
                return base64.b64decode(data["audios"][0])
            except Exception as e:  # noqa: BLE001
                last = e
    raise RuntimeError(f"Sarvam TTS failed: {last}")
