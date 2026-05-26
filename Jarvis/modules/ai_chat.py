# ============================================================
# JARVIS - AI Chat Module (Gemini / OpenAI)
# ============================================================

import random
import config
from modules.memory_manager import memory

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIChat:
    """AI-powered chat using Gemini (Primary) or OpenAI, with offline fallback."""

    _chat_mode = False

    OFFLINE_RESPONSES = {
        "hello": "Hello sir. JARVIS online and ready to assist you.",
        "hi": "Good day sir. How may I assist you?",
        "how are you": "All systems operational, sir. I'm functioning at peak efficiency.",
        "who are you": "I am JARVIS, your personal desktop assistant, sir.",
        "what can you do": (
            "I can control your system, browse the web, manage notes and tasks, "
            "play media, take screenshots, run AI chat, and much more, sir."
        ),
        "thank": "You're welcome, sir. Always at your service.",
        "bye": "Goodbye sir. JARVIS signing off.",
        "time": None,
        "date": None,
    }

    FALLBACK_GENERIC = [
        "An interesting query, sir. I recommend configuring the Gemini or OpenAI API for deeper analysis.",
        "I'm processing that locally, sir. My offline capabilities are somewhat limited.",
        "Noted, sir. For full intelligence, please configure your AI API key in config.py.",
    ]

    @classmethod
    def is_chat_mode(cls):
        return cls._chat_mode

    @classmethod
    def enable_chat_mode(cls):
        cls._chat_mode = True
        return "Chat mode activated, sir. Ask me anything."

    @classmethod
    def disable_chat_mode(cls):
        cls._chat_mode = False
        return "Chat mode deactivated, sir."

    @classmethod
    def _is_gemini_configured(cls):
        key = config.GEMINI_API_KEY
        return GEMINI_AVAILABLE and key and key != "your-gemini-api-key-here" and len(key) > 10

    @classmethod
    def _is_openai_configured(cls):
        key = config.OPENAI_API_KEY
        return OPENAI_AVAILABLE and key and key != "your-openai-api-key-here" and len(key) > 10

    @classmethod
    def ask(cls, question):
        """Process a question through Gemini, OpenAI, or offline fallback."""
        if not question:
            return "I didn't catch that, sir."

        if cls._is_gemini_configured():
            response = cls._ask_gemini(question)
            if response:
                return response

        if cls._is_openai_configured():
            response = cls._ask_openai(question)
            if response:
                return response

        return cls._offline_response(question)

    @classmethod
    def _ask_gemini(cls, question):
        """Query Gemini API."""
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            
            # Use appropriate model
            model = genai.GenerativeModel(
                model_name=config.GEMINI_MODEL,
                system_instruction=f"You are {config.ASSISTANT_NAME}, an Iron Man style AI assistant. "
                                   f"Address the user as {config.USER_NAME}. Be concise, witty, and helpful. "
                                   f"Keep responses under 3 sentences for voice output."
            )
            
            # Format history for Gemini
            # Gemini expects history as [{'role': 'user'/'model', 'parts': ['text']}]
            formatted_history = []
            for msg in memory.get_context():
                role = "user" if msg["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [msg["content"]]})
                
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(question)
            
            answer = response.text.strip()
            
            # Save to memory
            memory.add_message("user", question)
            memory.add_message("assistant", answer)
            
            return answer
        except Exception as e:
            print(f"[Gemini Error] {e}")
            return None

    @classmethod
    def _ask_openai(cls, question):
        """Query OpenAI API."""
        try:
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        f"You are {config.ASSISTANT_NAME}, a witty AI assistant "
                        f"like Iron Man's JARVIS. Address user as {config.USER_NAME}. "
                        "Keep answers brief for voice."
                    ),
                }
            ]
            
            # Append memory context
            messages.extend(memory.get_context())
            messages.append({"role": "user", "content": question})

            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
            )
            answer = response.choices[0].message.content.strip()
            
            # Save to memory
            memory.add_message("user", question)
            memory.add_message("assistant", answer)
            
            return answer
        except Exception as e:
            print(f"[OpenAI Error] {e}")
            return None

    @classmethod
    def _offline_response(cls, question):
        """Generate offline response without API."""
        import datetime
        q = question.lower().strip()

        for key, response in cls.OFFLINE_RESPONSES.items():
            if key in q:
                if key == "time":
                    now = datetime.datetime.now().strftime("%I:%M %p")
                    return f"The time is {now}, sir."
                if key == "date":
                    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
                    return f"Today is {today}, sir."
                return response

        if "?" in q:
            responses = [
                f"Regarding '{question[:50]}', I'd need cloud AI for a full answer, sir.",
                "That's beyond my offline knowledge base, sir. Try configuring Gemini or OpenAI.",
            ]
            return random.choice(responses)

        return random.choice(cls.FALLBACK_GENERIC)
