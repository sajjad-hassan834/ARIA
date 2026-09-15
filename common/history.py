import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("common.history")


class HistoryStore:
    """
    Thread-safe, atomic JSON history logger with rolling capacity.
    Reusable across all ARIA microservices.
    """

    def __init__(self, file_path: Union[str, Path], max_items: int = 50):
        self.file_path = Path(file_path).resolve()
        self.max_items = max_items
        self._lock = threading.Lock()
        self._init_file()

    def _init_file(self):
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
        except Exception as exc:
            logger.error(f"Failed to initialize history store at {self.file_path}: {exc}")

    def record(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Record an entry at the head of history, ensuring timestamp and capping."""
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.utcnow().isoformat()

        with self._lock:
            try:
                history = self._load()
                history.insert(0, entry)
                history = history[:self.max_items]

                temp_file = self.file_path.with_suffix(".tmp")
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                temp_file.replace(self.file_path)
            except Exception as exc:
                logger.error(f"Error recording history in {self.file_path}: {exc}")

        return entry

    def _load(self) -> List[Dict[str, Any]]:
        if not self.file_path.exists():
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    if isinstance(data, list):
                        return data
        except Exception as exc:
            logger.warning(f"Failed reading history {self.file_path}: {exc}")
        return []

    def get_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve recent entries up to limit."""
        with self._lock:
            history = self._load()
        if limit is not None and limit > 0:
            return history[:limit]
        return history

    def clear(self):
        """Clear all stored history."""
        with self._lock:
            try:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
            except Exception as exc:
                logger.error(f"Error clearing history {self.file_path}: {exc}")
