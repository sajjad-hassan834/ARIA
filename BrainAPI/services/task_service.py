import json
import uuid
from datetime import datetime
from typing import Any, Dict, List
import config


class TaskService:
    def __init__(self, storage_file=config.CONTEXT_HISTORY_FILE):
        self.storage_file = storage_file
        self.max_history_length = 20
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
            print(f"[TaskService] Error saving task history: {e}")

    def record_task(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Record planned task in persistent history (keeps last 20)."""
        data = self._load_data()
        history = data.get("task_history", [])

        task_entry = {
            "task_id": f"task_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input": plan.get("input"),
            "intent": plan.get("intent"),
            "api_route": plan.get("api_route"),
            "port": plan.get("port"),
            "steps": plan.get("steps"),
            "confidence": plan.get("confidence"),
            "estimated_time": plan.get("estimated_time"),
            "status": "planned",
        }

        history.append(task_entry)
        if len(history) > self.max_history_length:
            history = history[-self.max_history_length :]

        data["task_history"] = history
        self._save_data(data)
        return task_entry

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return the last planned tasks (default up to 20)."""
        data = self._load_data()
        history = data.get("task_history", [])
        return history[-limit:]


task_service = TaskService()
