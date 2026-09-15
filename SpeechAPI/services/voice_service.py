import speech_recognition as sr
import threading
import queue
import time
import logging

try:
    from core.logger import AppLogger
except ImportError:
    try:
        from SpeechAPI.core.logger import AppLogger
    except ImportError:
        class AppLogger:
            def __init__(self, name: str = "voice_service"):
                self.logger = logging.getLogger(name)
            def info(self, msg: str, *args, **kwargs):
                self.logger.info(msg, *args, **kwargs)
            def warning(self, msg: str, *args, **kwargs):
                self.logger.warning(msg, *args, **kwargs)
            def error(self, msg: str, *args, **kwargs):
                self.logger.error(msg, *args, **kwargs)
            def debug(self, msg: str, *args, **kwargs):
                self.logger.debug(msg, *args, **kwargs)

class VoiceService:
    def __init__(self, logger: AppLogger = None, on_command_callback = None):
        self.logger = logger or AppLogger("voice_service")
        self.on_command = on_command_callback or (lambda text: None)
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self._thread = None
        self.audio_queue = queue.Queue()
        
        # Optimized settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5

    def start(self):
        if self.is_listening:
            return
        self.is_listening = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        self.logger.info("Voice listening started")

    def stop(self):
        self.is_listening = False
        self.logger.info("Voice listening stopped")

    def _listen_loop(self):
        mic_index = self._find_microphone()
        
        try:
            mic_context = sr.Microphone(device_index=mic_index) if mic_index is not None else sr.Microphone()
        except Exception as e:
            self.logger.error(f"Cannot initialize microphone: {e}")
            self.is_listening = False
            return

        try:
            with mic_context as source:
                self.logger.info("Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                self.logger.info(f"Microphone ready! Threshold: {int(self.recognizer.energy_threshold)}")
                
                while self.is_listening:
                    try:
                        self.logger.info("Listening for command...")
                        audio = self.recognizer.listen(
                            source,
                            timeout=8,
                            phrase_time_limit=12
                        )
                        
                        # Try English first
                        try:
                            text = self.recognizer.recognize_google(
                                audio, 
                                language="en-US",
                                show_all=False
                            )
                            self.logger.info(f"Recognized (EN): {text}")
                            if text and len(text.strip()) > 1:
                                self.on_command(text)
                            continue
                        except sr.UnknownValueError:
                            pass
                        
                        # Try Urdu
                        try:
                            text = self.recognizer.recognize_google(
                                audio,
                                language="ur-PK",
                                show_all=False
                            )
                            self.logger.info(f"Recognized (UR): {text}")
                            if text and len(text.strip()) > 1:
                                self.on_command(text)
                            continue
                        except sr.UnknownValueError:
                            pass
                        
                        self.logger.warning("Could not understand audio")
                        
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        self.logger.error(f"Voice error: {e}")
                        time.sleep(1)
        except Exception as e:
            self.logger.error(f"Microphone loop terminated with error: {e}")
            self.is_listening = False

    def _find_microphone(self):
        try:
            mics = sr.Microphone.list_microphone_names()
            for i, name in enumerate(mics):
                if any(k in name.lower() for k in ["array", "realtek", "microphone"]):
                    self.logger.info(f"Using mic: [{i}] {name}")
                    return i
        except Exception as e:
            self.logger.warning(f"Could not list microphones: {e}")
        return None
