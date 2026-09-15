import json
import re
from typing import Any, Dict, List, Optional, Tuple
import httpx
try:
    import config
except ImportError:
    from BrainAPI import config
from .context_service import context_service


TASK_ROUTES: Dict[str, Dict[str, Any]] = {
    "open_browser": {"api": "browser_api", "port": 8002},
    "play_music": {"api": "browser_api", "port": 8002},
    "search_web": {"api": "browser_api", "port": 8002},
    "open_youtube": {"api": "browser_api", "port": 8002},
    "create_folder": {"api": "desktop_api", "port": 8003},
    "open_notepad": {"api": "desktop_api", "port": 8003},
    "screenshot": {"api": "desktop_api", "port": 8003},
    "volume_up": {"api": "desktop_api", "port": 8003},
    "download_file": {"api": "file_api", "port": 8004},
    "move_file": {"api": "file_api", "port": 8004},
    "delete_file": {"api": "file_api", "port": 8004},
}

INTENT_STEPS: Dict[str, List[Dict[str, Any]]] = {
    "play_music": [
        {"action": "open_browser", "target": "youtube.com"},
        {"action": "search", "query": "{query}"},
        {"action": "click_first_result"},
        {"action": "play"},
    ],
    "search_web": [
        {"action": "open_browser"},
        {"action": "goto_url", "target": "google.com"},
        {"action": "search", "query": "{query}"},
    ],
    "open_youtube": [
        {"action": "open_browser"},
        {"action": "goto_url", "target": "youtube.com"},
    ],
    "screenshot": [
        {"action": "take_screenshot"},
        {"action": "save_to_desktop"},
    ],
    "create_folder": [
        {"action": "create_folder", "location": "desktop", "name": "{name}"},
    ],
    "open_notepad": [
        {"action": "open_application", "target": "notepad.exe"},
    ],
    "volume_up": [
        {"action": "change_volume", "direction": "up", "level": "+10%"},
    ],
    "open_browser": [
        {"action": "open_browser", "target": "about:blank"},
    ],
    "download_file": [
        {"action": "download_file", "source": "{query}"},
    ],
    "move_file": [
        {"action": "move_file", "source": "{query}"},
    ],
    "delete_file": [
        {"action": "delete_file", "target": "{query}"},
    ],
}


