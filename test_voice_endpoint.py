"""
ARIA Voice Command Terminal Test Script
Tests the full voice pipeline with auto-microphone detection and live volume meter:
Microphone -> Gateway (8080) -> SpeechAPI Whisper (8000) -> BrainAPI OpenAI (8001) -> Desktop/Browser Subsystem (8002/8003) -> TTS Voice Response
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

def find_best_microphone_index():
    """Find the active microphone device index with the strongest signal."""
    if not sd:
        return None

    devices = sd.query_devices()
    preferred_keywords = ["microphone array 2", "realtek hd audio mic", "microphone array", "input"]

    # 1. First priority: Look for Realtek SST / Microphone Array 2 (known active device 18)
    for idx, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0:
            name_lower = d.get("name", "").lower()
            if "microphone array 2" in name_lower or "sst" in name_lower:
                return idx

    # 2. Second priority: Probe devices for non-zero signal
    candidates = []
    for idx, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0:
            try:
                rec = sd.rec(int(0.08 * 16000), samplerate=16000, channels=1, dtype='int16', device=idx)
                sd.wait()
                amp = int(np.max(np.abs(rec)))
                candidates.append((amp, idx, d.get("name")))
            except Exception:
                continue

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        # Return device with highest amplitude
        return candidates[0][1]

    return None

def record_live_audio(output_path: str, duration_sec: int = 4, device_index: int = None):
    """Record live audio using sounddevice with a live audio level meter."""
    if not sd:
        print("[-] sounddevice not available. Please install: pip install sounddevice")
        return False

    dev_idx = device_index if device_index is not None else find_best_microphone_index()
    dev_name = sd.query_devices(dev_idx)["name"] if dev_idx is not None else "Default"
    print(f"\n[+] Using Microphone: [{dev_idx}] {dev_name}")

    sample_rate = 16000
    total_frames = int(duration_sec * sample_rate)
    chunk_size = int(sample_rate * 0.1)  # 100ms chunks for meter
    num_chunks = int(duration_sec / 0.1)

    all_audio = []
    print(f"\n[>>>] LISTENING NOW! Speak your command clearly into your mic... [{duration_sec}s]\n")

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16', device=dev_idx) as stream:
            for _ in range(num_chunks):
                data, overflowed = stream.read(chunk_size)
                all_audio.append(data)
                amp = np.max(np.abs(data))
                level = min(20, int(amp / 1500))
                bar = "█" * level + "░" * (20 - level)
                sys.stdout.write(f"\r  Mic Level: [{bar}] {amp:5d} / 32767")
                sys.stdout.flush()

        print("\n\n[✓] Recording complete. Processing audio...")
        full_waveform = np.concatenate(all_audio, axis=0)

        max_volume = int(np.max(np.abs(full_waveform)))
        if max_volume < 100:
            print(f"[!] Warning: Audio signal was very quiet (Peak: {max_volume}). Please check mic volume in Windows.")
        else:
            print(f"[✓] Voice audio captured cleanly (Peak Amplitude: {max_volume})")

        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(full_waveform.tobytes())

        return True
    except Exception as e:
        print(f"[-] Recording error: {e}")
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
    print(f"\n[*] Sending audio to ARIA Gateway: {GATEWAY_AUDIO_URL}...")
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
