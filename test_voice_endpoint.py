"""
ARIA Voice Command Terminal Test Script
Records live audio directly from the active Realtek Microphone (Device 18) via sounddevice,
sends to ARIA Gateway API (8080), transcribes via Whisper, plans via OpenAI, and executes.
"""
import sys
import os
import time
import argparse
import wave
from pathlib import Path
import httpx
import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None

GATEWAY_AUDIO_URL = "http://127.0.0.1:8080/api/gateway/command/audio"

def get_real_microphone_device():
    """Identify the active hardware microphone device index."""
    if not sd:
        return None

    # Priority 1: Device 18 (Microphone Array 2 - Realtek HD Audio Mic input with SST)
    devices = sd.query_devices()
    for idx, d in enumerate(devices):
        name = d.get("name", "")
        if "Microphone Array 2" in name and d.get("max_input_channels", 0) > 0:
            return idx

    # Priority 2: Any Microphone Array with positive input channels
    for idx, d in enumerate(devices):
        name = d.get("name", "")
        if "Microphone Array" in name and d.get("max_input_channels", 0) > 0:
            return idx

    return None

def record_live_audio(output_path: str, duration_sec: int = 4, device_index: int = None):
    """Record live audio using sounddevice.rec."""
    if not sd:
        print("[-] sounddevice not available. Please run: pip install sounddevice")
        return False

    dev_idx = device_index if device_index is not None else get_real_microphone_device()
    dev_name = sd.query_devices(dev_idx)["name"] if dev_idx is not None else "Default"
    print(f"\n[+] Active Hardware Microphone Selected: [{dev_idx}] {dev_name}")

    sample_rate = 16000
    total_frames = int(duration_sec * sample_rate)

    print(f"\n[>>>] PREPARE TO SPEAK... Starting in 1 second...")
    time.sleep(1.0)
    print(f"\n{'='*60}")
    print(f"  [>>>] LISTENING NOW! Speak your command into your microphone!  ")
    print(f"{'='*60}\n")

    try:
        # Asynchronous non-blocking recording buffer
        audio_buffer = sd.rec(total_frames, samplerate=sample_rate, channels=1, dtype='int16', device=dev_idx)

        # Interactive countdown
        for rem in range(duration_sec, 0, -1):
            sys.stdout.write(f"\r  >>> Recording in progress... [ {rem} seconds remaining ] <<<  ")
            sys.stdout.flush()
            time.sleep(1.0)

        sd.wait()
        sys.stdout.write("\r  [✓] Recording complete! Processing your voice command...          \n\n")
        sys.stdout.flush()

        peak = int(np.max(np.abs(audio_buffer)))
        print(f"[+] Audio Capture Signal Level: Peak Amplitude = {peak} / 32767")

        if peak < 80:
            print("[!] Warning: Recorded audio is very quiet. Make sure you speak directly into your laptop mic.")

        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_buffer.tobytes())

        return True

    except Exception as e:
        print(f"\n[-] Recording error: {e}")
        return False

def generate_speech_wav(text: str, output_path: str):
    """Generate a clean WAV speech file using pyttsx3."""
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.save_to_file(text, output_path)
    engine.runAndWait()

def test_voice(audio_file_path: str):
    """Upload audio file to Gateway and display response."""
    print(f"[*] Uploading audio to ARIA Gateway: {GATEWAY_AUDIO_URL}...")
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
            plan = data.get('plan') or {}
            print("=" * 60)
            print("  ARIA VOICE PIPELINE EXECUTION SUCCESSFUL")
            print("=" * 60)
            print(f"  Recognized Command : \"{data.get('command')}\"")
            print(f"  AI Intent          : {data.get('intent')}")
            print(f"  Executed By API    : {data.get('executed_by')} (Port {plan.get('port', '8080')})")
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
    parser.add_argument("--device", type=int, default=None, help="Specific microphone device index (optional)")
    parser.add_argument("--command", type=str, default="open notepad", help="Text to synthesize for test audio")
    parser.add_argument("--duration", type=int, default=4, help="Recording duration in seconds (default: 4)")
    args = parser.parse_args()

    temp_wav = os.path.abspath("test_utterance.wav")

    print("=" * 60)
    print("      ARIA VOICE COMMAND TERMINAL TEST")
    print("=" * 60)

    if args.mic:
        success = record_live_audio(temp_wav, duration_sec=args.duration, device_index=args.device)
        if not success:
            print("[-] Recording failed. Falling back to synthetic audio test...")
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
