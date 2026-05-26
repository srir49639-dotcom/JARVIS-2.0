# ============================================================
# JARVIS - Futuristic GUI Dashboard (Pure Python / CustomTkinter)
# ============================================================

import threading
import time
import math
import tkinter as tk
from datetime import datetime

import customtkinter as ctk

import config
from modules.system_controls import SystemControls


class JarvisDashboard(ctk.CTk):
    """Pure Python dark-themed JARVIS control dashboard with animations."""

    def __init__(self, assistant_ref=None):
        super().__init__()

        self.assistant = assistant_ref
        self._running = False
        self._command_history = []

        # Dark Iron-Man Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(f"{config.ASSISTANT_NAME} HUD")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        # Make the window frameless and slightly transparent for that "HUD" feel
        # Uncomment below lines if you want a true borderless widget
        # self.overrideredirect(True) 
        self.attributes("-alpha", 0.95)

        # Variables for animation
        self.angle_outer = 0
        self.angle_inner = 0
        self.core_pulse = 1.0
        self.pulse_dir = -0.05
        
        self._build_ui()
        self._start_stats_updater()
        self._animate_core()

    def _build_ui(self):
        """Build dashboard layout."""
        # Main layout grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # ---- Header ----
        header = ctk.CTkFrame(self, fg_color="#0a0a1a", corner_radius=0, height=60)
        header.grid(row=0, column=0, columnspan=3, sticky="ew")
        
        ctk.CTkLabel(
            header,
            text=f"// {config.ASSISTANT_NAME} SYSTEM CORE //",
            font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
            text_color="#00f3ff",
        ).pack(side="left", padx=30, pady=15)

        self.status_label = ctk.CTkLabel(
            header,
            text="● SYSTEM STANDBY",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color="#888888",
        )
        self.status_label.pack(side="right", padx=30, pady=15)

        # ---- Left Panel: System Stats ----
        left = ctk.CTkFrame(self, fg_color="#0d1117", corner_radius=15, border_width=1, border_color="#00f3ff")
        left.grid(row=1, column=0, padx=(20, 10), pady=20, sticky="nsew")
        
        ctk.CTkLabel(left, text="SYSTEM DIAGNOSTICS", font=ctk.CTkFont(family="Consolas", size=16, weight="bold"), text_color="#00f3ff").pack(pady=(20, 10))

        self.cpu_bar = self._create_stat_widget(left, "CPU USAGE")
        self.ram_bar = self._create_stat_widget(left, "RAM USAGE")
        self.battery_bar = self._create_stat_widget(left, "POWER LEVEL")
        
        self.time_label = ctk.CTkLabel(
            left,
            text="00:00:00",
            font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
            text_color="#00f3ff",
        )
        self.time_label.pack(pady=40)
        
        # Controls
        self.start_btn = ctk.CTkButton(
            left,
            text="INITIALIZE CORE",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            fg_color="#004466",
            hover_color="#00f3ff",
            text_color="#ffffff",
            height=45,
            command=self._toggle_assistant,
        )
        self.start_btn.pack(pady=10, padx=20, fill="x")

    def _create_stat_widget(self, parent, label):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=15)
        
        lbl = ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(family="Consolas", size=12), text_color="#8ab4f8")
        lbl.pack(anchor="w")
        
        val_lbl = ctk.CTkLabel(frame, text="0%", font=ctk.CTkFont(family="Consolas", size=14, weight="bold"), text_color="#ffffff")
        val_lbl.pack(side="right")
        
        bar = ctk.CTkProgressBar(frame, height=8, progress_color="#00f3ff", fg_color="#1a1a2e")
        bar.pack(fill="x", pady=5)
        bar.set(0)
        
        # Attach value label to bar object for easy updating
        bar.val_lbl = val_lbl 
        return bar

        # ---- Center Panel: AI Core Animation ----
    def _build_ui_continue(self):
        center = ctk.CTkFrame(self, fg_color="#05050a", corner_radius=15, border_width=1, border_color="#00f3ff")
        center.grid(row=1, column=1, padx=10, pady=20, sticky="nsew")
        
        self.canvas = tk.Canvas(center, bg="#05050a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ---- Right Panel: Comms Log ----
        right = ctk.CTkFrame(self, fg_color="#0d1117", corner_radius=15, border_width=1, border_color="#00f3ff")
        right.grid(row=1, column=2, padx=(10, 20), pady=20, sticky="nsew")
        
        ctk.CTkLabel(right, text="COMMUNICATIONS LINK", font=ctk.CTkFont(family="Consolas", size=16, weight="bold"), text_color="#00f3ff").pack(pady=(20, 10))
        
        self.history_box = ctk.CTkTextbox(
            right,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#05050a",
            text_color="#00ff88",
            wrap="word",
        )
        self.history_box.pack(fill="both", expand=True, padx=20, pady=10)
        
        input_frame = ctk.CTkFrame(right, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=20)
        
        self.cmd_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter override command...",
            font=ctk.CTkFont(family="Consolas", size=12),
            height=40,
            fg_color="#05050a",
            border_color="#00f3ff"
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.cmd_entry.bind("<Return>", self._on_manual_command)
        
        ctk.CTkButton(
            input_frame,
            text="EXECUTE",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            width=80,
            height=40,
            fg_color="#004466",
            hover_color="#00f3ff",
            command=self._on_manual_command,
        ).pack(side="right")
        
        # Auto-start logic
        self.after(1000, self._auto_start)

    def _draw_arc(self, cx, cy, radius, start, extent, width, color, dash=None):
        self.canvas.create_arc(
            cx - radius, cy - radius, cx + radius, cy + radius,
            start=start, extent=extent, style=tk.ARC, width=width, outline=color, dash=dash
        )

    def _animate_core(self):
        """Draw and animate the HUD AI Core using tkinter Canvas."""
        if not hasattr(self, 'canvas'):
            self.after(50, self._animate_core)
            return
            
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w > 1 and h > 1:
            cx, cy = w / 2, h / 2
            
            # Determine color based on state
            core_color = "#00ff88" if self._running else "#00f3ff"
            glow_color = "#005533" if self._running else "#004466"
            
            # Update angles
            speed_mult = 3 if self._running else 1
            self.angle_outer = (self.angle_outer + (2 * speed_mult)) % 360
            self.angle_inner = (self.angle_inner - (3 * speed_mult)) % 360
            
            # Pulsing logic
            self.core_pulse += (self.pulse_dir * speed_mult)
            if self.core_pulse > 1.2:
                self.pulse_dir = -0.05
            elif self.core_pulse < 0.8:
                self.pulse_dir = 0.05
                
            # Draw outer dashed ring
            self._draw_arc(cx, cy, 140, self.angle_outer, 90, 4, core_color, dash=(10, 5))
            self._draw_arc(cx, cy, 140, self.angle_outer + 180, 90, 4, core_color, dash=(10, 5))
            
            # Draw inner solid segments
            self._draw_arc(cx, cy, 110, self.angle_inner, 120, 6, core_color)
            self._draw_arc(cx, cy, 110, self.angle_inner + 180, 120, 6, core_color)
            
            # Draw central pulsing core
            core_radius = 50 * self.core_pulse
            self.canvas.create_oval(
                cx - core_radius, cy - core_radius, cx + core_radius, cy + core_radius,
                fill=glow_color, outline=core_color, width=3
            )
            
            # Draw some tech accents
            self.canvas.create_text(cx, cy, text="CORE", fill="#ffffff", font=("Consolas", 12, "bold"))
            
        self.after(50, self._animate_core)

    def _toggle_assistant(self):
        """Start or stop the assistant."""
        if self.assistant is None:
            return
        if self._running:
            self.assistant.stop_listening()
            self._running = False
            self.start_btn.configure(text="INITIALIZE CORE", fg_color="#004466")
            self.set_status("SYSTEM STANDBY", "#888888")
        else:
            self.assistant.start()
            self._running = True
            self.start_btn.configure(text="TERMINATE CORE", fg_color="#ff3366")
            self.set_status("LISTENING...", "#00ff88")

    def _on_manual_command(self, event=None):
        """Process manual text command."""
        cmd = self.cmd_entry.get().strip()
        if cmd and self.assistant:
            self.cmd_entry.delete(0, tk.END)
            self.add_history(f"Override> {cmd}", "user")
            threading.Thread(
                target=self.assistant.process_command,
                args=(cmd,),
                daemon=True,
            ).start()

    def add_history(self, text, source="system"):
        """Add entry to command history."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {text}\n"
        self.history_box.insert("end", entry)
        self.history_box.see("end")

    def set_status(self, status, color="#00f3ff"):
        self.status_label.configure(text=f"● {status}", text_color=color)

    def _auto_start(self):
        if self.assistant and not self._running:
            self._toggle_assistant()

    def set_mic_status(self, available):
        if not available:
            self.add_history("WARNING: Audio input unavailable.", "system")

    def set_listen_mode(self, active):
        if active:
            self.set_status("ACTIVE...", "#00ff88")
        else:
            if self._running:
                self.set_status("LISTENING...", "#00ff88")
            else:
                self.set_status("SYSTEM STANDBY", "#888888")

    def _start_stats_updater(self):
        """Background thread to update system stats."""
        def update():
            while True:
                try:
                    stats = SystemControls.get_system_stats()
                    cpu = stats.get("cpu", 0)
                    ram = stats.get("ram", 0)
                    battery = stats.get("battery")
                    plugged = stats.get("battery_plugged", True)

                    self.cpu_bar.set(cpu / 100)
                    self.cpu_bar.val_lbl.configure(text=f"{cpu:.0f}%")
                    
                    self.ram_bar.set(ram / 100)
                    self.ram_bar.val_lbl.configure(text=f"{ram:.0f}%")

                    if battery is not None:
                        self.battery_bar.set(battery / 100)
                        p_icon = "⚡" if plugged else "🔋"
                        self.battery_bar.val_lbl.configure(text=f"{p_icon} {battery:.0f}%")

                    self.time_label.configure(
                        text=datetime.now().strftime("%H:%M:%S")
                    )
                except Exception:
                    pass
                time.sleep(1)

        threading.Thread(target=update, daemon=True).start()

    def on_assistant_response(self, response):
        """Callback when assistant responds."""
        self.add_history(f"JARVIS> {response}", "system")

    def _init_delayed(self):
        self._build_ui_continue()

    # Override the constructor to call the second half of UI build
    def __init__(self, assistant_ref=None):
        super().__init__()
        self.assistant = assistant_ref
        self._running = False
        self._command_history = []
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title(f"{config.ASSISTANT_NAME} HUD")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.attributes("-alpha", 0.95)
        self.angle_outer = 0
        self.angle_inner = 0
        self.core_pulse = 1.0
        self.pulse_dir = -0.05
        self._build_ui()
        self._build_ui_continue()
        self._start_stats_updater()
        self._animate_core()
