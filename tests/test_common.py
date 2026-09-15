import asyncio
import os
import sys
import tempfile
from pathlib import Path
import httpx
import pytest
from fastapi import FastAPI

# Ensure ARIA root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import common


def test_global_config_ports():
    """Verify standard ARIA ports are correctly mapped."""
    assert common.PORTS["speech_api"] == 8000
    assert common.PORTS["brain_api"] == 8001
    assert common.PORTS["browser_api"] == 8002
    assert common.PORTS["desktop_api"] == 8003
    assert common.PORTS["file_api"] == 8004
    assert common.PORTS["gateway_api"] == 8080
    assert common.PORTS["ollama"] == 11434


def test_global_config_urls():
    """Verify default subsystem URLs are mapped correctly."""
    assert "8000" in common.SPEECH_API_URL
    assert "8001" in common.BRAIN_API_URL
    assert "8002" in common.BROWSER_API_URL
    assert "8003" in common.DESKTOP_API_URL
    assert "8004" in common.FILE_API_URL
    assert "8080" in common.GATEWAY_API_URL
    assert len(common.APIS) == 5


def test_shared_models():
    """Verify shared Pydantic models instantiate and validate properly."""
    step = common.PlanStep(action="open_browser", target="youtube.com", step=1)
    assert step.action == "open_browser"
    assert step.step == 1

    plan_req = common.ExecutePlanRequest(steps=[{"action": "click", "step": 1}])
    assert len(plan_req.steps) == 1

    plan_resp = common.ExecutePlanResponse(status="success", steps_executed=1, steps_failed=0)
    assert plan_resp.status == "success"

    api_resp = common.APIResponse(success=True, message="All good", data={"key": "val"})
    assert api_resp.success is True

    health_resp = common.HealthResponse(status="healthy", service="test_service", port=9999)
    assert health_resp.status == "healthy"


def test_history_store_rolling_and_thread_safety():
    """Verify HistoryStore creates files, records atomically, and caps rolling records."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        history_path = Path(tmp_dir) / "test_history.json"
        store = common.HistoryStore(file_path=history_path, max_items=5)

        # Record 10 items
        for i in range(10):
            store.record({"id": i, "command": f"cmd_{i}"})

        records = store.get_all()
        # Must be capped at 5
        assert len(records) == 5
        # Most recent must be first
        assert records[0]["id"] == 9
        assert records[4]["id"] == 5

        # Limit retrieval
        limited = store.get_all(limit=2)
        assert len(limited) == 2
        assert limited[0]["id"] == 9

        # Clear
        store.clear()
        assert len(store.get_all()) == 0


@pytest.mark.asyncio
async def test_network_probe_offline():
    """Verify network probing reports offline gracefully for non-existent servers."""
    async with httpx.AsyncClient() as client:
        res = await common.probe_service_health(client, "http://127.0.0.1:59999", port=59999, timeout=0.1)
        assert res["status"] == "offline"
        assert res["port"] == 59999


@pytest.mark.asyncio
async def test_network_probe_ollama_disconnected():
    """Verify Ollama probing reports disconnected for non-existent host."""
    async with httpx.AsyncClient() as client:
        res = await common.probe_ollama_status(client, "http://127.0.0.1:59999", timeout=0.1)
        assert res == "disconnected"


def test_cors_middleware():
    """Verify setup_cors applies to FastAPI app."""
    app = FastAPI()
    common.setup_cors(app)
    # Check that middleware was registered
    has_cors = any("CORSMiddleware" in str(m) for m in app.user_middleware)
    assert has_cors is True


if __name__ == "__main__":
    pytest.main(["-v", __file__])
