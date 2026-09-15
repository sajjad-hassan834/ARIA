from typing import Any, Dict, Optional
import common
from config import ACTION_HISTORY_FILE

_history_store = common.HistoryStore(file_path=ACTION_HISTORY_FILE, max_items=50)


def record_action(action: str, params: Optional[Dict[str, Any]], success: bool, result: Optional[Any] = None) -> Dict[str, Any]:
    """Record a desktop action to action_history.json using global HistoryStore."""
    entry = {
        "action": action,
        "params": params or {},
        "success": success,
        "result": result,
    }
    return _history_store.record(entry)
