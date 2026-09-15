import json
import logging
import os
import re

import config

logger = logging.getLogger("speech_api.llm")

SYSTEM_PROMPT = """You are a voice command intent classifier for a desktop controller app.

Available intents:
- open_browser, open_notepad, open_calculator
- open_explorer, screenshot, volume_up, volume_down
- mute, close_window, minimize_window, maximize_window
- scroll_up, scroll_down, copy, paste, save
- shutdown, restart, lock_screen
- open_youtube, open_google, search_web, type_text
- unknown

User can speak in English, Urdu, or Roman Urdu.

Examples:
- "open youtube" → open_youtube
- "turn up volume" → volume_up
- "take a screenshot" → screenshot
- "search for AI news" → search_web
- "copy this" → copy
- "shut down computer" → shutdown

Return ONLY valid JSON in English:
{
    "intent": "open_notepad",
    "confidence": 0.95,
    "language": "en",
    "parameters": {},
    "response": "Opening Notepad"
}
"""

_FALLBACK = {
    "intent": "unknown",
    "confidence": 0.0,
    "language": "en",
    "parameters": {},
    "response": "Could not understand command. Please try again.",
}


def _classify_via_openai(text: str) -> dict | None:
    """Classify intent using OpenAI GPT-4o-mini."""
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("openai_api_key")
    if not api_key:
        return None
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Command: {text}"},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 150,
        }
        with httpx.Client(timeout=8.0) as client:
            resp = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if resp.status_code != 200:
            return None
        raw = resp.json()["choices"][0]["message"]["content"].strip()
        if not raw:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"OpenAI classification failed: {e}")
        return None


def classify_intent_llm(text: str) -> dict:
    """
    Classify user intent using OpenAI GPT-4o-mini.
    Falls back gracefully if unavailable.
    """
    result = _classify_via_openai(text)
    if result and result.get("intent") and result["intent"] != "unknown":
        return result

    return _FALLBACK
