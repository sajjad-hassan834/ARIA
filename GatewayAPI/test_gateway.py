import asyncio
import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Ensure GatewayAPI is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app
from config import HISTORY_FILE
from services.orchestrator import orchestrator_service

client = TestClient(app)


def test_root_endpoint():
    """Verify Gateway root metadata endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ARIA Master Gateway API"
    assert data["port"] == 8080
    assert data["status"] == "online"
    assert "endpoints" in data


def test_health_endpoint():
    """Verify /health endpoint returns health state."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["gateway"] == "online"
    assert data["port"] == 8080
    assert "apis" in data
    assert "speech_api" in data["apis"]
    assert "brain_api" in data["apis"]


def test_gateway_status_endpoint():
    """Verify /api/gateway/status returns structured status for all subsystems."""
    response = client.get("/api/gateway/status")
    assert response.status_code == 200
    data = response.json()
    assert data["gateway"] == "online"
    assert "apis" in data
    assert "ollama" in data
    for api_key in ["speech_api", "brain_api", "browser_api", "desktop_api", "file_api"]:
        assert api_key in data["apis"]
        assert "status" in data["apis"][api_key]
        assert "port" in data["apis"][api_key]


def test_empty_text_command_validation():
    """Verify empty text command returns 400 Bad Request."""
    response = client.post("/api/gateway/command/text", json={"command": "   "})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_process_text_command_browser_mock():
    """Verify end-to-end orchestration for browser command using mocks."""
    mock_brain_plan = {
        "input": "YouTube par Arijit Singh ke gaane chalao",
        "intent": "play_music",
        "steps": [
            {"action": "open_browser", "target": "youtube.com"},
            {"action": "search", "query": "Arijit Singh"},
            {"action": "click_first_result"},
            {"action": "play"}
        ],
        "api_route": "browser_api",
        "port": 8002,
        "confidence": 0.95,
        "estimated_time": "3.5s"
    }

    mock_browser_exec = {
        "status": "success",
        "steps_executed": 4,
        "steps_failed": 0,
        "time": "3.1s",
        "results": [{"action": "open_browser"}, {"action": "play"}]
    }

    async def mock_post(self, url, *args, **kwargs):
        url_str = str(url)
        req = httpx.Request("POST", url_str)
        if "8001" in url_str or "brain" in url_str:
            return httpx.Response(200, json=mock_brain_plan, request=req)
        elif "8002" in url_str or "browser" in url_str:
            return httpx.Response(200, json=mock_browser_exec, request=req)
        return httpx.Response(404, request=req)

    with patch.object(httpx.AsyncClient, "post", new=mock_post):
        response = client.post(
            "/api/gateway/command/text",
            json={"command": "YouTube par Arijit Singh ke gaane chalao"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["command"] == "YouTube par Arijit Singh ke gaane chalao"
        assert data["intent"] == "play_music"
        assert data["executed_by"] == "browser_api"
        assert data["status"] == "success"
        assert data["steps_completed"] == 4
        assert "Arijit Singh" in data["response"]
        assert "s" in data["time"]


def test_process_text_command_retry_and_offline():
    """Verify retry logic when Brain API is offline."""
    async def mock_fail_post(self, url, *args, **kwargs):
        raise httpx.ConnectError("Connection refused")

    with patch.object(httpx.AsyncClient, "post", new=mock_fail_post):
        response = client.post(
            "/api/gateway/command/text",
            json={"command": "test offline command"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["offline", "error"]
        assert data["steps_completed"] == 0
        assert "Failed to plan command" in data["response"]


def test_process_audio_command_mock():
    """Verify audio command flow: Speech API transcription -> Brain API -> Subsystem."""
    mock_transcribe = {
        "text": "YouTube par Arijit Singh ke gaane chalao",
        "confidence": 0.96,
        "language": "hi",
        "processing_time": 0.5
    }

    mock_brain_plan = {
        "input": "YouTube par Arijit Singh ke gaane chalao",
        "intent": "play_music",
        "steps": [{"action": "open_browser"}],
        "api_route": "browser_api",
        "port": 8002,
        "confidence": 0.95,
        "estimated_time": "1s"
    }

    mock_browser_exec = {
        "status": "success",
        "steps_executed": 1,
        "steps_failed": 0,
        "time": "0.8s"
    }

    async def mock_audio_post(self, url, *args, **kwargs):
        url_str = str(url)
        req = httpx.Request("POST", url_str)
        if "8000" in url_str or "speech" in url_str:
            return httpx.Response(200, json=mock_transcribe, request=req)
        elif "8001" in url_str or "brain" in url_str:
            return httpx.Response(200, json=mock_brain_plan, request=req)
        elif "8002" in url_str or "browser" in url_str:
            return httpx.Response(200, json=mock_browser_exec, request=req)
        return httpx.Response(404, request=req)

    with patch.object(httpx.AsyncClient, "post", new=mock_audio_post):

        fake_audio = b"RIFF....WAVEfmt ...."
        response = client.post(
            "/api/gateway/command/audio",
            files={"file": ("test.wav", fake_audio, "audio/wav")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["command"] == "YouTube par Arijit Singh ke gaane chalao"
        assert data["status"] == "success"
        assert data["intent"] == "play_music"
        assert "transcription" in data


def test_empty_audio_command_validation():
    """Verify empty audio file returns 400 Bad Request."""
    response = client.post(
        "/api/gateway/command/audio",
        files={"file": ("empty.wav", b"", "audio/wav")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


def test_command_history_retrieval():
    """Verify history endpoint returns recorded commands."""
    response = client.get("/api/gateway/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "history" in data
    assert isinstance(data["history"], list)
    assert data["total"] == len(data["history"])


if __name__ == "__main__":
    pytest.main(["-v", __file__])
