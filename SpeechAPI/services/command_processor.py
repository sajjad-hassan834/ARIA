import json
import os
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List
from pathlib import Path

import config
from services.nlu_service import nlu_service
from models.schemas import CommandResponse

class CommandProcessor:
    def __init__(self, history_file: Path = config.HISTORY_FILE, max_history: int = config.MAX_HISTORY):
        self.history_file = history_file
        self.max_history = max_history
        self._lock = threading.Lock()
        self._ensure_history_file()

    def _ensure_history_file(self) -> None:
        """Create history file and parent directories if not present."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists() or self.history_file.stat().st_size == 0:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def _read_history(self) -> List[Dict[str, Any]]:
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception:
            return []

    def _write_history(self, history: List[Dict[str, Any]]) -> None:
        # Atomic write pattern using temp file
        temp_file = self.history_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, self.history_file)

    def log_command(self, record: Dict[str, Any]) -> None:
        """Add record to history and truncate to max_history."""
        with self._lock:
            history = self._read_history()
            history.insert(0, record)  # Most recent first
            if len(history) > self.max_history:
                history = history[:self.max_history]
            self._write_history(history)

    def get_history(self, limit: int = config.MAX_HISTORY) -> List[Dict[str, Any]]:
        """Retrieve recent command history."""
        with self._lock:
            history = self._read_history()
            return history[:limit]

    def process_command(self, text: str) -> CommandResponse:
        """
        Process transcribed or raw text input:
        1. Match intent via NLU
        2. Resolve action and friendly response
        3. Formulate CommandResponse
        4. Log to command_history.json
        """
        match_result = nlu_service.match_intent(text)
        intent = match_result["intent"]
        confidence = match_result["confidence"]

        action, default_response = nlu_service.get_intent_action_and_response(intent)
        response_text = match_result.get("response") or default_response
        success = (intent != "unknown")


        timestamp = datetime.now(timezone.utc).isoformat()

        cmd_response = CommandResponse(
            raw_text=text,
            intent=intent,
            action=action,
            response=response_text,
            success=success,
            timestamp=timestamp
        )

        # Log to file
        log_payload = cmd_response.model_dump()
        log_payload["confidence"] = confidence
        log_payload["language"] = match_result.get("language", "en")
        self.log_command(log_payload)

        return cmd_response


command_processor = CommandProcessor()
