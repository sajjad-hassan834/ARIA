import re
import logging
from typing import Dict, Any, List, Tuple
from rapidfuzz import fuzz, process

import config
from services.llm_service import classify_intent_llm

logger = logging.getLogger("speech_api.nlu")

# Comprehensive intent definitions and phrases for desktop controller
INTENT_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "open_browser": {
        "action": "open_browser",
        "default_response": "Opening browser now",
        "phrases": [
            ("open browser", "en"),
            ("launch browser", "en"),
            ("open chrome", "en"),
            ("browser kholo", "roman_urdu"),
            ("kholo browser", "roman_urdu"),
            ("internet kholo", "roman_urdu"),
            ("chrome kholo", "roman_urdu"),
            ("kholo", "roman_urdu"),
            ("براؤزر کھولو", "ur"),
        ],
    },
    "open_notepad": {
        "action": "open_notepad",
        "default_response": "Opening Notepad",
        "phrases": [
            ("open notepad", "en"),
            ("launch notepad", "en"),
            ("notepad kholo", "roman_urdu"),
            ("notepad open karo", "roman_urdu"),
            ("نوٹ پیڈ کھولو", "ur"),
        ],
    },
    "open_calculator": {
        "action": "open_calculator",
        "default_response": "Opening Calculator",
        "phrases": [
            ("open calculator", "en"),
            ("launch calculator", "en"),
            ("calculator kholo", "roman_urdu"),
            ("hisaab kholo", "roman_urdu"),
            ("کیلکولیٹر کھولو", "ur"),
        ],
    },
    "open_explorer": {
        "action": "open_explorer",
        "default_response": "Opening File Explorer",
        "phrases": [
            ("open explorer", "en"),
            ("open file explorer", "en"),
            ("open my computer", "en"),
            ("file explorer kholo", "roman_urdu"),
            ("files kholo", "roman_urdu"),
            ("فائل مینیجر کھولو", "ur"),
        ],
    },
    "open_youtube": {
        "action": "open_youtube",
        "default_response": "Opening YouTube",
        "phrases": [
            ("open youtube", "en"),
            ("launch youtube", "en"),
            ("youtube kholo", "roman_urdu"),
            ("mujhe youtube dekhna hai", "roman_urdu"),
            ("youtube chalao", "roman_urdu"),
            ("یوٹیوب کھولو", "ur"),
        ],
    },
    "open_google": {
        "action": "open_google",
        "default_response": "Opening Google",
        "phrases": [
            ("open google", "en"),
            ("google kholo", "roman_urdu"),
            ("گوگل کھولو", "ur"),
        ],
    },
    "search_web": {
        "action": "search_web",
        "default_response": "Searching on the web",
        "phrases": [
            ("search web", "en"),
            ("search google", "en"),
            ("google par search karo", "roman_urdu"),
            ("google par weather dekhna hai", "roman_urdu"),
            ("search karo", "roman_urdu"),
            ("internet par dhoondo", "roman_urdu"),
            ("گوگل پر تلاش کرو", "ur"),
        ],
    },
    "type_text": {
        "action": "type_text",
        "default_response": "Ready to type text",
        "phrases": [
            ("type text", "en"),
            ("start typing", "en"),
            ("mujhe kuch likhna hai", "roman_urdu"),
            ("kuch likho", "roman_urdu"),
            ("likhna shuru karo", "roman_urdu"),
            ("ٹائپ کرو", "ur"),
        ],
    },
    "screenshot": {
        "action": "capture_screen",
        "default_response": "Taking screenshot now",
        "phrases": [
            ("screenshot", "en"),
            ("take screenshot", "en"),
            ("capture screen", "en"),
            ("screenshot lo", "roman_urdu"),
            ("screen ka photo lo", "roman_urdu"),
            ("meri screen dikhao", "roman_urdu"),
            ("tasveer lo", "roman_urdu"),
            ("اسکرین شاٹ لو", "ur"),
        ],
    },
    "volume_up": {
        "action": "volume_up",
        "default_response": "Increasing volume",
        "phrases": [
            ("volume up", "en"),
            ("increase volume", "en"),
            ("louder", "en"),
            ("awaz barha", "roman_urdu"),
            ("awaz barhao", "roman_urdu"),
            ("awaz zyada karo", "roman_urdu"),
            ("awaz teez karo", "roman_urdu"),
            ("آواز بڑھاؤ", "ur"),
        ],
    },
    "volume_down": {
        "action": "volume_down",
        "default_response": "Decreasing volume",
        "phrases": [
            ("volume down", "en"),
            ("decrease volume", "en"),
            ("quieter", "en"),
            ("awaz kam karo", "roman_urdu"),
            ("awaz dheemi karo", "roman_urdu"),
            ("awaz ghatao", "roman_urdu"),
            ("آواز کم کرو", "ur"),
        ],
    },
    "mute": {
        "action": "mute",
        "default_response": "Muting audio",
        "phrases": [
            ("mute", "en"),
            ("mute sound", "en"),
            ("silence", "en"),
            ("awaz band karo", "roman_urdu"),
            ("awaaz bilkul band karo", "roman_urdu"),
            ("awaaz band", "roman_urdu"),
            ("chup karo", "roman_urdu"),
            ("آواز بند کرو", "ur"),
        ],
    },
    "close_window": {
        "action": "close_window",
        "default_response": "Closing window",
        "phrases": [
            ("close window", "en"),
            ("close application", "en"),
            ("close app", "en"),
            ("close", "en"),
            ("band karo yeh sab", "roman_urdu"),
            ("band karo", "roman_urdu"),
            ("band kardo", "roman_urdu"),
            ("khatam karo", "roman_urdu"),
            ("بند کرو", "ur"),
        ],
    },
    "minimize_window": {
        "action": "minimize_window",
        "default_response": "Minimizing window",
        "phrases": [
            ("minimize window", "en"),
            ("minimize", "en"),
            ("chota karo", "roman_urdu"),
            ("minimize karo", "roman_urdu"),
        ],
    },
    "maximize_window": {
        "action": "maximize_window",
        "default_response": "Maximizing window",
        "phrases": [
            ("maximize window", "en"),
            ("maximize", "en"),
            ("bada karo", "roman_urdu"),
            ("maximize karo", "roman_urdu"),
        ],
    },
    "scroll_up": {
        "action": "scroll_up",
        "default_response": "Scrolling up",
        "phrases": [
            ("scroll up", "en"),
            ("up", "en"),
            ("upar jao", "roman_urdu"),
            ("upar scroll karo", "roman_urdu"),
        ],
    },
    "scroll_down": {
        "action": "scroll_down",
        "default_response": "Scrolling down",
        "phrases": [
            ("scroll down", "en"),
            ("down", "en"),
            ("neeche jao", "roman_urdu"),
            ("neeche scroll karo", "roman_urdu"),
        ],
    },
    "copy": {
        "action": "copy",
        "default_response": "Copied to clipboard",
        "phrases": [
            ("copy", "en"),
            ("copy text", "en"),
            ("copy this", "en"),
            ("copy kar do", "roman_urdu"),
            ("sab kuch copy karo", "roman_urdu"),
            ("copy karo", "roman_urdu"),
        ],
    },
    "paste": {
        "action": "paste",
        "default_response": "Pasting from clipboard",
        "phrases": [
            ("paste", "en"),
            ("paste text", "en"),
            ("paste kar do", "roman_urdu"),
            ("paste karo", "roman_urdu"),
        ],
    },
    "save": {
        "action": "save",
        "default_response": "Saving file",
        "phrases": [
            ("save", "en"),
            ("save file", "en"),
            ("save karo", "roman_urdu"),
            ("mehfooz karo", "roman_urdu"),
        ],
    },
    "shutdown": {
        "action": "shutdown",
        "default_response": "Shutting down computer",
        "phrases": [
            ("shutdown", "en"),
            ("shut down computer", "en"),
            ("turn off pc", "en"),
            ("computer band karo", "roman_urdu"),
            ("pc band karo", "roman_urdu"),
            ("کمپیوٹر بند کرو", "ur"),
        ],
    },
    "restart": {
        "action": "restart",
        "default_response": "Restarting computer",
        "phrases": [
            ("restart", "en"),
            ("reboot", "en"),
            ("restart karo", "roman_urdu"),
            ("دوبارہ شروع کرو", "ur"),
        ],
    },
    "lock_screen": {
        "action": "lock_screen",
        "default_response": "Locking screen",
        "phrases": [
            ("lock screen", "en"),
            ("lock computer", "en"),
            ("screen lock karo", "roman_urdu"),
            ("لاک اسکرین", "ur"),
        ],
    },
    "time_check": {
        "action": "check_time",
        "default_response": "Checking current time",
        "phrases": [
            ("what time is it", "en"),
            ("time kya hua hai", "roman_urdu"),
            ("waqt batao", "roman_urdu"),
        ],
    },
    "greeting": {
        "action": "greet_user",
        "default_response": "Hello! How can I assist you today?",
        "phrases": [
            ("hello", "en"),
            ("hi", "en"),
            ("salam", "roman_urdu"),
            ("kya haal hai", "roman_urdu"),
        ],
    },
}

