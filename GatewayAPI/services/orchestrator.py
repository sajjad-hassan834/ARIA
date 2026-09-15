import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pyttsx3

import common
import config

logger = logging.getLogger("gateway.orchestrator")


def speak_async(text: str):
    """Speaks back to the user asynchronously using pyttsx3 TTS."""
    if not text or not text.strip():
        return

    def _speak():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 160)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.warning(f"Voice synthesis error: {e}")

    threading.Thread(target=_speak, daemon=True).start()


APIS = {
    "speech_api": config.SPEECH_API,
    "brain_api": config.BRAIN_API,
    "browser_api": config.BROWSER_API,
    "desktop_api": config.DESKTOP_API,
    "file_api": config.FILE_API,
}

PORTS = {
    "speech_api": 8000,
    "brain_api": 8001,
    "browser_api": 8002,
    "desktop_api": 8003,
    "file_api": 8004,
}


def _format_human_response(intent: str, plan: Dict[str, Any], exec_data: Dict[str, Any], default_text: str) -> str:
    """Generate friendly natural language response for the user."""
    # Check if plan contains an intelligent direct response message
    if plan and plan.get("response"):
        return str(plan["response"])

    # Check if subsystem provided a clean message
    if isinstance(exec_data, dict):
        if exec_data.get("message"):
            return str(exec_data["message"])
        if exec_data.get("response"):
            return str(exec_data["response"])

    steps = plan.get("steps", [])
    query = None
    target = None
    name = None
    for step in steps:
        if not query and step.get("query"):
            query = step.get("query")
        if not target and step.get("target"):
            target = step.get("target")
        if not name and step.get("name"):
            name = step.get("name")
        params = step.get("params") or {}
        if not query and params.get("query"):
            query = params.get("query")
        if not target and (params.get("app") or params.get("target")):
            target = params.get("app") or params.get("target")
        if not name and params.get("name"):
            name = params.get("name")

    # Intent-based templates
    if intent == "play_music":
        subject = query or target or "requested music"
        return f"Playing {subject} on YouTube!"
    elif intent == "open_youtube":
        return "Opened YouTube in browser!"
    elif intent == "search_web":
        return f"Searched for '{query or default_text}' on Google!"
    elif intent == "screenshot":
        return "Screenshot captured and saved to Desktop!"
    elif intent == "create_folder":
        return f"Created folder '{name or 'New Folder'}' successfully!"
    elif intent == "open_notepad":
        return "Notepad opened successfully!"
    elif intent == "volume_up":
        return "System volume increased by 10%!"
    elif intent == "open_browser":
        return "Opened web browser!"
    elif intent == "download_file":
        return f"Download initiated for {query or 'file'}."
    elif intent == "move_file":
        return f"Moved file {query or ''} successfully."
    elif intent == "delete_file":
        return f"File {query or target or ''} deleted successfully."
    
    return f"Command executed successfully: {default_text}"


