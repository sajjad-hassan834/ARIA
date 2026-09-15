import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load from ARIA root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

logger = logging.getLogger("brain.intelligence")

# ---------------------------------------------------------------------------
# OpenAI Client
# ---------------------------------------------------------------------------
_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_api_key) if _api_key else None

# ---------------------------------------------------------------------------
# System Prompt — Full AI-driven, no hardcoding
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are ARIA - Advanced Resilient Intelligence Agent running on a Windows laptop.
You control the laptop completely via structured JSON action plans.

USER LANGUAGES: English, Urdu, Roman Urdu (Urdu written in English letters like "kholo", "chalao", "band karo")

YOUR THINKING PROCESS:
1. THINK — What does the user REALLY want? (Go beyond literal words)
2. REASON — Which tool and action will accomplish this best?
3. ACT — Create precise, ordered steps

═══════════════════════════════════════════
AVAILABLE TOOLS
═══════════════════════════════════════════

▶ browser_api (port 8002) — Web & Internet:
  • open_url      → {"action": "open_url",      "target": "https://site.com"}
  • search_youtube → {"action": "search_youtube", "query": "song artist name"}
  • search_google  → {"action": "search_google",  "query": "what to search"}

▶ desktop_api (port 8003) — Apps & System:
  • open_app     → {"action": "open_app",    "target": "notepad|calculator|paint|explorer|chrome|word|excel|powershell|cmd|vlc"}
  • close_app    → {"action": "close_app",   "target": "app name"}
  • screenshot   → {"action": "screenshot"}
  • volume_up    → {"action": "volume_up"}
  • volume_down  → {"action": "volume_down"}
  • mute         → {"action": "mute"}
  • type_text    → {"action": "type_text",   "text": "text to type"}
  • lock_screen  → {"action": "lock_screen"}
  • shutdown     → {"action": "shutdown"}
  • restart      → {"action": "restart"}

▶ file_api (port 8004) — Files & Folders:
  • create_file   → {"action": "create_file",   "name": "file.txt",   "location": "desktop|downloads|documents"}
  • create_folder → {"action": "create_folder", "name": "My Folder",  "location": "desktop|downloads|documents"}
  • list_files    → {"action": "list_files",    "location": "desktop|downloads|documents"}
  • open_file     → {"action": "open_file",     "path": "full/path/to/file"}
  • delete_file   → {"action": "delete_file",   "path": "full/path/to/file"}
  • move_file     → {"action": "move_file",     "source": "path", "destination": "path"}

═══════════════════════════════════════════
ROMAN URDU DICTIONARY
═══════════════════════════════════════════
kholo / open karo    = open
band karo            = close / shutdown
chalao / chala do    = play / run / start
dikhao / dikha do    = show / display
dhundo / search karo = search / find
screenshot lo        = take screenshot
screen pakdo         = take screenshot
awaz barha / barha do = volume up
awaz kam / kam karo  = volume down
mute karo            = mute
file banao           = create file
folder banao         = create folder
desktop par          = on desktop / to desktop
downloads mein       = in downloads folder
documents mein       = in documents folder
gaana / gaane        = song / songs / music
chalao               = play
dobara karo          = do it again / repeat
computer band karo   = shutdown computer
lock karo            = lock screen
waqt kya hai         = what time is it
kal wala             = yesterday's / the previous

═══════════════════════════════════════════
SMART CONTEXT RULES
═══════════════════════════════════════════
• "social media" → open facebook.com
• "news dekhna hai" → search_google "latest news today"
• "koi acchi film" → search_google "best movies 2024"  
• "weather check karo" → search_google "weather today [city if mentioned]"
• "YouTube par X ke gaane" → search_youtube "X songs"
• "work ke liye folder" → create_folder on desktop
• Multi-step commands → create multiple steps in order
• If user says "wahi karo phir" / "dobara" → repeat last intent

═══════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════
1. Return ONLY valid JSON — no explanation, no markdown, no prefix text
2. "response" field MUST be in the SAME LANGUAGE as user input
   - English input → English response
   - Roman Urdu input → Roman Urdu response  
   - Urdu script → Urdu script response
3. NEVER return intent "unknown" — always make your best guess
4. confidence 0.0–1.0 based on how sure you are

═══════════════════════════════════════════
RESPONSE FORMAT
═══════════════════════════════════════════
{
  "thinking": "what the user wants in one sentence",
  "reasoning": "which tool and why",
  "intent": "descriptive_snake_case_intent",
  "api_route": "browser_api OR desktop_api OR file_api",
  "port": 8002,
  "steps": [
    {"step": 1, "action": "action_name", "target": "value", "query": "if needed"}
  ],
  "response": "friendly confirmation in user's language",
  "confidence": 0.95
}

