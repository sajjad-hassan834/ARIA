import json
import pytest
from fastapi.testclient import TestClient
from main import app
from config import ACTION_HISTORY_FILE

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["port"] == 8003
    assert data["service"] == "desktop_api"


def test_power_safety():
    # Shutdown without confirm must fail
    res = client.post("/api/desktop/system/power", json={"action": "shutdown", "confirm": False})
    assert res.status_code == 400

    # Restart without confirm must fail
    res = client.post("/api/desktop/system/power", json={"action": "restart"})
    assert res.status_code == 400


def test_app_unsupported():
    res = client.post("/api/desktop/app/open", json={"app": "nonexistent_fake_app_xyz"})
    assert res.status_code == 400
    data = res.json()
    assert "Unsupported application" in data["detail"]["message"]


def test_volume():
    res = client.post("/api/desktop/system/volume", json={"action": "up", "level": 1})
    assert res.status_code == 200
    assert res.json()["success"] is True

    res = client.post("/api/desktop/system/volume", json={"action": "invalid_vol"})
    assert res.status_code == 400


def test_screen_type():
    res = client.post("/api/desktop/screen/type", json={"text": "", "speed": "fast"})
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_screen_scroll():
    res = client.post("/api/desktop/screen/scroll", json={"direction": "up", "amount": 1})
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_screen_click_bounds():
    # Invalid coordinates
    res = client.post("/api/desktop/screen/click", json={"x": -10, "y": -10, "button": "left"})
    assert res.status_code == 400


def test_execute_plan():
    plan = {
        "steps": [
            {"action": "wait", "params": {"seconds": 0.1}},
            {"action": "volume", "params": {"action": "mute"}},
            {"action": "scroll", "params": {"direction": "down", "amount": 1}},
        ]
    }
    res = client.post("/api/desktop/execute-plan", json=plan)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]["results"]) == 3


def test_action_history_recorded():
    assert ACTION_HISTORY_FILE.exists()
    with open(ACTION_HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
    assert isinstance(history, list)
    assert len(history) > 0
    # verify entry format
    last_entry = history[-1]
    assert "timestamp" in last_entry
    assert "action" in last_entry
    assert "params" in last_entry
    assert "success" in last_entry


if __name__ == "__main__":
    print("Running tests manually...")
    test_health()
    print("Health check passed.")
    test_power_safety()
    print("Power safety passed.")
    test_app_unsupported()
    print("App unsupported validation passed.")
    test_volume()
    print("Volume passed.")
    test_screen_type()
    print("Screen type passed.")
    test_screen_scroll()
    print("Screen scroll passed.")
    test_screen_click_bounds()
    print("Screen click bounds passed.")
    test_execute_plan()
    print("Execute plan passed.")
    test_action_history_recorded()
    print("Action history recorded passed.")
    print("ALL TESTS PASSED SUCCESSFULLY!")
