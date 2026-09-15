import io
import json
import base64
import tempfile
import logging
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.command_processor import command_processor

logger = logging.getLogger("speech_api.websocket")

router = APIRouter(tags=["WebSocket Voice Stream"])

@router.websocket("/ws/voice-stream")
async def websocket_voice_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio streaming and speech interaction.

    Clients can send:
    1. Raw binary audio bytes (WAV/PCM/WebM chunks)
    2. JSON messages:
       - {"action": "chunk", "data": "<base64_encoded_audio>"}
       - {"action": "commit"} (finalize current buffer and execute command)
       - {"action": "reset"} (clear current audio buffer)
       - {"action": "ping"} -> returns pong

    Events emitted to client:
    - {"event": "connected", "message": "Voice stream initialized"}
    - {"event": "transcribing", "data": {"status": "processing_chunk", "bytes_received": ...}}
    - {"event": "recognized", "data": {"text": "...", "confidence": 0.95, "language": "en"}}
    - {"event": "executing", "data": {"intent": "...", "action": "..."}}
    - {"event": "done", "data": {"raw_text": "...", "intent": "...", "response": "...", "success": True, "timestamp": "..."}}
    - {"event": "error", "message": "..."}
    """
    await websocket.accept()
    await websocket.send_json({
        "event": "connected",
        "message": "SpeechAPI Voice Stream connected. Send audio chunks or JSON payload."
    })

    whisper_service = getattr(websocket.app.state, "whisper_service", None)
    if not whisper_service:
        from services.whisper_service import whisper_service as fallback_service
        whisper_service = fallback_service

    audio_buffer = bytearray()

    async def process_and_emit(audio_data: bytes):
        if len(audio_data) < 1000:
            await websocket.send_json({
                "event": "done",
                "data": {
                    "raw_text": "",
                    "intent": "unknown",
                    "action": "none",
                    "response": "Audio segment too short to recognize.",
                    "success": False
                }
            })
            return

        # Emit transcribing event
        await websocket.send_json({
            "event": "transcribing",
            "data": {"status": "analyzing_audio", "buffer_size": len(audio_data)}
        })

        temp_path = None
        try:
            # Write buffer to temp wav/webm file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                temp_path = Path(tmp.name)
                tmp.write(audio_data)

            # Transcribe via Whisper
            result = whisper_service.transcribe(str(temp_path))
            text = result.get("text", "").strip()

            # Emit recognized event
            await websocket.send_json({
                "event": "recognized",
                "data": {
                    "text": text,
                    "confidence": result.get("confidence", 0.0),
                    "language": result.get("language", "en")
                }
            })

            # Emit executing event
            cmd_result = command_processor.process_command(text)
            await websocket.send_json({
                "event": "executing",
                "data": {
                    "intent": cmd_result.intent,
                    "action": cmd_result.action
                }
            })

            # Emit done event
            await websocket.send_json({
                "event": "done",
                "data": cmd_result.model_dump()
            })

        except Exception as err:
            logger.error(f"WebSocket processing error: {err}", exc_info=True)
            await websocket.send_json({
                "event": "error",
                "message": f"Processing error: {str(err)}"
            })
        finally:
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message and message["bytes"]:
                chunk = message["bytes"]
                audio_buffer.extend(chunk)
                await websocket.send_json({
                    "event": "transcribing",
                    "data": {
                        "status": "receiving_stream",
                        "chunk_size": len(chunk),
                        "total_buffered": len(audio_buffer)
                    }
                })

            elif "text" in message and message["text"]:
                try:
                    data = json.loads(message["text"])
                    action = data.get("action", "")

                    if action == "chunk":
                        b64_str = data.get("data", "")
                        chunk = base64.b64decode(b64_str)
                        audio_buffer.extend(chunk)
                        await websocket.send_json({
                            "event": "transcribing",
                            "data": {
                                "status": "chunk_buffered",
                                "chunk_size": len(chunk),
                                "total_buffered": len(audio_buffer)
                            }
                        })

                    elif action == "commit":
                        # Process full buffered audio
                        buffer_copy = bytes(audio_buffer)
                        audio_buffer.clear()
                        await process_and_emit(buffer_copy)

                    elif action == "reset":
                        audio_buffer.clear()
                        await websocket.send_json({
                            "event": "reset",
                            "message": "Audio buffer cleared"
                        })

                    elif action == "ping":
                        await websocket.send_json({"event": "pong"})

                    elif action == "transcribe_direct":
                        # Client sent entire audio in single packet
                        b64_str = data.get("data", "")
                        audio_bytes = base64.b64decode(b64_str)
                        await process_and_emit(audio_bytes)

                    else:
                        await websocket.send_json({
                            "event": "error",
                            "message": f"Unknown action: '{action}'"
                        })

                except json.JSONDecodeError:
                    await websocket.send_json({
                        "event": "error",
                        "message": "Invalid JSON text frame received."
                    })

    except (WebSocketDisconnect, RuntimeError):
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket unhandled error: {e}", exc_info=True)

