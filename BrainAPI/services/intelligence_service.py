import json
import logging
import os
import re

logger = logging.getLogger("intelligence_service")

# ---------------------------------------------------------------------------
# System Prompt (shared by both OpenAI and Ollama paths)
# ---------------------------------------------------------------------------
THINK_REASON_ACT_PROMPT = """You are ARIA - Advanced Resilient Intelligence Agent.
You have the ability to THINK, REASON, and ACT.

Available actions you can perform:
BROWSER ACTIONS:
- open_url: Open any website
- search_youtube: Search on YouTube  
- search_google: Search on Google
- open_whatsapp_web: Open WhatsApp Web
- open_gmail: Open Gmail
- open_facebook: Open Facebook

DESKTOP ACTIONS:
- open_notepad: Open Notepad
- open_calculator: Open Calculator
- open_explorer: Open File Explorer
- take_screenshot: Take screenshot
- volume_up/volume_down/mute: Control volume
- type_text: Type any text

FILE ACTIONS:
- create_file: Create a new file
- create_folder: Create folder
- open_file: Open a file
- list_files: List files in folder

SYSTEM ACTIONS:
- lock_screen: Lock computer
- shutdown: Shutdown computer
- restart: Restart computer

When user gives a command, you must:
1. THINK: What does the user want?
2. REASON: What is the best way to do it using available actions?
3. ACT: Create a step-by-step plan

User has a Windows laptop. Use existing browser (do not open new windows).
User may speak in English, Urdu, or Roman Urdu.

Roman Urdu examples:
- "youtube kholo" = open YouTube
- "google par search karo" = search on Google
- "notepad kholo" = open Notepad
- "screenshot lo" = take screenshot
- "computer band karo" = shutdown
- "awaz barha do" = volume up
- "koi bhi gaana chalao" = search music on YouTube

Return ONLY this JSON format, nothing else:
{
  "thinking": "What I understood from the command",
  "reasoning": "Why I chose these steps",
  "intent": "main_intent_name",
  "api_route": "browser_api OR desktop_api OR file_api",
  "port": 8002,
  "steps": [
    {"step": 1, "action": "action_name", "target": "url_or_value", "query": "search_query"}
  ],
  "response": "Short confirmation message in same language as user",
  "confidence": 0.95
}"""


# ---------------------------------------------------------------------------
# Route normalizer (shared)
# ---------------------------------------------------------------------------
def _normalize_route(result: dict) -> dict:
    """Normalize api_route and port to valid values."""
    result.setdefault("input", "")
    result.setdefault("estimated_time", "1.0s")

    route = str(result.get("api_route", "browser_api")).lower().strip()
    if any(k in route for k in ["browser", "youtube", "google", "web", "url", "internet", "search", "gmail", "whatsapp"]):
        result["api_route"] = "browser_api"
        result["port"] = 8002
    elif any(k in route for k in ["desktop", "system", "app", "screen", "volume", "power", "notepad", "calculator", "explorer"]):
        result["api_route"] = "desktop_api"
        result["port"] = 8003
    elif any(k in route for k in ["file", "folder", "directory"]):
        result["api_route"] = "file_api"
        result["port"] = 8004
    else:
        result["api_route"] = "browser_api"
        result["port"] = 8002

    return result


