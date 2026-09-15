from typing import Any, Dict, Optional
import common
from config import HISTORY_FILE

_history_store = common.HistoryStore(file_path=HISTORY_FILE, max_items=50)


def log_operation(operation: str, parameters: Dict[str, Any], status: str = "success", error: Optional[str] = None, data: Optional[Any] = None) -> None:
    """Record an operation to data/file_history.json using global HistoryStore."""
    entry = {
        "operation": operation,
        "parameters": parameters,
        "status": status,
        "error": error,
        "data": data,
    }
    _history_store.record(entry)
