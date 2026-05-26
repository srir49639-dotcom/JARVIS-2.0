"""Google and YouTube search."""
import webbrowser
import urllib.parse
from speech_engine import speak

def google_search(query):
    if not query:
        speak("What should I search for?")
        return
    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    speak(f"Searching Google for {query}.")
    webbrowser.open(url)

def youtube_search(query):
    if not query:
        speak("What should I search on YouTube?")
        return
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
    speak(f"Searching YouTube for {query}.")
    webbrowser.open(url)

def handle(command):
    cmd = command.lower().strip()
    for prefix in ("search youtube for ", "youtube search ", "play on youtube ", "youtube "):
        if cmd.startswith(prefix):
            youtube_search(cmd[len(prefix):].strip())
            return True
    for prefix in ("search for ", "search ", "google search ", "google for ", "look up ", "find "):
        if cmd.startswith(prefix):
            google_search(cmd[len(prefix):].strip())
            return True
    return False
