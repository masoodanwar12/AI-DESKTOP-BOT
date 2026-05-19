"""
AI Desktop Bot - Main UI
Modern dark themed Tkinter interface
UPDATED v3.0 — Added: youtube play button, claude, chatgpt quick buttons
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import time
import os
import sys
from datetime import datetime

# ─────────────────────────────────────────────
# COLORS & FONTS
# ─────────────────────────────────────────────
BG_DARK      = "#0a0a0f"
BG_CARD      = "#12121a"
BG_INPUT     = "#1a1a2e"
ACCENT       = "#6c63ff"
ACCENT_GLOW  = "#8b85ff"
GREEN        = "#00ff9f"
RED          = "#ff4757"
YELLOW       = "#ffd32a"
TEXT_PRIMARY = "#e8e8ff"
TEXT_DIM     = "#6b6b8a"
BORDER       = "#2a2a3e"

FONT_TITLE   = ("Courier New", 22, "bold")
FONT_MONO    = ("Courier New", 11)
FONT_SMALL   = ("Courier New", 9)
FONT_BTN     = ("Courier New", 10, "bold")


class DesktopBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 AI Desktop Bot v3.0")
        self.root.geometry("950x780")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        self.bot = None
        self.voice = None
        self.is_voice_on = False
        self.is_processing = False

        self._build_ui()
        self._show_welcome()

    # ─────────────────────────────────────────
    # BUILD UI
    # ─────────────────────────────────────────

    def _build_ui(self):
        # ── TOP BAR ──
        top = tk.Frame(self.root, bg=BG_DARK, pady=10)
        top.pack(fill="x", padx=20)

        tk.Label(top, text="⬡", font=("Courier New", 28, "bold"),
                 bg=BG_DARK, fg=ACCENT).pack(side="left")

        tk.Label(top, text=" AI DESKTOP BOT", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left", padx=5)

        tk.Label(top, text="v3.0", font=FONT_SMALL,
                 bg=BG_DARK, fg=TEXT_DIM).pack(side="left")

        # Status dot
        self.status_dot = tk.Label(top, text="●", font=("Courier New", 16),
                                   bg=BG_DARK, fg=RED)
        self.status_dot.pack(side="right", padx=5)

        self.status_label = tk.Label(top, text="OFFLINE", font=FONT_SMALL,
                                     bg=BG_DARK, fg=RED)
        self.status_label.pack(side="right")

        # ── SEPARATOR ──
        tk.Frame(self.root, bg=ACCENT, height=1).pack(fill="x", padx=20)

        # ── MAIN BODY ──
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # LEFT — Chat log
        left = tk.Frame(body, bg=BG_DARK)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="[ COMMAND LOG ]", font=FONT_SMALL,
                 bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w")

        self.chat_log = scrolledtext.ScrolledText(
            left,
            bg=BG_CARD, fg=TEXT_PRIMARY,
            font=FONT_MONO,
            wrap=tk.WORD,
            relief="flat",
            borderwidth=0,
            state="disabled",
            padx=10, pady=10,
        )
        self.chat_log.pack(fill="both", expand=True)

        # Tag colors for chat
        self.chat_log.tag_config("user",   foreground=ACCENT_GLOW)
        self.chat_log.tag_config("bot",    foreground=GREEN)
        self.chat_log.tag_config("system", foreground=YELLOW)
        self.chat_log.tag_config("error",  foreground=RED)
        self.chat_log.tag_config("dim",    foreground=TEXT_DIM)
        self.chat_log.tag_config("action", foreground="#ff9f43")

        # RIGHT — Controls
        right = tk.Frame(body, bg=BG_DARK, width=220)
        right.pack(side="right", fill="y", padx=(15, 0))
        right.pack_propagate(False)

        # ── API Key ──
        self._make_section(right, "[ API KEY ]")
        self.api_entry = tk.Entry(
            right, bg=BG_INPUT, fg=TEXT_PRIMARY,
            font=FONT_MONO, relief="flat",
            insertbackground=ACCENT, show="*",
            borderwidth=5
        )
        self.api_entry.pack(fill="x", pady=(0, 5))
        self._make_btn(right, "⚡ CONNECT", self._connect, ACCENT)

        # ── Voice ──
        self._make_section(right, "[ VOICE ]")
        self.voice_btn = self._make_btn(right, "🎤 START VOICE", self._toggle_voice, TEXT_DIM)

        # ── Quick Commands ──
        self._make_section(right, "[ QUICK COMMANDS ]")

        # ✅ UPDATED quick commands — added play, claude, chatgpt
        quick_cmds = [
            ("🌐 Open Chrome",     "open chrome"),
            ("📺 YouTube",         "open youtube"),
            ("▶️ Play Lofi Music", "play lofi music"),        # ← NEW
            ("🔍 Google Search",   "search google"),
            ("🤖 Open Claude",     "open claude"),            # ← NEW
            ("💬 Open ChatGPT",    "open chatgpt"),           # ← NEW
            ("📸 Screenshot",      "take a screenshot"),
            ("💻 System Info",     "show system info"),
            ("🔊 Volume Up",       "volume up"),
            ("🔇 Volume Down",     "volume down"),
            ("📁 Downloads",       "open downloads folder"),  # ← NEW
            ("🖥️ Desktop",        "open desktop folder"),    # ← NEW
            ("📋 Copy",            "press ctrl c"),
            ("📌 Paste",           "press ctrl v"),
        ]

        for label, cmd in quick_cmds:
            btn = tk.Button(
                right, text=label,
                bg=BG_CARD, fg=TEXT_PRIMARY,
                font=FONT_SMALL, relief="flat",
                activebackground=BG_INPUT,
                activeforeground=ACCENT,
                cursor="hand2",
                command=lambda c=cmd: self._quick_cmd(c),
                pady=3,
            )
            btn.pack(fill="x", pady=1)

        # ── System Info ──
        self._make_section(right, "[ SYSTEM ]")
        self.sys_label = tk.Label(
            right, text="CPU: --  RAM: --",
            font=FONT_SMALL, bg=BG_DARK,
            fg=TEXT_DIM, justify="left"
        )
        self.sys_label.pack(anchor="w")
        self._update_sys_info()

        # ── INPUT BAR ──
        bottom = tk.Frame(self.root, bg=BG_DARK, pady=10)
        bottom.pack(fill="x", padx=20)

        tk.Label(bottom, text="▶", font=FONT_MONO,
                 bg=BG_DARK, fg=ACCENT).pack(side="left", padx=(0, 5))

        self.cmd_entry = tk.Entry(
            bottom, bg=BG_INPUT, fg=TEXT_PRIMARY,
            font=FONT_MONO, relief="flat",
            insertbackground=ACCENT,
            borderwidth=8,
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True)
        self.cmd_entry.bind("<Return>", self._send_command)
        self.cmd_entry.bind("<Up>", self._history_up)

        self._make_btn(bottom, "SEND ▶", self._send_command, ACCENT, side="right")

        # Command history
        self.cmd_history = []
        self.history_idx = -1

        # ── STATUS BAR ──
        bar = tk.Frame(self.root, bg=BG_CARD, pady=4)
        bar.pack(fill="x")
        self.bottom_status = tk.Label(
            bar, text="Connect your Groq API key to start",
            font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM
        )
        self.bottom_status.pack(side="left", padx=10)

        self.clock_label = tk.Label(bar, font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM)
        self.clock_label.pack(side="right", padx=10)
        self._update_clock()

    def _make_section(self, parent, text):
        tk.Label(parent, text=text, font=FONT_SMALL,
                 bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w", pady=(10, 2))

    def _make_btn(self, parent, text, cmd, color, side=None):
        btn = tk.Button(
            parent, text=text,
            bg=color, fg=BG_DARK if color != TEXT_DIM else TEXT_PRIMARY,
            font=FONT_BTN, relief="flat",
            activebackground=ACCENT_GLOW,
            cursor="hand2",
            command=cmd,
            pady=5,
        )
        if side:
            btn.pack(side=side, padx=(10, 0))
        else:
            btn.pack(fill="x", pady=2)
        return btn

    # ─────────────────────────────────────────
    # CHAT LOG
    # ─────────────────────────────────────────

    def _log(self, text, tag="bot"):
        self.chat_log.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_log.insert("end", f"[{timestamp}] ", "dim")
        self.chat_log.insert("end", text + "\n", tag)
        self.chat_log.configure(state="disabled")
        self.chat_log.see("end")

    def _show_welcome(self):
        self._log("╔══════════════════════════════════════╗", "system")
        self._log("║      AI DESKTOP BOT  v3.0            ║", "system")
        self._log("║  Voice + Text  |  Full System Control ║", "system")
        self._log("╚══════════════════════════════════════╝", "system")
        self._log("✅ NEW: YouTube Auto-Play added!", "system")
        self._log("✅ NEW: Claude & ChatGPT quick buttons!", "system")
        self._log("✅ NEW: Open folders & files!", "system")
        self._log("─" * 42, "dim")
        self._log("Enter your Groq API key and click CONNECT", "dim")
        self._log("Then type or speak any command!", "dim")

    # ─────────────────────────────────────────
    # CONNECT TO GROQ
    # ─────────────────────────────────────────

    def _connect(self):
        api_key = self.api_entry.get().strip()
        if not api_key:
            self._log("❌ Please enter your Groq API key!", "error")
            return

        self._log("⚡ Connecting to Groq AI...", "system")
        self.bottom_status.config(text="Connecting...")

        def do_connect():
            try:
                from bot_brain import BotBrain
                self.bot = BotBrain(api_key)
                result = self.bot.execute("say hello")
                self.root.after(0, self._on_connected, result)
            except Exception as e:
                self.root.after(0, self._on_connect_error, str(e))

        threading.Thread(target=do_connect, daemon=True).start()

    def _on_connected(self, result):
        self.status_dot.config(fg=GREEN)
        self.status_label.config(fg=GREEN, text="ONLINE")
        self.bottom_status.config(text="✅ Connected to Groq AI — Ready!")
        self._log("✅ Connected to Groq AI!", "system")
        self._log(f"🤖 Bot: {result.get('output', 'Hello! Ready to help.')}", "bot")
        self.cmd_entry.focus()

    def _on_connect_error(self, error):
        self._log(f"❌ Connection failed: {error}", "error")
        self.bottom_status.config(text="Connection failed")

    # ─────────────────────────────────────────
    # SEND COMMAND
    # ─────────────────────────────────────────

    def _send_command(self, event=None):
        if not self.bot:
            self._log("❌ Connect first! Enter API key and click CONNECT", "error")
            return
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        self.cmd_entry.delete(0, "end")
        self.cmd_history.append(cmd)
        self.history_idx = -1
        self._process_command(cmd)

    def _quick_cmd(self, cmd):
        if not self.bot:
            self._log("❌ Connect first!", "error")
            return
        self._process_command(cmd)

    def _process_command(self, cmd):
        if self.is_processing:
            self._log("⏳ Still processing previous command...", "dim")
            return
        self.is_processing = True
        self._log(f"👤 You: {cmd}", "user")
        self.bottom_status.config(text="🔄 Processing...")

        def run():
            try:
                result = self.bot.execute(cmd)
                self.root.after(0, self._show_result, result)
            except Exception as e:
                self.root.after(0, self._show_error, str(e))

        threading.Thread(target=run, daemon=True).start()

    def _show_result(self, result):
        message = result.get("message", "")
        output = result.get("output", "")
        self._log(f"⚡ Action: {message}", "action")
        self._log(f"🤖 Bot: {output}", "bot")
        self.bottom_status.config(text=f"✅ Done: {message}")
        self.is_processing = False

    def _show_error(self, error):
        self._log(f"❌ Error: {error}", "error")
        self.bottom_status.config(text="❌ Error occurred")
        self.is_processing = False

    # ─────────────────────────────────────────
    # VOICE
    # ─────────────────────────────────────────

    def _toggle_voice(self):
        if not self.bot:
            self._log("❌ Connect first!", "error")
            return
        if not self.is_voice_on:
            self._start_voice()
        else:
            self._stop_voice()

    def _start_voice(self):
        try:
            from voice_module import VoiceListener
            self.voice = VoiceListener(callback=self._on_voice_command)
            self.voice.start_listening()
            self.is_voice_on = True
            self.voice_btn.config(text="🔴 STOP VOICE", bg=RED)
            self._log("🎤 Voice activated! Speak your command...", "system")
        except Exception as e:
            self._log(f"❌ Voice error: {e}", "error")

    def _stop_voice(self):
        if self.voice:
            self.voice.stop_listening()
        self.is_voice_on = False
        self.voice_btn.config(text="🎤 START VOICE", bg=TEXT_DIM)
        self._log("🎤 Voice deactivated", "system")

    def _on_voice_command(self, text):
        self._log(f"🎤 Voice: {text}", "user")
        self.root.after(0, self._process_command, text)

    # ─────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────

    def _history_up(self, event):
        if self.cmd_history:
            self.history_idx = max(0, len(self.cmd_history) - 1)
            self.cmd_entry.delete(0, "end")
            self.cmd_entry.insert(0, self.cmd_history[self.history_idx])

    def _update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self._update_clock)

    def _update_sys_info(self):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.sys_label.config(text=f"CPU: {cpu:.0f}%  RAM: {ram:.0f}%")
        except:
            pass
        self.root.after(3000, self._update_sys_info)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.update_idletasks()
    w, h = 950, 780
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    app = DesktopBotUI(root)
    root.mainloop()
