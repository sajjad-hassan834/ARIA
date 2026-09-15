import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
try:
    import config
except ImportError:
    from BrainAPI import config


class ContextService:
    def __init__(self, storage_file=config.CONTEXT_HISTORY_FILE):
        self.storage_file = storage_file
        self.max_context_length = 10
        self.repeat_phrases = [
            "wahi karo phir",
            "wahi karo fir",
            "wahi dobara karo",
            "wahi fir karo",
            "wahi phir karo",
            "phir se karo",
            "fir se karo",
            "dobara karo",
            "ek baar aur",
            "repeat karo",
            "again",
            "do it again",
            "repeat that",
            "repeat",
            "one more time",
        ]
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.storage_file.exists():
            self._save_data({"recent_commands": [], "task_history": []})

    def _load_data(self) -> Dict[str, Any]:
        try:
            if self.storage_file.exists():
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"recent_commands": [], "task_history": []}

    def _save_data(self, data: Dict[str, Any]) -> None:
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ContextService] Error saving context: {e}")

    def is_repeat_command(self, text: str) -> bool:
        """Check if user command requests repeating previous action."""
        cleaned = re.sub(r"[^\w\s]", "", text.strip().lower())
        for phrase in self.repeat_phrases:
            if phrase in cleaned or cleaned == phrase:
                return True
        return False

    def add_command(
        self,
        text: str,
        intent: Optional[str] = None,
        plan: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record command in context history (maintaining max 10)."""
        data = self._load_data()
        recent = data.get("recent_commands", [])

        entry = {
            "input": text,
            "intent": intent,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "plan": plan,
            "metadata": metadata or {},
        }

        # Keep last 10 commands
        recent.append(entry)
        if len(recent) > self.max_context_length:
            recent = recent[-self.max_context_length :]

        data["recent_commands"] = recent
        self._save_data(data)
        return entry

    def get_recent_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        data = self._load_data()
        recent = data.get("recent_commands", [])
        return recent[-limit:]

    def get_last_plan(self) -> Optional[Dict[str, Any]]:
        """Return the most recent plan executed or planned."""
        data = self._load_data()
        recent = data.get("recent_commands", [])
        for item in reversed(recent):
            if item.get("plan"):
                return item["plan"]

        tasks = data.get("task_history", [])
        if tasks:
            return tasks[-1].get("plan")
        return None


context_service = ContextService()
