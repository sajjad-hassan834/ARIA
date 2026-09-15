import io
import json
import wave
import struct
import math
import sys
from pathlib import Path
from fastapi.testclient import TestClient

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


from main import app
from services.nlu_service import nlu_service
from services.command_processor import command_processor
from services.tts_service import tts_service
from services.whisper_service import whisper_service

def generate_test_wav(duration_sec: float = 1.0, freq: float = 440.0, sample_rate: int = 16000) -> bytes:
    """Generate a clean synthetic sine wave PCM audio file in WAV format."""
    num_samples = int(sample_rate * duration_sec)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            value = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * freq * i / sample_rate))
            frames.extend(struct.pack("<h", value))
        wav_file.writeframes(frames)
    buffer.seek(0)
    return buffer.read()

def test_nlu_service():
    print("\n--- Testing NLU Service ---")
    test_cases = [
        ("awaz barha", "volume_up", "roman_urdu"),
        ("kholo", "open_browser", "roman_urdu"),
        ("band karo", "close_window", "roman_urdu"),
        ("screenshot lo", "screenshot", "roman_urdu"),
        ("open browser", "open_browser", "en"),
        ("volume up", "volume_up", "en"),
        ("what time is it", "time_check", "en"),
        ("salam", "greeting", "roman_urdu"),
        # User requested Ollama / NLU test phrases:
        ("mujhe kuch likhna hai", "type_text", "roman_urdu"),
        ("google par weather dekhna hai", "search_web", "roman_urdu"),
        ("sab kuch copy karo", "copy", "roman_urdu"),
        ("band karo yeh sab", "close_window", "roman_urdu"),
        ("meri screen dikhao", "screenshot", "roman_urdu"),
        ("awaaz bilkul band karo", "mute", "roman_urdu"),
    ]

    for phrase, expected_intent, expected_lang in test_cases:
        result = nlu_service.match_intent(phrase)
        print(f"Input: '{phrase}' -> Intent: {result['intent']} (expected: {expected_intent}), Conf: {result['confidence']}, Lang: {result['language']}")
        assert result["intent"] == expected_intent, f"Failed for '{phrase}': got {result['intent']}, expected {expected_intent}"
        assert result["confidence"] >= 0.75, f"Low confidence for '{phrase}': {result['confidence']}"
    print("✓ All NLU tests passed successfully!")

def test_command_processor():
    print("\n--- Testing Command Processor ---")
    resp = command_processor.process_command("awaz barha")
    print(f"Command response: {resp.model_dump()}")
    assert resp.intent == "volume_up"
    assert resp.action == "volume_up"
    assert resp.success is True
    assert resp.response == "Increasing volume"

    # Check history
    history = command_processor.get_history(limit=10)
    assert len(history) > 0
    assert history[0]["intent"] == "volume_up"
    print("✓ Command processor and history logging passed successfully!")

def test_tts_service():
    print("\n--- Testing TTS Service ---")
    stream = tts_service.text_to_speech_mp3("Hello, testing text to speech.")
    audio_bytes = stream.read()
    print(f"Synthesized audio length: {len(audio_bytes)} bytes")
    assert len(audio_bytes) > 0
    print("✓ TTS service passed successfully!")

