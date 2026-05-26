"""Time, date, weather, jokes, Wikipedia."""
import datetime
import random
import re
import requests
import wikipedia
from speech_engine import speak
import config

def tell_time():
    now = datetime.datetime.now()
    speak(f"The time is {now.strftime('%I:%M %p')}.")

def tell_date():
    now = datetime.datetime.now()
    speak(f"Today is {now.strftime('%A, %B %d, %Y')}.")

def get_weather(city=""):
    city = city or config.DEFAULT_CITY
    url = f"https://wttr.in/{requests.utils.quote(city)}?format=3"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            speak(f"Weather in {city}: {r.text.strip()}")
        else:
            speak(f"Could not get weather for {city}.")
    except requests.RequestException:
        speak("Weather service unavailable. Check internet.")

def wiki_summary(query):
    if not query:
        speak("What topic?")
        return
    try:
        wikipedia.set_lang("en")
        speak(wikipedia.summary(query, sentences=2, auto_suggest=True))
    except wikipedia.exceptions.DisambiguationError as e:
        speak(f"Did you mean {e.options[0]}?")
    except wikipedia.exceptions.PageError:
        speak(f"No Wikipedia page for {query}.")
    except Exception:
        speak("Wikipedia error.")

_JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why do Java developers wear glasses? Because they do not C sharp.",
    "A SQL query walks into a bar and asks: Can I join you?",
]

def tell_joke():
    speak(random.choice(_JOKES))

def handle(command):
    cmd = command.lower().strip()
    if any(p in cmd for p in ("what time", "current time", "tell me the time", "what is the time")):
        tell_time(); return True
    if any(p in cmd for p in ("what date", "today", "what day", "current date")):
        tell_date(); return True
    if "weather" in cmd or "temperature" in cmd or "forecast" in cmd:
        city = ""
        for phrase in ("weather in ", "weather for ", "temperature in "):
            if phrase in cmd:
                city = cmd.split(phrase, 1)[-1].strip()
        get_weather(city); return True
    if "joke" in cmd or "funny" in cmd:
        tell_joke(); return True
    for trigger in ("tell me about ", "what is ", "who is ", "wikipedia ", "wiki "):
        if cmd.startswith(trigger):
            wiki_summary(cmd[len(trigger):].strip())
            return True
    return False
