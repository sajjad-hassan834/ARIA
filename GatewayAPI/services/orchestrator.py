"""
ARIA Gateway Orchestrator — Routes commands through Brain → Subsystem APIs.
Speaks voice response after every command via the TTS service.
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx

import common
import config
from services.tts_service import speak

logger = logging.getLogger("gateway.orchestrator")

# ── API URL registry ─────────────────────────────────────────────────────────
APIS = {
    "speech_api": config.SPEECH_API,
    "brain_api":  config.BRAIN_API,
    "browser_api": config.BROWSER_API,
    "desktop_api": config.DESKTOP_API,
    "file_api":   config.FILE_API,
}

# Subsystem execute-plan endpoint paths
_EXEC_PATHS = {
    "browser_api": "/api/browser/execute-plan",
    "desktop_api": "/api/desktop/execute-plan",
    "file_api":    "/api/files/execute-plan",
}


# ── History helper ────────────────────────────────────────────────────────────
class OrchestratorService:
    def __init__(self):
        self.history_store = common.HistoryStore(
            file_path=config.HISTORY_FILE,
            max_items=config.MAX_HISTORY_ITEMS,
        )

    def record_history(self, entry: Dict[str, Any]):
        return self.history_store.record(entry)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.history_store.get_all(limit=limit)

    # ── Shared retry POST ────────────────────────────────────────────────────
    async def _post(
        self,
        client: httpx.AsyncClient,
        url: str,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: float = config.DEFAULT_TIMEOUT,
    ) -> Tuple[bool, Optional[httpx.Response], str]:
        return await common.post_with_retry(
            client=client,
            url=url,
            json_data=json_data,
            files=files,
            timeout=timeout,
            max_retries=config.MAX_RETRIES,
        )

    # ── Text Command ─────────────────────────────────────────────────────────
    async def process_text_command(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """
        Full flow:
          1. Brain API → get AI plan (OpenAI GPT-4o-mini)
          2. Route plan to correct subsystem API
          3. Speak voice response
          4. Return result + record in history
        """
        t0 = time.perf_counter()
        clean = text.strip()

        async with httpx.AsyncClient(timeout=config.DEFAULT_TIMEOUT) as http:

            # ── Step 1: Brain API ────────────────────────────────────────────
            brain_url = f"{APIS['brain_api'].rstrip('/')}/api/brain/plan"
            ok, brain_resp, brain_err = await self._post(
                http, brain_url, json_data={"text": clean, "language": language}
            )

            if not ok or not brain_resp or brain_resp.status_code >= 400:
                elapsed = f"{time.perf_counter() - t0:.1f}s"
                msg = brain_err or (
                    f"Brain API HTTP {brain_resp.status_code}" if brain_resp else "Brain API offline"
                )
                speak("Brain API is offline. Please check backend services.")
                result = self._error_result(clean, "brain_api", msg, elapsed, is_offline="Connection" in (brain_err or ""))
                self.record_history(result)
                return result

            try:
                plan = brain_resp.json()
            except Exception as e:
                elapsed = f"{time.perf_counter() - t0:.1f}s"
                speak("Could not interpret execution plan. Please try again.")
                result = self._error_result(clean, "brain_api", str(e), elapsed)
                self.record_history(result)
                return result

            # ── Step 2: Route to subsystem ───────────────────────────────────
            api_route = (plan.get("api_route") or "browser_api").strip()
            steps     = plan.get("steps", [])
            intent    = plan.get("intent", "unknown")
            plan_resp = plan.get("response", "")

            # If api_route is unknown or no steps → still speak the plan response
            exec_path = _EXEC_PATHS.get(api_route)
            if not exec_path or not steps:
                elapsed = f"{time.perf_counter() - t0:.1f}s"
                speak(plan_resp or "Understood the command, but no executable steps were generated.")
                result = {
                    "command": clean,
                    "intent": intent,
                    "executed_by": api_route,
                    "status": "success" if not steps else "error",
                    "steps_completed": 0,
                    "response": plan_resp or f"No executable steps for intent: {intent}",
                    "time": elapsed,
                    "plan": plan,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.record_history(result)
                return result

            target_base = APIS.get(api_route, "")
            exec_url    = f"{target_base.rstrip('/')}{exec_path}"

            exec_ok, sub_resp, sub_err = await self._post(
                http, exec_url, json_data={"steps": steps}
            )

            elapsed = f"{time.perf_counter() - t0:.1f}s"

            if not exec_ok or not sub_resp or sub_resp.status_code >= 400:
                err_msg = sub_err or (
                    f"{api_route} HTTP {sub_resp.status_code}" if sub_resp else f"{api_route} offline"
                )
                speak(f"Subsystem unavailable: {api_route.replace('_', ' ')}. Please check backend.")
                result = self._error_result(
                    clean, api_route, err_msg, elapsed,
                    intent=intent,
                    is_offline="Connection" in (sub_err or ""),
                    plan=plan,
                )
                self.record_history(result)
                return result

            try:
                exec_data = sub_resp.json()
            except Exception:
                exec_data = {"raw": sub_resp.text}

            # Step count
            steps_done = len(steps)
            if isinstance(exec_data, dict):
                if "steps_executed" in exec_data:
                    steps_done = exec_data["steps_executed"]
                elif "data" in exec_data and isinstance(exec_data.get("data"), dict):
                    steps_done = len(exec_data["data"].get("results", steps))

            # Final human response — prefer plan's AI-generated reply
            human_resp = plan_resp or exec_data.get("message") or exec_data.get("response") or "Task completed!"

            result = {
                "command": clean,
                "intent": intent,
                "executed_by": api_route,
                "status": "success",
                "steps_completed": steps_done,
                "response": human_resp,
                "time": elapsed,
                "plan": plan,
                "details": exec_data,
                "timestamp": datetime.utcnow().isoformat(),
            }
            self.record_history(result)

            # Speak the AI-generated response 🔊
            speak(human_resp)

            return result

    # ── Audio Command ─────────────────────────────────────────────────────────
    async def process_audio_command(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        content_type: str = "audio/wav",
    ) -> Dict[str, Any]:
        """Transcribe via Speech API then hand off to process_text_command."""
        t0 = time.perf_counter()

        async with httpx.AsyncClient(timeout=config.DEFAULT_TIMEOUT) as http:
            speech_url = f"{APIS['speech_api'].rstrip('/')}/api/speech/transcribe"
            files = {"file": (filename, audio_bytes, content_type)}

            ok, speech_resp, speech_err = await self._post(http, speech_url, files=files)

            if not ok or not speech_resp or speech_resp.status_code >= 400:
                elapsed = f"{time.perf_counter() - t0:.1f}s"
                msg = speech_err or (f"Speech API HTTP {speech_resp.status_code}" if speech_resp else "Speech API offline")
                speak("Awaaz samajh nahi aya. Speech API offline hai.")
                result = self._error_result("[Voice]", "speech_api", msg, elapsed, is_offline="Connection" in (speech_err or ""))
                self.record_history(result)
                return result

            try:
                speech_data = speech_resp.json()
                transcribed  = speech_data.get("text", "").strip()
            except Exception as e:
                elapsed = f"{time.perf_counter() - t0:.1f}s"
                msg = "Could not process audio. Please try again."
                speak(msg)
                result = self._error_result("[Voice]", "speech_api", str(e), elapsed)
                self.record_history(result)
                return result

            # Detect and discard Whisper silence hallucinations
            clean_low = transcribed.lower().strip(" .!?,")
            is_hallucination = (
                not clean_low
                or len(clean_low) < 2
                or all(w == "you" for w in clean_low.split())
                or clean_low in ("you", "thank you", "thanks for watching", "subtitles by", "bye", "amara")
            )
            if is_hallucination:
                elapsed = f"{time.perf_counter() - t0:.1f}s"
                msg = "No clear voice detected. Please speak into your microphone."
                speak(msg)
                result = {
                    "command": "[Silence / Background Noise]",
                    "intent": "no_speech",
                    "executed_by": "speech_api",
                    "status": "error",
                    "steps_completed": 0,
                    "response": msg,
                    "time": elapsed,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.record_history(result)
                return result

            res = await self.process_text_command(transcribed)
            res["transcription"] = speech_data
            return res

    # ── Health Check ──────────────────────────────────────────────────────────
    async def check_all_apis(self) -> Dict[str, Any]:
        """Probe all subsystem APIs and Ollama, return status map."""
        async with httpx.AsyncClient() as http:
            tasks = [
                common.probe_service_health(
                    client=http,
                    base_url=info["url"],
                    port=info["port"],
                    timeout=config.HEALTH_TIMEOUT,
                )
                for info in config.APIS.values()
            ]
            ollama_task = common.probe_ollama_status(
                client=http,
                host=config.OLLAMA_HOST,
                timeout=0.3,
            )
            results      = await asyncio.gather(*tasks)
            ollama_status = await ollama_task

        apis_status = {name: res for name, res in zip(config.APIS.keys(), results)}
        return {"gateway": "online", "apis": apis_status, "ollama": ollama_status}

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _error_result(
        command: str,
        executed_by: str,
        error: str,
        elapsed: str,
        intent: str = "error",
        is_offline: bool = False,
        plan: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        return {
            "command": command,
            "intent": intent,
            "executed_by": executed_by,
            "status": "offline" if is_offline else "error",
            "steps_completed": 0,
            "response": f"Error: {error}",
            "time": elapsed,
            "plan": plan,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }


# ── Singleton ─────────────────────────────────────────────────────────────────
orchestrator_service = OrchestratorService()
