# ============================================================
# JARVIS - Unified Speech Engine (GUI + Voice)
# Features: pyttsx3 fallback, OpenAI TTS, Whisper STT (Optional)
# ============================================================

import re
import threading
import time
import os

import pyttsx3
import speech_recognition as sr
from colorama import Fore, Style

import config

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SpeechEngine:
    """STT/TTS with wake-word loop and follow-up listening."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.ENERGY_THRESHOLD
        self.recognizer.pause_threshold = config.PAUSE_THRESHOLD
        self.recognizer.dynamic_energy_threshold = config.DYNAMIC_ENERGY

        # Fallback TTS
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty("rate", config.TTS_RATE)
        self.tts_engine.setProperty("volume", config.TTS_VOLUME)
        voices = self.tts_engine.getProperty("voices")
        for v in voices:
            if "david" in v.name.lower() or "zira" not in v.name.lower():
                self.tts_engine.setProperty("voice", v.id)
                break

        self._speaking = False
        self._lock = threading.Lock()
        self._mic_available = True
        self._mic_index = None
        
        # Advanced API Flags
        self.use_openai_tts = False
        self.use_openai_whisper = False
        
        if OPENAI_AVAILABLE and config.OPENAI_API_KEY and len(config.OPENAI_API_KEY) > 10 and config.OPENAI_API_KEY != "your-openai-api-key-here":
            # For now, disable cloud voice to save credits, but flag is here to enable.
            # self.use_openai_tts = True
            pass

        self._calibrate_mic()

    def _calibrate_mic(self):
        try:
            with sr.Microphone() as source:
                print(f"{Fore.CYAN}[JARVIS] Calibrating microphone...{Style.RESET_ALL}")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                self._mic_index = source.device_index
                print(f"{Fore.GREEN}[JARVIS] Microphone ready.{Style.RESET_ALL}")
        except Exception as e:
            self._mic_available = False
            print(f"{Fore.RED}[JARVIS] Microphone error: {e}{Style.RESET_ALL}")

    @property
    def mic_available(self):
        return self._mic_available

    def speak(self, text, block=True):
        if not text:
            return
        
        def run_tts():
            try:
                with self._lock:
                    self._speaking = True
                    if self.use_openai_tts:
                        self._openai_tts(text)
                    else:
                        self.tts_engine.say(str(text))
                        self.tts_engine.runAndWait()
            except Exception as e:
                print(f"{Fore.RED}[TTS Error] {e}{Style.RESET_ALL}")
            finally:
                self._speaking = False
                time.sleep(config.POST_SPEAK_DELAY)

        if block:
            run_tts()
        else:
            threading.Thread(target=run_tts, daemon=True).start()

    def _openai_tts(self, text):
        """Use OpenAI TTS API for high quality natural voice."""
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text,
        )
        # We need to save to a file and play it
        import tempfile
        import pygame
        temp_audio = os.path.join(tempfile.gettempdir(), "jarvis_tts.mp3")
        response.stream_to_file(temp_audio)
        
        pygame.mixer.init()
        pygame.mixer.music.load(temp_audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()

    def is_speaking(self):
        return self._speaking

    def _recognize(self, audio):
        if self.use_openai_whisper:
            return self._recognize_whisper(audio)
        try:
            return self.recognizer.recognize_google(audio).lower().strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"{Fore.RED}[STT API] {e}{Style.RESET_ALL}")
            return None

    def _recognize_whisper(self, audio):
        """Use OpenAI Whisper API for accurate STT."""
        import tempfile
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        try:
            wav_data = audio.get_wav_data()
            temp_wav = os.path.join(tempfile.gettempdir(), "jarvis_stt.wav")
            with open(temp_wav, "wb") as f:
                f.write(wav_data)
            
            with open(temp_wav, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcription.text.lower().strip()
        except Exception as e:
            print(f"{Fore.RED}[Whisper Error] {e}{Style.RESET_ALL}")
            return None

    def listen(self, timeout=None, phrase_time_limit=None, show_prompt=True):
        """Single phrase listen."""
        if not self._mic_available:
            return None
        timeout = timeout if timeout is not None else config.LISTEN_TIMEOUT
        phrase_limit = phrase_time_limit or config.PHRASE_TIME_LIMIT
        try:
            with sr.Microphone(device_index=self._mic_index) as source:
                if show_prompt:
                    print(f"{Fore.YELLOW}[Listening...]{Style.RESET_ALL}")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.35)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )
            text = self._recognize(audio)
            if text:
                print(f"{Fore.GREEN}You said: {text}{Style.RESET_ALL}")
            return text
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"{Fore.RED}[Listen Error] {e}{Style.RESET_ALL}")
            return None

    def listen_for_wake(self, stop_check=None):
        """Block until wake word heard. Returns full heard text."""
        if not self._mic_available:
            return None
        print(
            f"{Fore.YELLOW}[WAITING]{Style.RESET_ALL} "
            f'Say "{config.WAKE_WORD}" or "jarvis"...'
        )
        with sr.Microphone(device_index=self._mic_index) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            while True:
                if stop_check and stop_check():
                    return None
                try:
                    audio = self.recognizer.listen(
                        source, timeout=2, phrase_time_limit=6
                    )
                    text = self._recognize(audio)
                    if text:
                        print(f"{Fore.WHITE}[Heard]{Style.RESET_ALL} {text}")
                        if self.contains_wake_word(text):
                            return text
                except sr.WaitTimeoutError:
                    pass
                except Exception:
                    time.sleep(0.2)

    def listen_for_command(self, speak_prompt=True):
        """Listen for command after wake (no wake word required)."""
        if speak_prompt:
            self.speak("Yes sir?")
        return self.listen(timeout=config.LISTEN_TIMEOUT, show_prompt=True)

    def listen_yes_no(self):
        """Short listen for confirmation."""
        return self.listen(timeout=6, phrase_time_limit=4, show_prompt=False)

    @staticmethod
    def contains_wake_word(text):
        if not text:
            return False
        text = text.lower()
        if config.WAKE_WORD in text:
            return True
        return any(w in text for w in config.WAKE_WORDS)

    @staticmethod
    def extract_command_from_wake(text):
        if not text:
            return ""
        cmd = text.lower()
        cmd = cmd.replace(config.WAKE_WORD, "")
        for w in config.WAKE_WORDS:
            cmd = cmd.replace(w, "")
        cmd = re.sub(r"^(hey|ok|okay|please)\s+", "", cmd.strip())
        return re.sub(r"\s+", " ", cmd).strip()

    @staticmethod
    def is_direct_command(text):
        if not text or len(text) < 3:
            return False
        text = text.lower()
        triggers = (
            "open ", "close ", "quit ", "exit ", "kill ", "stop", "goodbye", "bye",
            "search ", "play ", "lock", "shutdown",
            "restart", "what time", "what is the time", "weather",
            "battery", "cpu", "ram", "screenshot", "volume", "mute",
            "remember", "note ", "todo", "timer", "alarm", "help",
            "joke", "wikipedia", "youtube", "google",
        )
        return any(t in text for t in triggers)