class OrchestratorService:
    def __init__(self):
        self.history_store = common.HistoryStore(
            file_path=config.HISTORY_FILE,
            max_items=config.MAX_HISTORY_ITEMS
        )

    def record_history(self, entry: Dict[str, Any]):
        """Persist command execution record using global HistoryStore."""
        return self.history_store.record(entry)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent command history from global HistoryStore."""
        return self.history_store.get_all(limit=limit)

    async def _post_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: float = config.DEFAULT_TIMEOUT,
    ) -> Tuple[bool, Optional[httpx.Response], str]:
        """Execute an HTTP POST with retry using global common.post_with_retry."""
        return await common.post_with_retry(
            client=client,
            url=url,
            json_data=json_data,
            files=files,
            timeout=timeout,
            max_retries=config.MAX_RETRIES,
        )


    async def process_text_command(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """
        Full orchestration flow:
        1. Query Brain API for intent & plan (port 8001)
        2. Route plan to subsystem API (Browser 8002 / Desktop 8003 / File 8004)
        3. Format response, measure time, record in history
        """
        start_time = time.perf_counter()
        clean_text = text.strip()

        async with httpx.AsyncClient(timeout=config.DEFAULT_TIMEOUT) as client:
            # Step 1: Brain API - Get plan
            brain_url = f"{APIS['brain_api'].rstrip('/')}/api/brain/plan"
            ok, brain_response, brain_err = await self._post_with_retry(
                client,
                brain_url,
                json_data={"text": clean_text, "language": language},
            )

            if not ok or not brain_response or brain_response.status_code >= 400:
                elapsed = f"{time.perf_counter() - start_time:.1f}s"
                err_msg = brain_err or (f"Brain API error {brain_response.status_code}" if brain_response else "Brain API is offline")
                result = {
                    "command": clean_text,
                    "intent": "unknown",
                    "executed_by": "brain_api",
                    "status": "offline" if "Connection error" in brain_err else "error",
                    "steps_completed": 0,
                    "response": f"Failed to plan command: {err_msg}",
                    "time": elapsed,
                    "plan": None,
                    "error": err_msg,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.record_history(result)
                return result

            try:
                plan = brain_response.json()
            except Exception as e:
                elapsed = f"{time.perf_counter() - start_time:.1f}s"
                result = {
                    "command": clean_text,
                    "intent": "unknown",
                    "executed_by": "brain_api",
                    "status": "error",
                    "steps_completed": 0,
                    "response": f"Brain API returned invalid JSON: {str(e)}",
                    "time": elapsed,
                    "plan": None,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.record_history(result)
                return result

            # Step 2: Route to correct subsystem API
            api_route = plan.get("api_route") or "browser_api"
            steps = plan.get("steps", [])
            target_api_url = APIS.get(api_route)

            if not target_api_url:
                elapsed = f"{time.perf_counter() - start_time:.1f}s"
                result = {
                    "command": clean_text,
                    "intent": plan.get("intent", "unknown"),
                    "executed_by": api_route,
                    "status": "error",
                    "steps_completed": 0,
                    "response": f"Unknown target subsystem: '{api_route}'",
                    "time": elapsed,
                    "plan": plan,
                    "error": f"No endpoint configured for {api_route}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.record_history(result)
                return result

            # Determine endpoint path for executing plan
            if api_route == "browser_api":
                exec_url = f"{target_api_url.rstrip('/')}/api/browser/execute-plan"
            elif api_route == "desktop_api":
                exec_url = f"{target_api_url.rstrip('/')}/api/desktop/execute-plan"
            elif api_route == "file_api":
                exec_url = f"{target_api_url.rstrip('/')}/api/files/execute-plan"
            else:
                exec_url = f"{target_api_url.rstrip('/')}/execute-plan"

            # Execute plan with retry
            exec_ok, sub_response, sub_err = await self._post_with_retry(
                client,
                exec_url,
                json_data={"steps": steps},
            )

            elapsed = f"{time.perf_counter() - start_time:.1f}s"

            if not exec_ok or not sub_response or sub_response.status_code >= 400:
                err_msg = sub_err or (f"{api_route} error {sub_response.status_code}" if sub_response else f"{api_route} is offline")
                result = {
                    "command": clean_text,
                    "intent": plan.get("intent"),
                    "executed_by": api_route,
                    "status": "offline" if "Connection error" in (sub_err or "") else "error",
                    "steps_completed": 0,
                    "response": f"Subsystem {api_route} execution failed: {err_msg}",
                    "time": elapsed,
                    "plan": plan,
                    "error": err_msg,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.record_history(result)
                return result

            try:
                exec_data = sub_response.json()
            except Exception:
                exec_data = {"raw": sub_response.text}

            # Parse completion count
            steps_completed = len(steps)
            if isinstance(exec_data, dict):
                if "steps_executed" in exec_data:
                    steps_completed = exec_data.get("steps_executed", len(steps))
                elif "data" in exec_data and isinstance(exec_data["data"], dict) and "results" in exec_data["data"]:
                    steps_completed = len(exec_data["data"]["results"])

            human_resp = _format_human_response(plan.get("intent", ""), plan, exec_data, clean_text)

            result = {
                "command": clean_text,
                "intent": plan.get("intent"),
                "executed_by": api_route,
                "status": "success",
                "steps_completed": steps_completed,
                "response": human_resp,
                "time": elapsed,
                "plan": plan,
                "details": exec_data,
                "timestamp": datetime.utcnow().isoformat(),
            }
            self.record_history(result)

            # Call after successful execution:
            speak_async(result.get("response", "Task completed"))

            return result

    async def process_audio_command(self, audio_bytes: bytes, filename: str = "audio.wav", content_type: str = "audio/wav") -> Dict[str, Any]:
        """
        Process voice command:
        1. Transcribe audio with Speech API (8000)
        2. Feed transcribed text into process_text_command
        """
        start_time = time.perf_counter()

        async with httpx.AsyncClient(timeout=config.DEFAULT_TIMEOUT) as client:
            speech_url = f"{APIS['speech_api'].rstrip('/')}/api/speech/transcribe"
            files = {"file": (filename, audio_bytes, content_type)}

            ok, speech_response, speech_err = await self._post_with_retry(
                client,
                speech_url,
                files=files,
            )

            if not ok or not speech_response or speech_response.status_code >= 400:
                elapsed = f"{time.perf_counter() - start_time:.1f}s"
                err_msg = speech_err or (f"Speech API error {speech_response.status_code}" if speech_response else "Speech API is offline")
                result = {
                    "command": "[Voice Command]",
                    "intent": "unknown",
                    "executed_by": "speech_api",
                    "status": "offline" if "Connection error" in speech_err else "error",
                    "steps_completed": 0,
                    "response": f"Speech transcription failed: {err_msg}",
                    "time": elapsed,
                    "error": err_msg,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.record_history(result)
                return result

            try:
                speech_data = speech_response.json()
                transcribed_text = speech_data.get("text", "").strip()
            except Exception as e:
                elapsed = f"{time.perf_counter() - start_time:.1f}s"
                result = {
                    "command": "[Voice Command]",
                    "intent": "unknown",
                    "executed_by": "speech_api",
                    "status": "error",
                    "steps_completed": 0,
                    "response": f"Failed to parse speech transcription: {str(e)}",
                    "time": elapsed,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.record_history(result)
                return result

            if not transcribed_text:
                elapsed = f"{time.perf_counter() - start_time:.1f}s"
                result = {
                    "command": "",
                    "intent": "unknown",
                    "executed_by": "speech_api",
                    "status": "error",
                    "steps_completed": 0,
                    "response": "No audible speech could be recognized.",
                    "time": elapsed,
                    "transcription": speech_data,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.record_history(result)
                return result

            # Hand off transcribed text to main planning and execution flow
            res = await self.process_text_command(transcribed_text)
            res["transcription"] = speech_data
            return res

    async def check_all_apis(self) -> Dict[str, Any]:
        """Check availability status of Gateway, all 5 subsystem APIs, and Ollama using global common probes."""
        async with httpx.AsyncClient() as client:
            tasks = [
                common.probe_service_health(
                    client=client,
                    base_url=url_info["url"],
                    port=url_info["port"],
                    timeout=config.HEALTH_TIMEOUT
                )
                for name, url_info in config.APIS.items()
            ]
            ollama_task = common.probe_ollama_status(
                client=client,
                host=config.OLLAMA_HOST,
                timeout=config.HEALTH_TIMEOUT
            )

            results = await asyncio.gather(*tasks)
            ollama_status = await ollama_task

        apis_status = {name: res for name, res in zip(config.APIS.keys(), results)}

        return {
            "gateway": "online",
            "apis": apis_status,
            "ollama": ollama_status,
        }



orchestrator_service = OrchestratorService()