ROMAN_URDU_KEYWORDS = {
    "kholo", "band", "karo", "krdo", "kro", "awaz", "awaaz", "barha", "barhao",
    "teez", "kam", "dheemi", "ghatao", "lo", "lelo", "tasveer", "chalao", "roko",
    "kya", "hai", "waqt", "salam", "haal", "kaise", "batao", "sunao", "mera", "meri",
    "apna", "shukriya", "theek", "bhai", "janaab", "mujhe", "zyada", "dekhna", "likhna",
    "dhoondo", "mehfooz", "chota", "bada", "upar", "neeche", "yeh", "sab", "bilkul"
}

class NLUService:
    def __init__(self, fuzzy_threshold: float = config.FUZZY_THRESHOLD):
        self.threshold = fuzzy_threshold
        self.phrase_database: List[Tuple[str, str, str]] = []
        for intent, data in INTENT_DEFINITIONS.items():
            for phrase, lang in data["phrases"]:
                self.phrase_database.append((phrase.lower().strip(), intent, lang))
        self.all_phrases = [item[0] for item in self.phrase_database]

    def detect_language(self, text: str) -> str:
        """Auto-detect language: Urdu script, Roman Urdu keywords, or English."""
        cleaned = text.strip()
        if not cleaned:
            return "en"

        if re.search(r"[\u0600-\u06FF]", cleaned):
            return "ur"

        words = set(re.findall(r"\b\w+\b", cleaned.lower()))
        if words.intersection(ROMAN_URDU_KEYWORDS):
            return "roman_urdu"

        return "en"

    def match_intent(self, text: str) -> Dict[str, Any]:
        """
        NLU Intent Matching Pipeline with Priority Order:
        1. Exact hardcoded match -> return immediately
        2. RapidFuzz fuzzy match (>75%) -> return immediately
        3. phi3:mini via Ollama -> return result if recognized
        Fallback: Graceful fallback to fuzzy match or unknown if Ollama is not running.
        """
        raw_input = text.strip()
        if not raw_input:
            return {
                "input": raw_input,
                "intent": "unknown",
                "confidence": 0.0,
                "language": "en",
                "parameters": {},
                "response": "Could not understand empty input"
            }

        input_lower = raw_input.lower()
        detected_lang = self.detect_language(raw_input)

        # -------------------------------------------------------------
        # STEP 1: Exact hardcoded match
        # -------------------------------------------------------------
        for phrase, intent, lang in self.phrase_database:
            if input_lower == phrase:
                _, default_resp = self.get_intent_action_and_response(intent)
                return {
                    "input": raw_input,
                    "intent": intent,
                    "confidence": 1.0,
                    "language": lang if lang != "en" else detected_lang,
                    "parameters": {},
                    "response": default_resp
                }

        # -------------------------------------------------------------
        # STEP 2: RapidFuzz fuzzy match (> threshold, default 75%)
        # -------------------------------------------------------------
        best_match = process.extractOne(
            input_lower,
            self.all_phrases,
            scorer=fuzz.token_set_ratio
        )

        fuzzy_candidate = None
        if best_match:
            matched_phrase, score, index = best_match
            matched_intent = self.phrase_database[index][1]
            phrase_lang = self.phrase_database[index][2]
            confidence = round(score / 100.0, 2)

            if score >= self.threshold:
                effective_lang = detected_lang if detected_lang in ["ur", "roman_urdu"] else phrase_lang
                _, default_resp = self.get_intent_action_and_response(matched_intent)
                return {
                    "input": raw_input,
                    "intent": matched_intent,
                    "confidence": confidence,
                    "language": effective_lang,
                    "parameters": {},
                    "response": default_resp
                }
            else:
                fuzzy_candidate = {
                    "input": raw_input,
                    "intent": matched_intent if score >= 50 else "unknown",
                    "confidence": confidence,
                    "language": phrase_lang if phrase_lang != "en" else detected_lang,
                    "parameters": {},
                    "response": self.get_intent_action_and_response(matched_intent)[1] if score >= 50 else "Could not understand command"
                }

        # -------------------------------------------------------------
        # STEP 3: Dynamic intent classification with Ollama (phi3:mini)
        # -------------------------------------------------------------
        if getattr(config, "USE_LLM_FALLBACK", True):
            logger.info(f"Invoking Ollama ({config.OLLAMA_MODEL}) for dynamic intent understanding on: '{raw_input}'")
            llm_result = classify_intent_llm(raw_input)
            llm_intent = llm_result.get("intent", "unknown")

            if llm_intent and llm_intent != "unknown":
                llm_conf = float(llm_result.get("confidence", 0.90))
                llm_lang = llm_result.get("language", detected_lang)
                llm_params = llm_result.get("parameters", {})
                llm_resp = llm_result.get("response") or self.get_intent_action_and_response(llm_intent)[1]

                return {
                    "input": raw_input,
                    "intent": llm_intent,
                    "confidence": round(llm_conf, 2),
                    "language": llm_lang,
                    "parameters": llm_params,
                    "response": llm_resp
                }

        # -------------------------------------------------------------
        # Fallback: Use best fuzzy candidate or unknown
        # -------------------------------------------------------------
        if fuzzy_candidate and fuzzy_candidate["intent"] != "unknown":
            return fuzzy_candidate

        return {
            "input": raw_input,
            "intent": "unknown",
            "confidence": round((best_match[1] / 100.0) if best_match else 0.0, 2),
            "language": detected_lang,
            "parameters": {},
            "response": "Could not understand command"
        }

    def get_intent_action_and_response(self, intent: str) -> Tuple[str, str]:
        """Fetch standard action identifier and human-like response text for an intent."""
        if intent in INTENT_DEFINITIONS:
            entry = INTENT_DEFINITIONS[intent]
            return entry["action"], entry["default_response"]
        return "unrecognized_action", "I did not recognize that command. Please try again."


nlu_service = NLUService()
