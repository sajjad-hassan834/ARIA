"""
ARIA Voice Command Terminal Test Script
Tests the full voice pipeline:
Microphone / Audio WAV -> Gateway (8080) -> SpeechAPI Whisper (8000) -> BrainAPI OpenAI (8001) -> Desktop/Browser Subsystem (8002/8003) -> TTS Voice Spoken Response
"""
import sys
import os
import time
import argparse
from pathlib import Path
import httpx

GATEWAY_AUDIO_URL = "http://127.0.0.1:8080/api/gateway/command/audio"
GATEWAY_TEXT_URL = "http://127.0.0.1:8080/api/gateway/command/text"

def generate_speech_wav(text: str, output_path: str):
    """Generate a clean WAV speech file using pyttsx3."""
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.save_to_file(text, output_path)
    engine.runAndWait()

def record_from_microphone(output_path: str, duration_sec: int = 4):
    """Record live audio from the microphone using PyAudio or SpeechRecognition."""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("\n[+] Adjusting for ambient room noise... (1 sec)")
            r.adjust_for_ambient_noise(source, duration=1.0)
            print(f"[>>>] LISTENING NOW! Speak your command clearly (e.g. 'Open Notepad')... [{duration_sec}s]")
            audio = r.record(source, duration=duration_sec)
            with open(output_path, "wb") as f:
                f.write(audio.get_wav_data())
            print("[✓] Audio recording finished.")
            return True
    except Exception as e:
        print(f"[-] Microphone recording failed: {e}")
        return False

def test_voice(audio_file_path: str):
    """Upload audio file to Gateway and display response."""
    print(f"\n[*] Uploading '{audio_file_path}' to ARIA Gateway: {GATEWAY_AUDIO_URL}...")
    t0 = time.perf_counter()

    with open(audio_file_path, "rb") as f:
        audio_bytes = f.read()

    files = {
        "file": (os.path.basename(audio_file_path), audio_bytes, "audio/wav")
    }

    try:
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(GATEWAY_AUDIO_URL, files=files)
        
        elapsed = time.perf_counter() - t0
        print(f"[*] Response received in {elapsed:.2f}s (HTTP {resp.status_code}):\n")

        if resp.status_code == 200:
            data = resp.json()
            print("=" * 60)
            print("  ARIA VOICE PIPELINE EXECUTION SUCCESSFUL")
            print("=" * 60)
            print(f"  Recognized Command : \"{data.get('command')}\"")
            print(f"  AI Intent          : {data.get('intent')}")
            print(f"  Executed By API    : {data.get('executed_by')} (Port {data.get('plan', {}).get('port', '—')})")
            print(f"  Execution Status   : {data.get('status').upper()}")
            print(f"  Steps Completed    : {data.get('steps_completed')}")
            print(f"  ARIA Voice Reply   : \"{data.get('response')}\"")
            print("=" * 60)
            return True
        else:
            print(f"[-] Gateway returned error (HTTP {resp.status_code}): {resp.text}")
            return False

    except Exception as e:
        print(f"[-] Request failed: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test ARIA Voice Command Endpoint")
    parser.add_argument("--mic", action="store_true", help="Record audio live from your laptop microphone")
    parser.add_argument("--command", type=str, default="open notepad", help="Text to synthesize for test audio")
    parser.add_argument("--duration", type=int, default=4, help="Recording duration in seconds")
    args = parser.parse_args()

    temp_wav = os.path.abspath("test_utterance.wav")

    print("=" * 60)
    print("      ARIA VOICE COMMAND TERMINAL TEST")
    print("=" * 60)

    if args.mic:
        print(f"Mode: LIVE MICROPHONE RECORDING ({args.duration} seconds)")
        success = record_from_microphone(temp_wav, duration_sec=args.duration)
        if not success:
            print("[-] Falling back to synthetic audio test...")
            generate_speech_wav(args.command, temp_wav)
    else:
        print(f"Mode: SYNTHETIC VOICE UTTERANCE: \"{args.command}\"")
        generate_speech_wav(args.command, temp_wav)

    test_voice(temp_wav)

    # Clean up temp file
    if os.path.exists(temp_wav):
        try:
            os.remove(temp_wav)
        except Exception:
            pass
