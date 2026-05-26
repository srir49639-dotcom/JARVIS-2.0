# ============================================================
# JARVIS - Browser & Web Module
# ============================================================

import re
import webbrowser

import pywhatkit
import requests
import wikipedia

import config
from modules.app_manager import AppManager


class BrowserModule:
    """Web browsing, search, Wikipedia, and weather."""

    URLS = config.WEBSITES

    @classmethod
    def open_site(cls, site_name):
        """Open a predefined website."""
        site_name = site_name.lower().strip()
        for key, url in cls.URLS.items():
            if key in site_name:
                try:
                    webbrowser.open(url)
                    AppManager.register_open(key, kind="website", extra={"url": url})
                    return True, f"Opening {key}, sir."
                except Exception as e:
                    return False, f"Could not open {key}: {e}"
        return False, f"Website '{site_name}' not recognized, sir."

    @staticmethod
    def google_search(query):
        """Search Google for a query."""
        try:
            query = query.strip()
            if not query:
                return False, "What should I search for, sir?"
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            AppManager.register_open("google", kind="website", extra={"search": query})
            return True, f"Searching Google for {query}, sir."
        except Exception as e:
            return False, f"Search failed: {e}"

    @staticmethod
    def youtube_search(query):
        """Search YouTube for a query."""
        try:
            query = query.strip()
            if not query:
                return False, "What should I search on YouTube, sir?"
            pywhatkit.playonyt(query)
            AppManager.register_open("youtube", kind="website", extra={"search": query})
            return True, f"Searching YouTube for {query}, sir."
        except Exception as e:
            return False, f"YouTube search failed: {e}"

    @staticmethod
    def wikipedia_summary(topic):
        """Get Wikipedia summary for a topic."""
        try:
            topic = topic.strip()
            if not topic:
                return "Please specify a topic for Wikipedia, sir."
            wikipedia.set_lang("en")
            summary = wikipedia.summary(topic, sentences=3)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple results found. Try: {e.options[0]}, sir."
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for {topic}, sir."
        except Exception as e:
            return f"Wikipedia error: {e}"

    @classmethod
    def get_weather(cls, city=None):
        """Get weather information."""
        city = city or config.DEFAULT_CITY
        if not config.WEATHER_API_KEY or config.WEATHER_API_KEY == "":
            return cls._weather_fallback(city)
        try:
            url = (
                f"http://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={config.WEATHER_API_KEY}&units=metric"
            )
            response = requests.get(url, timeout=10)
            data = response.json()
            if response.status_code != 200:
                return cls._weather_fallback(city)
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            return (
                f"Weather in {city}: {desc}, {temp} degrees Celsius, "
                f"humidity {humidity} percent, sir."
            )
        except Exception:
            return cls._weather_fallback(city)

    @staticmethod
    def _weather_fallback(city):
        """Fallback weather using wttr.in."""
        try:
            url = f"https://wttr.in/{city}?format=3"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return f"Weather for {city}: {response.text.strip()}, sir."
            return f"Could not fetch weather for {city}, sir."
        except Exception as e:
            return f"Weather unavailable: {e}"

    @staticmethod
    def extract_search_query(command, triggers):
        """Extract search query after trigger phrase."""
        command = command.lower()
        for trigger in triggers:
            if trigger in command:
                return command.split(trigger, 1)[-1].strip()
        return ""

    @staticmethod
    def extract_after(command, keyword):
        """Extract text after a keyword."""
        match = re.search(rf"{keyword}\s+(.+)", command, re.IGNORECASE)
        return match.group(1).strip() if match else ""