═══════════════════════════════════════════
EXAMPLES
═══════════════════════════════════════════
Input: "youtube par arijit singh ke gaane chalao"
{"thinking":"play arijit singh songs on youtube","reasoning":"search_youtube is best for music","intent":"play_music","api_route":"browser_api","port":8002,"steps":[{"step":1,"action":"search_youtube","query":"Arijit Singh songs"}],"response":"YouTube par Arijit Singh ke gaane chal rahe hain! 🎵","confidence":0.98}

Input: "open notepad"
{"thinking":"user wants notepad editor","reasoning":"open_app on desktop_api","intent":"open_notepad","api_route":"desktop_api","port":8003,"steps":[{"step":1,"action":"open_app","target":"notepad"}],"response":"Opening Notepad!","confidence":1.0}

Input: "notepad kholo"
{"thinking":"user wants notepad in Roman Urdu","reasoning":"open_app on desktop_api","intent":"open_notepad","api_route":"desktop_api","port":8003,"steps":[{"step":1,"action":"open_app","target":"notepad"}],"response":"Notepad khul raha hai!","confidence":1.0}

Input: "screenshot lo aur desktop par save karo"
{"thinking":"take screenshot and save to desktop","reasoning":"screenshot action auto-saves","intent":"screenshot","api_route":"desktop_api","port":8003,"steps":[{"step":1,"action":"screenshot"}],"response":"Screenshot le liya! Desktop par save ho gaya. 📸","confidence":1.0}

Input: "google par lahore ka weather check karo"
{"thinking":"search lahore weather on google","reasoning":"search_google with city name","intent":"search_weather","api_route":"browser_api","port":8002,"steps":[{"step":1,"action":"search_google","query":"Lahore weather today"}],"response":"Google par Lahore ka weather search kar raha hoon! ☁️","confidence":0.97}

Input: "Desktop par Projects naam ka folder banao"
{"thinking":"create folder named Projects on desktop","reasoning":"create_folder in file_api","intent":"create_folder","api_route":"file_api","port":8004,"steps":[{"step":1,"action":"create_folder","name":"Projects","location":"desktop"}],"response":"Desktop par 'Projects' folder ban gaya! 📁","confidence":1.0}

Input: "awaz thodi barha do"
{"thinking":"increase system volume","reasoning":"volume_up on desktop_api","intent":"volume_up","api_route":"desktop_api","port":8003,"steps":[{"step":1,"action":"volume_up"}],"response":"Awaz barha di! 🔊","confidence":1.0}

