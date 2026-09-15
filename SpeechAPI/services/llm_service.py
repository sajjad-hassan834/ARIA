import json
import logging
import os
import re
import urllib.request
import urllib.error

import config

logger = logging.getLogger("speech_api.llm")

try:
    import ollama  # type: ignore
except ImportError:
    ollama = None
    logger.warning("The 'ollama' Python package is not installed. LLM fallback via Ollama disabled.")

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
- "mujhe youtube dekhna hai" → open_youtube
- "awaz zyada karo" → volume_up
- "screen ka photo lo" → screenshot
- "google par search karo" → search_web
- "copy kar do" → copy
- "computer band karo" → shutdown

Return ONLY valid JSON, nothing else:
{
  "intent": "intent_name",
  "confidence": 0.95,
  "language": "english/roman_urdu/urdu",
  "parameters": {},
  "response": "Got it!"
}"""

_FALLBACK = {
    "intent": "unknown",
    "confidence": 0.0,
    "language": "unknown",
    "parameters": {},
    "response": "Could not understand command",
}


def check_ollama_status_sync() -> bool:
    """Synchronous check if Ollama daemon is reachable."""
    try:
        url = f"{config.OLLAMA_HOST}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            return resp.status == 200
    except Exception:
        return False


async def check_ollama_status() -> bool:
    """Non-blocking check if Ollama server is running."""
    import asyncio
    return await asyncio.to_thread(check_ollama_status_sync)


def _classify_via_openai(text: str) -> dict | None:
    """Classify intent using OpenAI GPT-4o-mini. Returns None if unavailable."""
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


def _classify_via_ollama(text: str) -> dict | None:
    """Classify intent using phi3:mini via Ollama. Returns None if unavailable."""
    if ollama is None:
        return None
    try:
        client = ollama.Client(host=config.OLLAMA_HOST)
        response = client.chat(
            model=config.OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Command: {text}"},
            ],
            # NOTE: Do NOT use format='json' with phi3:mini — it returns empty
            # content and causes "model output must contain output text" error.
            options={"temperature": 0.1, "num_predict": 150},
        )
        raw = response["message"]["content"].strip()
        if not raw:
            logger.warning("phi3:mini returned empty content in llm_service")
            return None

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group())
    except Exception as e:
        logger.warning(f"Ollama classification failed: {e}")
        return None


def classify_intent_llm(text: str) -> dict:
    """
    Classify user intent using LLM with priority:
      1. OpenAI GPT-4o-mini (fast, reliable JSON)
      2. phi3:mini via Ollama (local fallback, NO format='json')
      3. Return unknown fallback
    """
    # 1. Try OpenAI
    result = _classify_via_openai(text)
    if result and result.get("intent") and result["intent"] != "unknown":
        return result

    # 2. Try Ollama
    result = _classify_via_ollama(text)
    if result and result.get("intent") and result["intent"] != "unknown":
        return result

    return _FALLBACK
