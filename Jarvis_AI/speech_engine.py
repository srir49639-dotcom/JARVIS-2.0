"""
Jarvis AI Assistant -- Speech Engine
"""
import speech_recognition as sr
import pyttsx3
import threading
import time
import re
from colorama import Fore, Style
import config

_tts_lock = threading.Lock()
_tts_engine = None

def _get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty("rate", config.TTS_RATE)
        _tts_engine.setProperty("volume", config.TTS_VOLUME)
        voices = _tts_engine.getProperty("voices")
        for v in voices:
            if "david" in v.name.lower() or "zira" not in v.name.lower():
                _tts_engine.setProperty("voice", v.id)
                break
    return _tts_engine

def speak(text):
    print(f"{Fore.CYAN}[JARVIS]{Style.RESET_ALL} {text}")
    with _tts_lock:
        engine = _get_tts_engine()
        engine.say(text)
        engine.runAndWait()
    time.sleep(0.5)

_recogniser = None

def _get_recogniser():
    global _recogniser
    if _recogniser is None:
        _recogniser = sr.Recognizer()
        _recogniser.energy_threshold = config.ENERGY_THRESHOLD
        _recogniser.pause_threshold = config.PAUSE_THRESHOLD
        _recogniser.dynamic_energy_threshold = config.DYNAMIC_ENERGY
    return _recogniser

def listen_for_wake_word():
    recogniser = _get_recogniser()
    print(f"{Fore.YELLOW}[LISTENING]{Style.RESET_ALL} Say \"{config.WAKE_WORD}\" ...")
    with sr.Microphone() as source:
        recogniser.adjust_for_ambient_noise(source, duration=0.5)
        while True:
            try:
                audio = recogniser.listen(source, timeout=None, phrase_time_limit=5)
                text = recogniser.recognize_google(audio).lower().strip()
                print(f"{Fore.WHITE}[HEARD]{Style.RESET_ALL} {text}")
                if config.WAKE_WORD in text:
                    return text
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"{Fore.RED}[STT ERROR]{Style.RESET_ALL} {e}")
                time.sleep(1)

def extract_command_from_wake(text):
    cmd = text.lower()
    cmd = cmd.replace(config.WAKE_WORD, "").strip()
    cmd = re.sub(r"^(hey|ok|okay)\s+", "", cmd)
    return cmd.strip()

def listen_for_command(prompt="Yes? How can I help?"):
    recogniser = _get_recogniser()
    speak(prompt)
    with sr.Microphone() as source:
        recogniser.adjust_for_ambient_noise(source, duration=0.3)
        print(f"{Fore.GREEN}[COMMAND]{Style.RESET_ALL} Listening...")
        try:
            audio = recogniser.listen(source, timeout=8, phrase_time_limit=config.PHRASE_TIME_LIMIT)
        except sr.WaitTimeoutError:
            speak("I did not hear anything. Try again.")
            return None
    try:
        text = recogniser.recognize_google(audio).lower().strip()
        print(f"{Fore.GREEN}[COMMAND TEXT]{Style.RESET_ALL} \"{text}\"")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I did not catch that.")
        return None
    except sr.RequestError:
        speak("Speech service is unavailable. Check your internet.")
        return None

def listen_yes_no():
    recogniser = _get_recogniser()
    with sr.Microphone() as source:
        recogniser.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recogniser.listen(source, timeout=8, phrase_time_limit=4)
            return recogniser.recognize_google(audio).lower().strip()
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return None