Input: "reddit kholo"
{"thinking":"open reddit website","reasoning":"open_url to reddit.com","intent":"open_reddit","api_route":"browser_api","port":8002,"steps":[{"step":1,"action":"open_url","target":"https://reddit.com"}],"response":"Reddit khul raha hai! 🤖","confidence":1.0}
"""

# ---------------------------------------------------------------------------
# Conversation History (last 10 messages for context memory)
# ---------------------------------------------------------------------------
_conversation_history: list[dict] = []


def intelligent_plan(command: str) -> dict:
    """
    Fully AI-driven planning using OpenAI GPT-4o-mini.
    Maintains conversation history for context (e.g. 'dobara karo').
    Falls back to rule-based only if OpenAI is unavailable.
    """
    global _conversation_history

    # No API key → go straight to fallback
    if not client:
        logger.warning("OpenAI client not initialized — OPENAI_API_KEY missing. Using fallback.")
        return _smart_fallback(command)

    # Add user message to history
    _conversation_history.append({
        "role": "user",
        "content": f"Command: {command}"
    })
    # Keep last 10 turns (20 messages)
    if len(_conversation_history) > 20:
        _conversation_history = _conversation_history[-20:]

    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + _conversation_history

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.1,
            max_tokens=600,
            response_format={"type": "json_object"},
        )

        result_text = response.choices[0].message.content.strip()
        if not result_text:
            raise ValueError("Empty response from OpenAI")

        result = json.loads(result_text)
        result["input"] = command

        # Normalize api_route & port
        result = _normalize_route(result)

        # Add assistant reply to history for context
        _conversation_history.append({
            "role": "assistant",
            "content": result_text,
        })

        logger.info(f"OpenAI plan → intent={result.get('intent')} route={result.get('api_route')} confidence={result.get('confidence')}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"OpenAI JSON parse error: {e}")
        return _smart_fallback(command)
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return _smart_fallback(command)


def _normalize_route(result: dict) -> dict:
    """Ensure api_route and port are always valid."""
    result.setdefault("input", "")
    result.setdefault("estimated_time", "1.0s")
    result.setdefault("steps", [])

    route = str(result.get("api_route", "")).lower().strip()

    if any(k in route for k in ["browser", "web", "url", "youtube", "google", "internet", "search", "gmail", "whatsapp", "reddit", "amazon", "facebook"]):
        result["api_route"] = "browser_api"
        result["port"] = 8002
    elif any(k in route for k in ["desktop", "app", "screen", "volume", "system", "power", "notepad", "calculator", "lock", "shutdown", "restart"]):
        result["api_route"] = "desktop_api"
        result["port"] = 8003
    elif any(k in route for k in ["file", "folder", "directory", "document"]):
        result["api_route"] = "file_api"
        result["port"] = 8004
    else:
        # Default to browser_api for unknown routes
        result["api_route"] = "browser_api"
        result["port"] = 8002

    return result


def _smart_fallback(command: str) -> dict:
    """
    Lightweight keyword-based fallback when OpenAI is unavailable.
    Covers the most common commands only.
    """
    cmd = command.lower().strip()

    # YouTube / Music
    if any(w in cmd for w in ["youtube", "gaana", "gaane", "song", "music", "chalao", "play", "bajao"]):
        query = (cmd
                 .replace("youtube", "").replace("par", "").replace("pe", "")
                 .replace("chalao", "").replace("play", "").replace("bajao", "")
                 .replace("ke gaane", "").replace("songs", "").replace("song", "")
                 .strip()) or "trending music"
        return _build("play_music", "browser_api", 8002,
                      [{"step": 1, "action": "search_youtube", "query": query}],
                      f"YouTube par '{query}' search kar raha hoon!", command)

    # Google search
    if any(w in cmd for w in ["google", "search", "dhundo", "find", "check"]):
        query = (cmd.replace("google", "").replace("search", "").replace("par", "")
                 .replace("pe", "").replace("karo", "").replace("dhundo", "").strip()) or command
        return _build("search_google", "browser_api", 8002,
                      [{"step": 1, "action": "search_google", "query": query}],
                      f"Google par '{query}' search kar raha hoon!", command)

    # Screenshot
    if any(w in cmd for w in ["screenshot", "screen pakdo", "screen capture"]):
        return _build("screenshot", "desktop_api", 8003,
                      [{"step": 1, "action": "screenshot"}],
                      "Screenshot le liya! Desktop par save ho gaya.", command)

    # Volume
    if any(w in cmd for w in ["volume", "awaz", "sound"]):
        is_down = any(w in cmd for w in ["down", "kam", "ghatao", "low", "dheemi"])
        action = "volume_down" if is_down else "volume_up"
        return _build(action, "desktop_api", 8003,
                      [{"step": 1, "action": action}],
                      "Awaz kam kar di!" if is_down else "Awaz barha di!", command)

    # Notepad
    if any(w in cmd for w in ["notepad", "note pad"]):
        return _build("open_notepad", "desktop_api", 8003,
                      [{"step": 1, "action": "open_app", "target": "notepad"}],
                      "Notepad khul raha hai!", command)

    # Calculator
    if any(w in cmd for w in ["calculator", "calc", "hisab"]):
        return _build("open_calculator", "desktop_api", 8003,
                      [{"step": 1, "action": "open_app", "target": "calculator"}],
                      "Calculator khul raha hai!", command)

    # Common websites
    sites = {
        "reddit": ("https://reddit.com", "Reddit"),
        "gmail": ("https://gmail.com", "Gmail"),
        "amazon": ("https://amazon.com", "Amazon"),
        "facebook": ("https://facebook.com", "Facebook"),
        "instagram": ("https://instagram.com", "Instagram"),
        "twitter": ("https://twitter.com", "Twitter"),
        "whatsapp": ("https://web.whatsapp.com", "WhatsApp"),
    }
    for key, (url, label) in sites.items():
        if key in cmd:
            return _build(f"open_{key}", "browser_api", 8002,
                          [{"step": 1, "action": "open_url", "target": url}],
                          f"{label} khul raha hai!", command)

    # Default: google search
    return _build("search_google", "browser_api", 8002,
                  [{"step": 1, "action": "search_google", "query": command}],
                  f"Google par search kar raha hoon: {command}", command, confidence=0.5)


def _build(intent, api_route, port, steps, response, command, confidence=0.85):
    return {
        "input": command,
        "thinking": f"User wants: {intent.replace('_', ' ')}",
        "reasoning": "keyword fallback match",
        "intent": intent,
        "api_route": api_route,
        "port": port,
        "steps": steps,
        "response": response,
        "confidence": confidence,
        "estimated_time": "0.5s",
    }