class PlannerService:
    def __init__(self):
        self.routes = TASK_ROUTES
        self.intent_templates = INTENT_STEPS

    def detect_intent(self, text: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Rule-based intent classifier supporting English & Hinglish.
        Returns (intent, confidence, parameters)
        """
        lower = text.strip().lower()

        # Music / Songs / YouTube Play
        if any(k in lower for k in ["gaana", "gaane", "song", "songs", "sangeet"]) or (
            "play" in lower and not "game" in lower
        ) or ("chalao" in lower and "youtube" in lower):
            query = self._extract_music_query(text)
            return "play_music", 0.95, {"query": query}

        # YouTube Open
        if "youtube" in lower and any(k in lower for k in ["kholo", "open", "go to", "chalao"]):
            return "open_youtube", 0.92, {"target": "youtube.com"}

        # Web Search / Google
        if any(k in lower for k in ["search", "google", "dhoondo", "khojo"]):
            query = self._extract_search_query(text)
            return "search_web", 0.90, {"query": query}

        # Create Folder
        if "folder" in lower and any(k in lower for k in ["banao", "create", "make", "new"]):
            folder_name = self._extract_folder_name(text)
            return "create_folder", 0.93, {"name": folder_name, "location": "desktop"}

        # Screenshot
        if any(k in lower for k in ["screenshot", "screen shot", "capture screen"]):
            return "screenshot", 0.95, {}

        # Notepad
        if "notepad" in lower:
            return "open_notepad", 0.92, {"app": "notepad.exe"}

        # Volume
        if any(k in lower for k in ["volume", "awaz", "sound"]) and any(k in lower for k in ["up", "badhao", "increase"]):
            return "volume_up", 0.90, {"direction": "up"}

        # Browser
        if "browser" in lower and any(k in lower for k in ["open", "kholo", "start"]):
            return "open_browser", 0.88, {}

        # File actions
        if "download" in lower:
            return "download_file", 0.85, {"query": text}
        if "move" in lower or "shift" in lower:
            return "move_file", 0.85, {"query": text}
        if "delete" in lower or "hatao" in lower:
            return "delete_file", 0.85, {"query": text}

        # Default fallback
        return "search_web", 0.60, {"query": text}

    def _extract_music_query(self, text: str) -> str:
        """Extract song/artist name from English/Hinglish sentence."""
        cleaned = text
        # Remove common filler phrases
        remove_patterns = [
            r"(?i)\byoutube\s+par\b",
            r"(?i)\byoutube\s+pe\b",
            r"(?i)\bon\s+youtube\b",
            r"(?i)\bchalao\b",
            r"(?i)\bchala\s+do\b",
            r"(?i)\bbajao\b",
            r"(?i)\bbaja\s+do\b",
            r"(?i)\bsunao\b",
            r"(?i)\bplay\b",
            r"(?i)\bplease\b",
            r"(?i)\bke\s+gaane\b",
            r"(?i)\bke\s+songs\b",
            r"(?i)\bgaane\b",
            r"(?i)\bgaana\b",
            r"(?i)\bsongs\b",
            r"(?i)\bsong\b",
        ]
        extracted = cleaned
        for pat in remove_patterns:
            extracted = re.sub(pat, "", extracted).strip()

        extracted = re.sub(r"\s+", " ", extracted).strip()
        if not extracted:
            return "trending songs"
        return f"{extracted} songs"

    def _extract_search_query(self, text: str) -> str:
        remove_patterns = [
            r"(?i)\bgoogle\s+par\b",
            r"(?i)\bgoogle\s+pe\b",
            r"(?i)\bon\s+google\b",
            r"(?i)\bsearch\s+karo\b",
            r"(?i)\bsearch\s+for\b",
            r"(?i)\bsearch\b",
            r"(?i)\bdhoondo\b",
            r"(?i)\bkhojo\b",
        ]
        query = text
        for pat in remove_patterns:
            query = re.sub(pat, "", query).strip()
        query = re.sub(r"\s+", " ", query).strip()
        return query or text

    def _extract_folder_name(self, text: str) -> str:
        # Match "X naam se folder banao" or "folder named X"
        match = re.search(r"(?i)(?:named|naam\s+se)\s+([a-zA-Z0-9_\-\s]+)", text)
        if match:
            return match.group(1).strip()
        return "New Folder"

    def generate_steps(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Instantiate step template with parameters and 1-based index."""
        raw_steps = self.intent_templates.get(intent, [{"action": "execute", "target": intent}])
        generated = []

        for idx, s in enumerate(raw_steps, start=1):
            step_dict = {"step": idx, "action": s["action"]}
            for k, v in s.items():
                if k == "action":
                    continue
                if isinstance(v, str):
                    # Replace placeholders like {query}, {name}
                    for p_key, p_val in parameters.items():
                        v = v.replace(f"{{{p_key}}}", str(p_val))
                step_dict[k] = v
            generated.append(step_dict)

        return generated

    def plan_rule_based(self, text: str) -> Dict[str, Any]:
        """Generate execution plan using rule-based engine."""
        intent, confidence, parameters = self.detect_intent(text)
        route_info = self.routes.get(intent, {"api": "desktop_api", "port": 8003})
        steps = self.generate_steps(intent, parameters)

        estimated_times = {
            "browser_api": "3s",
            "desktop_api": "2s",
            "file_api": "1s",
        }

        api_route = route_info["api"]
        port = route_info["port"]

        return {
            "input": text,
            "intent": intent,
            "steps": steps,
            "api_route": api_route,
            "port": port,
            "confidence": confidence,
            "estimated_time": estimated_times.get(api_route, "2s"),
        }

    async def plan_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Synthesize execution plan using OpenAI GPT-4o-mini.
        """
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("openai_api_key")
        if not api_key:
            return None

        system_prompt = """You are ARIA Brain Planner.
Convert user commands (in English, Hindi, or Hinglish) into a JSON execution plan.
Valid api_routes:
- "browser_api" (port 8002) for web browsing, playing youtube videos/songs, searches.
- "desktop_api" (port 8003) for launching apps, desktop screenshots, system volume.
- "file_api" (port 8004) for creating files/folders, deleting files, moving files.

Return ONLY a valid JSON object matching this schema:
{
  "intent": "<intent_name>",
  "api_route": "browser_api" | "desktop_api" | "file_api",
  "port": 8002 | 8003 | 8004,
  "confidence": 0.95,
  "estimated_time": "2s",
  "steps": [
    {"step": 1, "action": "<action_name>", "target": "<target_or_none>", "query": "<query_or_none>", "location": "<location_or_none>", "name": "<name_or_none>"}
  ]
}"""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"User Command: {text}"},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1,
                }
                res = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    return json.loads(content)
        except Exception as e:
            logger.warning(f"OpenAI planning failed in planner_service: {e}")
        return None


    async def plan(self, text: str) -> Dict[str, Any]:
        """
        Master planning method:
        1. Check if user asked to repeat last command ("wahi karo phir").
        2. Attempt LLM planning if enabled (config.USE_LLM=True).
        3. Fall back immediately to rule-based planning (< 1ms).
        """
        if context_service.is_repeat_command(text):
            last_plan = context_service.get_last_plan()
            if last_plan:
                repeat_plan = dict(last_plan)
                repeat_plan["input"] = text
                repeat_plan["confidence"] = 1.0
                return repeat_plan

        if config.USE_LLM:
            llm_result = await self.plan_with_llm(text)
            if llm_result:
                return llm_result

        return self.plan_rule_based(text)

    def classify(self, text: str) -> Dict[str, Any]:
        """Classify utterance into API, port, action, and parameters."""
        intent, _, parameters = self.detect_intent(text)
        route_info = self.routes.get(intent, {"api": "desktop_api", "port": 8003})
        return {
            "input": text,
            "api": route_info["api"],
            "port": route_info["port"],
            "action": intent,
            "parameters": parameters,
        }


planner_service = PlannerService()