# ---------------------------------------------------------------------------
# OpenAI path — GPT-4o-mini (primary, fast, cheap, reliable JSON output)
# ---------------------------------------------------------------------------
def _plan_with_openai(user_command: str) -> dict | None:
    """Try to plan using OpenAI GPT-4o-mini. Returns None if unavailable."""
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
                {"role": "system", "content": THINK_REASON_ACT_PROMPT},
                {"role": "user", "content": f"Command: {user_command}"},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 300,
        }

        with httpx.Client(timeout=10.0) as client:
            resp = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if resp.status_code != 200:
            logger.warning(f"OpenAI returned HTTP {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        raw = data["choices"][0]["message"]["content"].strip()

        if not raw:
            logger.warning("OpenAI returned empty content")
            return None

        result = json.loads(raw)
        result["input"] = user_command
        return _normalize_route(result)

    except Exception as e:
        logger.warning(f"OpenAI plan failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Ollama path — phi3:mini (fallback, local, no JSON format mode)
# ---------------------------------------------------------------------------
def _plan_with_ollama(user_command: str) -> dict | None:
    """Try to plan using phi3:mini via Ollama. Returns None if unavailable."""
    try:
        import ollama  # type: ignore
        response = ollama.chat(
            model="phi3:mini",
            messages=[
                {"role": "system", "content": THINK_REASON_ACT_PROMPT},
                {"role": "user", "content": f"Command: {user_command}"},
            ],
            # NOTE: Do NOT pass format='json' — phi3:mini doesn't support it
            # and returns empty content causing the "model output must contain
            # either output text or tool calls" error.
            options={
                "temperature": 0.1,
                "num_predict": 300,
            },
        )

        raw = response["message"]["content"].strip()
        if not raw:
            logger.warning("phi3:mini returned empty content — skipping Ollama path")
            return None

        # Extract JSON from free-text output
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning(f"No JSON found in phi3:mini output: {raw[:100]}")
            return None

        result = json.loads(match.group())
        result["input"] = user_command
        return _normalize_route(result)

    except Exception as e:
        logger.warning(f"Ollama/phi3:mini plan failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def intelligent_plan(user_command: str) -> dict:
    """
    Generate an intelligent execution plan.

    Priority:
      1. OpenAI GPT-4o-mini  — fast, reliable JSON, uses user's API key
      2. phi3:mini via Ollama — local fallback (no format='json')
      3. Rule-based fallback  — always works, no LLM required
    """
    # 1. Try OpenAI first (primary)
    result = _plan_with_openai(user_command)
    if result:
        logger.info(f"Plan generated by OpenAI GPT-4o-mini for: '{user_command}'")
        return result

    # 2. Try Ollama phi3:mini (local fallback)
    result = _plan_with_ollama(user_command)
    if result:
        logger.info(f"Plan generated by phi3:mini (Ollama) for: '{user_command}'")
        return result

    # 3. Rule-based fallback — zero LLM cost, always available
    logger.info(f"Using rule-based fallback for: '{user_command}'")
    return fallback_plan(user_command)


def fallback_plan(command: str) -> dict:
    """Simple robust fallback if both LLM paths fail or are slow."""
    command_lower = command.lower()

    if any(w in command_lower for w in ["youtube", "music", "gaana", "song", "video", "chalao"]):
        query = (
            command_lower
            .replace("youtube", "").replace("par", "").replace("pe", "")
            .replace("chalao", "").replace("kholo", "").replace("play", "")
            .replace("song", "").replace("ke", "").replace("gaane", "").replace("gaana", "")
            .strip()
        )
        clean_query = query or "trending music"
        return {
            "input": command,
            "thinking": "User wants to play something on YouTube",
            "reasoning": "Opening YouTube with search query",
            "intent": "open_youtube",
            "api_route": "browser_api",
            "port": 8002,
            "steps": [{"step": 1, "action": "search_youtube", "query": clean_query, "target": clean_query}],
            "response": f"Opening YouTube for {clean_query}!",
            "confidence": 0.85,
            "estimated_time": "1.0s",
        }

    elif any(w in command_lower for w in ["google", "search", "dhundo", "search karo"]):
        query = (
            command_lower
            .replace("google", "").replace("search", "").replace("par", "")
            .replace("pe", "").replace("karo", "").replace("dhundo", "")
            .strip()
        )
        return {
            "input": command,
            "thinking": "User wants to search Google",
            "reasoning": "Opening Google search with query",
            "intent": "search_google",
            "api_route": "browser_api",
            "port": 8002,
            "steps": [{"step": 1, "action": "search_google", "query": query or "Google"}],
            "response": "Searching on Google now!",
            "confidence": 0.85,
            "estimated_time": "1.0s",
        }

    elif any(w in command_lower for w in ["notepad", "note", "likhna"]):
        return {
            "input": command,
            "thinking": "User wants to open Notepad",
            "reasoning": "Opening Notepad application",
            "intent": "open_notepad",
            "api_route": "desktop_api",
            "port": 8003,
            "steps": [{"step": 1, "action": "open_app", "target": "notepad"}],
            "response": "Opening Notepad!",
            "confidence": 0.9,
            "estimated_time": "0.5s",
        }

    elif any(w in command_lower for w in ["screenshot", "screen", "capture", "photo lo"]):
        return {
            "input": command,
            "thinking": "User wants a screenshot",
            "reasoning": "Taking screenshot",
            "intent": "screenshot",
            "api_route": "desktop_api",
            "port": 8003,
            "steps": [{"step": 1, "action": "screenshot"}],
            "response": "Taking screenshot!",
            "confidence": 0.9,
            "estimated_time": "0.5s",
        }

    elif any(w in command_lower for w in ["volume", "awaz", "sound"]):
        is_down = any(w in command_lower for w in ["down", "kam", "ghatao", "low"])
        return {
            "input": command,
            "thinking": "User wants to adjust volume",
            "reasoning": "Changing system audio volume",
            "intent": "volume_down" if is_down else "volume_up",
            "api_route": "desktop_api",
            "port": 8003,
            "steps": [{"step": 1, "action": "volume_down" if is_down else "volume_up"}],
            "response": "Volume kam kar diya hai!" if is_down else "Volume barha diya hai!",
            "confidence": 0.9,
            "estimated_time": "0.5s",
        }

    return {
        "input": command,
        "thinking": "Could not understand command",
        "reasoning": "No matching intent found",
        "intent": "unknown",
        "api_route": "brain_api",
        "port": 8001,
        "steps": [],
        "response": "Sorry, I didn't understand. Please try again.",
        "confidence": 0.0,
        "estimated_time": "0.1s",
    }