def test_api_endpoints():
    print("\n--- Testing API Endpoints with TestClient ---")
    with TestClient(app) as client:
        # 1. Root & Health
        res_root = client.get("/")
        assert res_root.status_code == 200
        assert res_root.json()["status"] == "online"
        print("✓ GET / passed")

        res_health = client.get("/health")
        assert res_health.status_code == 200
        health_json = res_health.json()
        print(f"✓ GET /health passed: {health_json}")
        assert health_json["status"] == "ok"
        assert health_json["whisper"] == "loaded"
        assert health_json["model"] == "phi3:mini"
        assert health_json["ollama"] in ["connected", "disconnected"]


        # 2. POST /api/speech/intent
        res_intent = client.post("/api/speech/intent", json={"text": "awaz barha"})
        assert res_intent.status_code == 200
        data = res_intent.json()
        print(f"✓ POST /api/speech/intent passed: {data}")
        assert data["intent"] == "volume_up"
        assert data["language"] == "roman_urdu"

        # 3. GET /api/speech/history
        res_hist = client.get("/api/speech/history")
        assert res_hist.status_code == 200
        hist_data = res_hist.json()
        print(f"✓ GET /api/speech/history passed: total {hist_data['total']} items")
        assert "history" in hist_data

        # 4. POST /api/tts/speak
        res_tts = client.post("/api/tts/speak", json={"text": "Opening browser now", "language": "en"})
        assert res_tts.status_code == 200
        assert res_tts.headers["content-type"] == "audio/mpeg"
        assert len(res_tts.content) > 100
        print(f"✓ POST /api/tts/speak passed: received {len(res_tts.content)} bytes audio/mpeg")

        # 5. POST /api/speech/transcribe & POST /api/speech/command with test audio
        test_wav = generate_test_wav(duration_sec=1.5)
        files = {"file": ("test.wav", test_wav, "audio/wav")}

        res_transcribe = client.post("/api/speech/transcribe", files=files)
        assert res_transcribe.status_code == 200
        trans_data = res_transcribe.json()
        print(f"✓ POST /api/speech/transcribe passed: {trans_data}")
        assert "text" in trans_data
        assert "confidence" in trans_data
        assert "processing_time" in trans_data

        files_cmd = {"file": ("test_cmd.wav", test_wav, "audio/wav")}
        res_cmd = client.post("/api/speech/command", files=files_cmd)
        assert res_cmd.status_code == 200
        cmd_data = res_cmd.json()
        print(f"✓ POST /api/speech/command passed: {cmd_data}")
        assert "raw_text" in cmd_data
        assert "intent" in cmd_data
        assert "action" in cmd_data
        assert "response" in cmd_data

        # 7. Exception Handling Tests
        print("\n--- Testing Structured Exception Handling ---")
        # Unsupported audio extension
        bad_file = {"file": ("malware.exe", b"invalid data", "application/octet-stream")}
        res_bad_file = client.post("/api/speech/transcribe", files=bad_file)
        assert res_bad_file.status_code == 400
        bad_json = res_bad_file.json()
        print(f"✓ Unsupported audio error response: {bad_json}")
        assert bad_json["success"] is False
        assert bad_json["error_code"] == "UNSUPPORTED_AUDIO_FORMAT"

        # Validation error test
        res_val = client.post("/api/speech/intent", json={})
        assert res_val.status_code == 422
        val_json = res_val.json()
        print(f"✓ Validation error response: {val_json}")
        assert val_json["error_code"] == "VALIDATION_ERROR"

        # 404 Resource Not Found
        res_404 = client.get("/api/non-existent-endpoint")
        assert res_404.status_code == 404
        json_404 = res_404.json()
        print(f"✓ 404 error response: {json_404}")
        assert json_404["error_code"] == "RESOURCE_NOT_FOUND"

        # 6. WebSocket /ws/voice-stream
        print("\n--- Testing WebSocket /ws/voice-stream ---")

        with client.websocket_connect("/ws/voice-stream") as ws:
            # 1. Connected event
            connected_msg = ws.receive_json()
            assert connected_msg["event"] == "connected"
            print(f"WebSocket connected: {connected_msg}")

            # 2. Send ping
            ws.send_json({"action": "ping"})
            pong_msg = ws.receive_json()
            assert pong_msg["event"] == "pong"
            print(f"WebSocket ping-pong: {pong_msg}")

            # 3. Send binary audio chunks
            ws.send_bytes(test_wav[:4000])
            chunk_event = ws.receive_json()
            assert chunk_event["event"] == "transcribing"
            print(f"WebSocket chunk event: {chunk_event}")

            # 4. Commit buffer
            ws.send_json({"action": "commit"})
            events_received = []
            # Buffer processing emits: transcribing -> recognized -> executing -> done
            for _ in range(4):
                evt = ws.receive_json()
                events_received.append(evt.get("event"))
                print(f"WebSocket event received: {evt.get('event')} -> {evt}")

            assert "transcribing" in events_received
            assert "recognized" in events_received
            assert "executing" in events_received
            assert "done" in events_received
            print("✓ WebSocket voice-stream events verified successfully!")

if __name__ == "__main__":
    test_nlu_service()
    test_command_processor()
    test_tts_service()
    test_api_endpoints()
    print("\n🎉 ALL TESTS COMPLETED AND PASSED SUCCESSFULLY! 🎉\n")
