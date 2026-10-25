"""Thin Sarvam AI client: chat (LLM) + text-to-speech.

Set SARVAM_API_KEY in your environment. Model names can be overridden:
  SARVAM_CHAT_MODEL (default: sarvam-m)
  SARVAM_TTS_MODEL  (default: bulbul:v2)
  SARVAM_TTS_SPEAKER (default: anushka)
"""
import base64
import os
import re
import time

import requests

BASE = "https://api.sarvam.ai"
CHAT_MODEL = os.getenv("SARVAM_CHAT_MODEL", "sarvam-m")
TTS_MODEL = os.getenv("SARVAM_TTS_MODEL", "bulbul:v2")
TTS_SPEAKER = os.getenv("SARVAM_TTS_SPEAKER", "anushka")

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
            r = requests.post(f"{BASE}/v1/chat/completions", json=payload, headers=_headers(), timeout=60)
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"] or ""
            # sarvam-m may emit a reasoning block
            text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
            return text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"Sarvam chat failed: {last}")


def tts(text: str, lang: str = "hindi") -> bytes:
    """Return WAV bytes for `text` spoken in `lang`."""
    code = LANG_CODES.get(lang.lower(), "hi-IN")
    payload = {
        "inputs": [text[:480]],
        "target_language_code": code,
        "speaker": TTS_SPEAKER,
        "model": TTS_MODEL,
    }
    r = requests.post(f"{BASE}/text-to-speech", json=payload, headers=_headers(), timeout=60)
    r.raise_for_status()
    return base64.b64decode(r.json()["audios"][0])
