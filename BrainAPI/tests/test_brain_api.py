import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["brain"] == "ready"
    assert "speech_api" in data
    assert "browser_api" in data
    assert "desktop_api" in data
    assert "file_api" in data
    assert "ollama" in data
    print("[OK] Health check passed:", data)


def test_plan_music():
    payload = {"text": "YouTube par Arijit Singh ke gaane chalao", "language": "auto"}
    response = client.post("/api/brain/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "play_music"
    assert data["api_route"] == "browser_api"
    assert data["port"] == 8002
    assert len(data["steps"]) >= 4
    assert data["steps"][0]["step"] == 1
    assert data["steps"][0]["action"] == "open_browser"
    print("[OK] Plan music passed:", data)


def test_classify_folder():
    payload = {"text": "Desktop par folder banao"}
    response = client.post("/api/brain/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "desktop_api"
    assert data["port"] == 8003
    assert data["action"] == "create_folder"
    print("[OK] Classify folder passed:", data)


def test_repeat_context():
    # 1. Plan something initial
    client.post("/api/brain/plan", json={"text": "YouTube par Arijit Singh ke gaane chalao"})

    # 2. Ask to repeat
    repeat_res = client.post("/api/brain/plan", json={"text": "wahi karo phir"})
    assert repeat_res.status_code == 200
    repeat_data = repeat_res.json()
    assert repeat_data["intent"] == "play_music"
    assert repeat_data["api_route"] == "browser_api"
    print("[OK] Repeat context passed:", repeat_data["intent"])


def test_history():
    response = client.get("/api/brain/history")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert data["total"] >= 1
    print(f"[OK] History check passed ({data['total']} tasks recorded)")


if __name__ == "__main__":
    test_health()
    test_plan_music()
    test_classify_folder()
    test_repeat_context()
    test_history()
    print("\nAll integration tests PASSED!")
