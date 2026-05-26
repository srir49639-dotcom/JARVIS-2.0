# ============================================================
# JARVIS - Command Router (expanded voice commands)
# ============================================================

import re
import threading

import config
from modules.system_controls import SystemControls
from modules.shutdown import is_shutdown_command
from modules.browser import BrowserModule
from modules.media import MediaControls
from modules.utilities import Utilities
from modules.ai_chat import AIChat
from modules.notes import NotesManager
from modules.camera import CameraModule
from modules.extra_features import ExtraFeatures
from modules.alarm_service import AlarmService
from modules.app_manager import AppManager
from modules.finance import FinanceModule


class CommandRouter:
    """Route natural language commands to JARVIS modules."""

    def __init__(self, assistant):
        self.assistant = assistant
        self.alarms = AlarmService(assistant._respond)

    def process(self, command):
        """Return True if command was handled."""
        if not command:
            return False
        cmd = command.lower().strip()
        a = self.assistant

        # ---- Shut down JARVIS itself ----
        if is_shutdown_command(cmd):
            a.shutdown()
            return True

        # ---- Greetings / Help ----
        if any(g in cmd for g in ("hello", "hi ", "hey", "good morning", "good evening")):
            a._respond(f"Hello {config.USER_NAME}. JARVIS ready. Say help for commands.")
            return True
        if any(f in cmd for f in ("see you", "good night")):
            a._respond("Goodbye sir. Say hey jarvis when you need me.")
            return True
        if any(t in cmd for t in ("thank you", "thanks")):
            a._respond("You are welcome, sir.")
            return True
        if cmd in ("help", "commands", "what can you do", "list commands"):
            a._respond(ExtraFeatures.help_commands())
            return True

        # ---- AI Chat ----
        if any(p in cmd for p in ("ask jarvis", "hey jarvis ask")):
            q = cmd.replace("ask jarvis", "").replace("hey jarvis ask", "").strip()
            a._respond(AIChat.ask(q))
            return True
        if "chat mode" in cmd or "enable chat" in cmd:
            a._respond(AIChat.enable_chat_mode())
            return True
        if any(p in cmd for p in ("exit chat", "disable chat", "stop chat")):
            a._respond(AIChat.disable_chat_mode())
            return True
        if AIChat.is_chat_mode():
            a._respond(AIChat.ask(cmd))
            return True

        # ---- Time / Date (flexible phrases) ----
        if re.search(r"\b(time|what.?s the time|what is the time|current time|tell me the time)\b", cmd):
            a._respond(ExtraFeatures.get_time())
            return True
        if re.search(r"\b(date|what.?s the date|what day|today.?s date)\b", cmd):
            a._respond(ExtraFeatures.get_date())
            return True

        # ---- Power ----
        if any(p in cmd for p in ("lock screen", "lock the screen", "lock laptop", "lock computer", "lock pc")):
            ok, msg = SystemControls.lock_screen()
            a._respond(msg)
            return True
        if any(p in cmd for p in ("shutdown", "shut down", "turn off")) and "cancel" not in cmd and "jarvis" not in cmd:
            a._ask_confirmation("shutdown", "Are you sure you want to shut down? Say yes or no.")
            return True
        if any(p in cmd for p in ("restart", "reboot")):
            a._ask_confirmation("restart", "Are you sure you want to restart? Say yes or no.")
            return True
        if "cancel shutdown" in cmd:
            ok, msg = SystemControls.cancel_shutdown()
            a._respond(msg)
            return True
        if "hibernate" in cmd:
            ok, msg = SystemControls.hibernate_system()
            a._respond(msg)
            return True
        if any(p in cmd for p in ("sleep mode", "go to sleep", "sleep now")):
            ok, msg = SystemControls.sleep_system()
            a._respond(msg)
            return True

        # ---- System status ----
        if "battery" in cmd:
            a._respond(SystemControls.get_battery())
            return True
        if "cpu" in cmd:
            a._respond(SystemControls.get_cpu_usage())
            return True
        if "ram" in cmd or "memory" in cmd:
            a._respond(SystemControls.get_ram_usage())
            return True
        if "uptime" in cmd:
            a._respond(SystemControls.get_uptime())
            return True
        if "disk" in cmd or "storage" in cmd:
            a._respond(ExtraFeatures.get_disk_usage())
            return True
        if "ip address" in cmd or "my ip" in cmd:
            a._respond(ExtraFeatures.get_ip_address())
            return True
        if "system info" in cmd or "computer info" in cmd:
            a._respond(ExtraFeatures.get_system_info())
            return True
        if "internet" in cmd and "speed" not in cmd:
            a._respond(SystemControls.check_internet())
            return True
        if "speed test" in cmd:
            a._respond("Running speed test, please wait sir.")
            a._respond(SystemControls.run_speed_test())
            return True
        if "temperature" in cmd or "thermal" in cmd:
            a._respond(SystemControls.get_thermal_stats())
            return True

        # ---- Close / Kill apps ----
        if cmd.startswith("terminate ") or cmd.startswith("force close "):
            target = re.sub(r"^(terminate|force close)\s+(the\s+)?", "", cmd).strip()
            ok, msg = SystemControls.kill_process(target)
            a._respond(msg)
            return True
        if any(cmd.startswith(p) for p in ("close ", "quit ", "exit ", "kill ")):
            target = re.sub(r"^(close|quit|exit|kill)\s+(the\s+)?", "", cmd).strip()
            if target in ("it", "that", "this", "last"):
                ok, msg = AppManager.close_last()
            elif target in ("browser", "browsers", "all browsers"):
                ok, msg = AppManager.close_all_browsers()
            else:
                if cmd.startswith("kill "):
                    ok, msg = SystemControls.kill_process(target)
                else:
                    ok, msg = AppManager.close(target)
            a._respond(msg)
            return True
        if cmd in ("close", "close it", "close that"):
            ok, msg = AppManager.close_last()
            a._respond(msg)
            return True

        # ---- Window control ----
        if "close window" in cmd or "close active window" in cmd:
            ok, msg = ExtraFeatures.close_active_window()
            a._respond(msg)
            return True
        if "minimize" in cmd:
            ok, msg = ExtraFeatures.minimize_window()
            a._respond(msg)
            return True
        if "maximize" in cmd:
            ok, msg = ExtraFeatures.maximize_window()
            a._respond(msg)
            return True
        if "switch window" in cmd or "alt tab" in cmd:
            ok, msg = ExtraFeatures.switch_window()
            a._respond(msg)
            return True
        if "empty recycle" in cmd or "clear recycle" in cmd:
            ok, msg = ExtraFeatures.empty_recycle_bin()
            a._respond(msg)
            return True

        # ---- Open apps / sites ----
        if cmd.startswith("open ") or cmd.startswith("launch ") or cmd.startswith("start "):
            target = re.sub(r"^(open|launch|start)\s+", "", cmd).strip()
            if "folder" in cmd or target in ("desktop", "documents", "downloads", "pictures", "music", "videos", "home"):
                folder = target.replace("folder", "").strip() or target
                ok, msg = ExtraFeatures.open_folder(folder)
                a._respond(msg)
                return True
            web_sites = (
                "google", "youtube", "github", "instagram", "chatgpt",
                "facebook", "twitter", "linkedin", "stackoverflow", "gmail",
                "whatsapp", "reddit", "amazon", "netflix",
            )
            if any(site in target for site in web_sites):
                ok, msg = BrowserModule.open_site(target)
                a._respond(msg)
                return True
            ok, msg = SystemControls.open_application(target)
            a._respond(msg)
            return True

        # ---- Search ----
        if cmd.startswith("search ") or cmd.startswith("google "):
            query = re.sub(r"^(search|google)\s+", "", cmd).strip()
            ok, msg = BrowserModule.google_search(query)
            a._respond(msg)
            return True
        if "youtube" in cmd and ("search" in cmd or "play" in cmd):
            query = BrowserModule.extract_search_query(
                cmd, ["search on youtube", "search youtube", "youtube search", "play on youtube", "play"]
            )
            if not query:
                query = cmd.split("youtube")[-1].replace("search", "").replace("play", "").strip()
            ok, msg = BrowserModule.youtube_search(query)
            a._respond(msg)
            return True

        # ---- Wikipedia / Weather / News ----
        if "wikipedia" in cmd or "wiki" in cmd or "tell me about" in cmd:
            topic = BrowserModule.extract_after(cmd, "wikipedia") or BrowserModule.extract_after(cmd, "tell me about")
            if not topic:
                topic = cmd.replace("wikipedia", "").replace("wiki", "").replace("tell me about", "").strip()
            a._respond(BrowserModule.wikipedia_summary(topic))
            return True
        if "weather" in cmd:
            city = BrowserModule.extract_after(cmd, "weather in") or BrowserModule.extract_after(cmd, "weather for")
            if not city:
                city = cmd.replace("weather", "").replace("in", "").replace("for", "").strip() or None
            a._respond(BrowserModule.get_weather(city))
            return True
        if "news" in cmd or "headline" in cmd:
            a._respond(ExtraFeatures.get_news_headline())
            return True
        if "crypto" in cmd or "price of" in cmd and any(c in cmd for c in ["bitcoin", "ethereum", "doge"]):
            coin = re.sub(r".*(price of|crypto)\s*", "", cmd).strip()
            if not coin:
                coin = "bitcoin" # Default
            ok, msg = FinanceModule.get_crypto_price(coin)
            a._respond(msg)
            return True
        if "stock" in cmd:
            ticker = re.sub(r".*(stock for|stock price of|stock)\s*", "", cmd).strip()
            if ticker:
                ok, msg = FinanceModule.get_stock_price(ticker)
                a._respond(msg)
                return True

        # ---- Media ----
        if "play on spotify" in cmd or "spotify play" in cmd:
            song = cmd.replace("play on spotify", "").replace("spotify play", "").replace("play", "").strip()
            if song:
                ok, msg = MediaControls.spotify_play_track(song)
                a._respond(msg)
                return True
        if "play music" in cmd or "start music" in cmd:
            ok, msg = MediaControls.play_music()
            a._respond(msg)
            return True
        if "pause" in cmd and "unpause" not in cmd:
            ok, msg = MediaControls.play_pause()
            a._respond(msg)
            return True
        if "next" in cmd and ("song" in cmd or "track" in cmd):
            ok, msg = MediaControls.next_track()
            a._respond(msg)
            return True
        if "previous" in cmd or "last song" in cmd:
            ok, msg = MediaControls.previous_track()
            a._respond(msg)
            return True
        if "volume up" in cmd or "increase volume" in cmd or "louder" in cmd:
            ok, msg = MediaControls.volume_up()
            a._respond(msg)
            return True
        if "volume down" in cmd or "decrease volume" in cmd or "quieter" in cmd:
            ok, msg = MediaControls.volume_down()
            a._respond(msg)
            return True
        if "mute" in cmd or "unmute" in cmd:
            ok, msg = MediaControls.mute()
            a._respond(msg)
            return True
        if "set volume to" in cmd or "volume to" in cmd:
            lvl = re.search(r'\d+', cmd)
            if lvl:
                ok, msg = SystemControls.set_volume(lvl.group())
                a._respond(msg)
                return True
        if "brightness" in cmd:
            lvl = re.search(r'\d+', cmd)
            if lvl:
                ok, msg = SystemControls.set_brightness(lvl.group())
                a._respond(msg)
                return True

        # ---- About JARVIS ----
        if "who are you" in cmd or "about yourself" in cmd or "what are you" in cmd:
            about_text = (
                "I am JARVIS, Just A Rather Very Intelligent System. "
                "I am a highly advanced artificial intelligence created to assist you with PC automation, "
                "information retrieval, and system diagnostics, sir."
            )
            a._respond(about_text)
            return True

        # ---- Notes / Tasks / Emails ----
        if "draft email" in cmd or "write email" in cmd or "send an email" in cmd:
            a._respond("What should be the subject of the email, sir?")
            subject = a.speech.listen(show_prompt=True) or "No Subject"
            
            a._respond("What should the email say, sir?")
            body = a.speech.listen(show_prompt=True) or "No body provided."
            
            ok, msg = ExtraFeatures.draft_email("", subject, body)
            a._respond(msg)
            return True
            
        if cmd.startswith("note ") or cmd.startswith("remember ") or cmd.startswith("save note "):
            for prefix in ("note ", "remember ", "save note "):
                if cmd.startswith(prefix):
                    ok, msg = NotesManager.save_note(command[len(prefix):].strip())
                    a._respond(msg)
                    return True
        if any(p in cmd for p in ("remember this", "save note", "take note", "note this")):
            content = cmd
            for t in ("remember this", "save note", "take note", "note this"):
                content = content.replace(t, "")
            content = content.strip()
            if content:
                ok, msg = NotesManager.save_note(content)
                a._respond(msg)
            else:
                a._respond("What should I remember, sir?")
            return True
        if "read notes" in cmd or "show notes" in cmd or "my notes" in cmd:
            a._respond(NotesManager.read_notes())
            return True
        if "clear notes" in cmd:
            ok, msg = NotesManager.clear_notes()
            a._respond(msg)
            return True
        if "add task" in cmd or "add todo" in cmd:
            task = cmd.replace("add task", "").replace("add todo", "").strip()
            if task:
                ok, msg = NotesManager.add_task(task)
                a._respond(msg)
            else:
                a._respond("What task should I add, sir?")
            return True
        if "show tasks" in cmd or "my tasks" in cmd or "todo" in cmd:
            a._respond(NotesManager.show_tasks())
            return True
        if "clear tasks" in cmd:
            ok, msg = NotesManager.clear_tasks()
            a._respond(msg)
            return True

        # ---- Utilities ----
        if "screenshot" in cmd or "screen shot" in cmd:
            ok, msg = Utilities.take_screenshot()
            a._respond(msg)
            return True
        alarm_result = self.alarms.handle(cmd)
        if alarm_result is not None:
            ok, msg = alarm_result
            a._respond(msg)
            return True
        if "clipboard" in cmd:
            if "read" in cmd or "what" in cmd:
                a._respond(ExtraFeatures.get_clipboard_content())
            else:
                a._respond(Utilities.read_clipboard())
            return True
        if "organize desktop" in cmd or "clean desktop" in cmd:
            ok, msg = ExtraFeatures.organize_desktop()
            a._respond(msg)
            return True
        if "qr code" in cmd:
            data = cmd.replace("qr code", "").replace("generate qr", "").replace("for", "").strip()
            ok, msg = Utilities.generate_qr_code(data)
            a._respond(msg)
            return True
        if "quote" in cmd or "motivat" in cmd:
            a._respond(Utilities.get_quote())
            return True
        if "joke" in cmd:
            a._respond(Utilities.get_joke())
            return True
        if "notify" in cmd or "remind me" in cmd:
            msg = re.sub(r".*(notify|remind me)\s*", "", cmd).strip()
            if msg:
                Utilities.send_notification("JARVIS", msg)
                a._respond(f"Reminder set: {msg}, sir.")
            return True
        if "type " in cmd or "write " in cmd:
            text = cmd.replace("type ", "").replace("write ", "").strip()
            ok, msg = ExtraFeatures.type_text(text)
            a._respond(msg)
            return True

        # ---- Camera ----
        if "webcam" in cmd or "open camera" in cmd:
            a._respond("Opening webcam. Press Q to close, sir.")
            threading.Thread(target=CameraModule.open_webcam, daemon=True).start()
            return True
        if "take photo" in cmd or "take picture" in cmd:
            ok, msg = CameraModule.take_photo()
            a._respond(msg)
            return True
        if "face detection" in cmd or "detect face" in cmd:
            a._respond("Starting face detection, sir.")
            threading.Thread(target=CameraModule.face_detection, daemon=True).start()
            return True
        if "read text" in cmd or "ocr" in cmd or "scan text" in cmd:
            a._respond("Scanning text from camera, please hold it steady, sir.")
            ok, msg = CameraModule.read_text_from_camera()
            a._respond(msg)
            return True

        # ---- Ask / AI fallback ----
        if cmd.startswith("ask ") or "question" in cmd:
            q = cmd.replace("ask", "").replace("question", "").strip()
            if q:
                a._respond(AIChat.ask(q))
                return True

        # Natural questions -> AI
        if any(cmd.startswith(w) for w in ("what ", "who ", "why ", "how ", "when ", "where ", "explain ", "define ")):
            a._respond(AIChat.ask(cmd))
            return True

        # Fallback to AI for any unrecognized command
        a._respond(AIChat.ask(cmd))
        return True
