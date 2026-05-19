"""
AI Desktop Bot - Brain (Command Processor)
Uses Groq AI to understand and execute system commands
UPDATED v3.0 — Added: youtube_play, open_file, open_folder, open_in_browser, chrome fix
"""

import os
import sys
import time
import json
import subprocess
import webbrowser
import pyautogui
import psutil
import platform
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """
You are an AI Desktop Automation Bot. You control a Windows computer.
When the user gives a command, respond ONLY with a JSON object like this:

{
  "action": "action_name",
  "params": { ... },
  "message": "what you are doing"
}

Available actions:

1. open_app
   {"action": "open_app", "params": {"app": "chrome"}, "message": "Opening Chrome"}
   Apps: chrome, notepad, calculator, explorer, cmd, spotify, vscode, whatsapp, word, excel, powerpoint, vlc, paint, opera, zoom, teams, telegram

2. open_url
   {"action": "open_url", "params": {"url": "https://youtube.com"}, "message": "Opening YouTube"}

3. open_chrome_url
   {"action": "open_chrome_url", "params": {"url": "https://youtube.com"}, "message": "Opening YouTube in Chrome"}
   Use when user says open something IN chrome — opens without profile picker

4. search_web
   {"action": "search_web", "params": {"query": "python tutorials"}, "message": "Searching google"}

5. youtube_search
   {"action": "youtube_search", "params": {"query": "lofi music"}, "message": "Searching YouTube"}
   Use when user says SEARCH something on youtube — just opens search results

6. youtube_play
   {"action": "youtube_play", "params": {"query": "lofi music"}, "message": "Playing lofi music on YouTube"}
   Use when user says PLAY something — opens YouTube and auto clicks first video
   Examples: "play lofi", "play shape of you", "play cricket highlights", "play arijit singh"

7. open_in_browser
   {"action": "open_in_browser", "params": {"site": "claude"}, "message": "Opening Claude AI"}
   Sites: claude, chatgpt, gemini, youtube, github, google, facebook, instagram, twitter, linkedin, whatsapp, netflix, spotify, gmail, drive

8. open_file
   {"action": "open_file", "params": {"path": "C:\\Users\\file.py", "app": "vscode"}, "message": "Opening file"}
   Apps for open_file: vscode, notepad, chrome, default

9. open_folder
   {"action": "open_folder", "params": {"path": "C:\\"}, "message": "Opening C drive"}
   Common paths:
   C drive = C:\\
   D drive = D:\\
   Downloads = C:\\Users\\{username}\\Downloads
   Documents = C:\\Users\\{username}\\Documents
   Desktop = C:\\Users\\{username}\\Desktop
   Pictures = C:\\Users\\{username}\\Pictures
   Always use double backslash in paths

10. type_text
    {"action": "type_text", "params": {"text": "Hello World"}, "message": "Typing text"}

11. screenshot
    {"action": "screenshot", "params": {"filename": "screen.png"}, "message": "Taking screenshot"}

12. volume
    {"action": "volume", "params": {"level": "up"}, "message": "Volume up"}
    Levels: up, down, mute

13. scroll
    {"action": "scroll", "params": {"direction": "down", "amount": 3}, "message": "Scrolling"}

14. click
    {"action": "click", "params": {"button": "left"}, "message": "Clicking"}

15. hotkey
    {"action": "hotkey", "params": {"keys": ["ctrl", "c"]}, "message": "Copying"}

16. post_to_browser
    {"action": "post_to_browser", "params": {"platform": "twitter"}, "message": "Opening Twitter"}
    Platforms: twitter, facebook, linkedin, instagram

17. system_info
    {"action": "system_info", "params": {}, "message": "Getting system info"}

18. close_app
    {"action": "close_app", "params": {"app": "chrome"}, "message": "Closing Chrome"}

19. speak
    {"action": "speak", "params": {"text": "Hello!"}, "message": "Speaking"}

20. create_file
    {"action": "create_file", "params": {"path": "C:\\Users\\test.txt", "content": "Hello!"}, "message": "Creating file"}

21. run_command
    {"action": "run_command", "params": {"cmd": "ipconfig"}, "message": "Running command"}
    Use for CMD commands: ipconfig, ping, dir, etc.

22. chat
    {"action": "chat", "params": {"response": "Hello!"}, "message": "Chatting"}
    Use for greetings or questions that need no system action.

IMPORTANT RULES:
- ONLY respond with valid JSON, nothing else
- No markdown, no explanation, just JSON
- If unsure, use chat action
- For folder navigation build the full path
- When user says C drive → path is C:\\
- When user says downloads → path is C:\\Users\\{username}\\Downloads
- When user says PLAY → use youtube_play (not youtube_search)
- When user says SEARCH on youtube → use youtube_search
"""


class BotBrain:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            groq_api_key=api_key,
        )
        self.history = []
        self.username = os.getenv("USERNAME", "User")

    def understand_command(self, command: str) -> dict:
        context = f"Windows username is: {self.username}\n\nUser command: {command}"
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=context)
        ]
        response = self.llm.invoke(messages)
        text = response.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"action": "chat", "params": {"response": text}, "message": "Responding"}

    def execute(self, command: str) -> dict:
        result = self.understand_command(command)
        action = result.get("action", "chat")
        params = result.get("params", {})
        output = self._run_action(action, params)
        result["output"] = output
        self.history.append({"command": command, "result": result})
        return result

    def _run_action(self, action: str, params: dict) -> str:
        try:

            # ── OPEN APP ──
            if action == "open_app":
                return self._open_app(params.get("app", ""))

            # ── OPEN URL ──
            elif action == "open_url":
                url = params.get("url", "")
                webbrowser.open(url)
                return f"Opened {url}"

            # ── OPEN CHROME WITHOUT PROFILE PICKER ──
            elif action == "open_chrome_url":
                url = params.get("url", "https://google.com")
                os.system(f'start chrome --profile-directory=Default "{url}"')
                return f"Opened Chrome → {url}"

            # ── SEARCH WEB ──
            elif action == "search_web":
                query = params.get("query", "")
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(url)
                return f"Searched: {query}"

            # ── YOUTUBE SEARCH ONLY ──
            elif action == "youtube_search":
                query = params.get("query", "")
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                os.system(f'start chrome --profile-directory=Default "{url}"')
                return f"YouTube search opened: {query}"

            # ── YOUTUBE PLAY — opens + auto clicks first video ──
            elif action == "youtube_play":
                query = params.get("query", "")
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

                # Open Chrome with YouTube search
                os.system(f'start chrome --profile-directory=Default "{url}"')

                # Wait for Chrome and YouTube to fully load
                time.sleep(5)

                # Focus Chrome window
                pyautogui.hotkey("alt", "tab")
                time.sleep(1)

                # Press Tab multiple times to reach first video
                for _ in range(5):
                    pyautogui.press("tab")
                    time.sleep(0.2)

                # Press Enter to play first video
                pyautogui.press("enter")
                time.sleep(1)

                return f"Playing: {query} on YouTube ✅"

            # ── OPEN IN BROWSER ──
            elif action == "open_in_browser":
                sites = {
                    "claude":    "https://claude.ai",
                    "chatgpt":   "https://chat.openai.com",
                    "gemini":    "https://gemini.google.com",
                    "youtube":   "https://youtube.com",
                    "github":    "https://github.com",
                    "google":    "https://google.com",
                    "facebook":  "https://facebook.com",
                    "instagram": "https://instagram.com",
                    "twitter":   "https://twitter.com",
                    "linkedin":  "https://linkedin.com",
                    "whatsapp":  "https://web.whatsapp.com",
                    "netflix":   "https://netflix.com",
                    "spotify":   "https://open.spotify.com",
                    "gmail":     "https://mail.google.com",
                    "drive":     "https://drive.google.com",
                }
                site = params.get("site", "").lower()
                url = sites.get(site, f"https://www.google.com/search?q={site}")
                webbrowser.open(url)
                return f"Opened {site} ✅"

            # ── OPEN FILE ──
            elif action == "open_file":
                filepath = params.get("path", "")
                app = params.get("app", "").lower()
                if not filepath:
                    return "No file path given"
                filepath = filepath.replace("{username}", self.username)
                if app == "vscode":
                    os.system(f'code "{filepath}"')
                    return f"Opened in VSCode: {filepath}"
                elif app == "notepad":
                    os.system(f'notepad "{filepath}"')
                    return f"Opened in Notepad: {filepath}"
                elif app == "chrome":
                    os.system(f'start chrome --profile-directory=Default "{filepath}"')
                    return f"Opened in Chrome: {filepath}"
                else:
                    os.startfile(filepath)
                    return f"Opened: {filepath}"

            # ── OPEN FOLDER ──
            elif action == "open_folder":
                folder = params.get("path", "C:\\")
                folder = folder.replace("{username}", self.username)
                os.system(f'explorer "{folder}"')
                return f"Opened folder: {folder}"

            # ── TYPE TEXT ──
            elif action == "type_text":
                time.sleep(1)
                pyautogui.typewrite(params.get("text", ""), interval=0.05)
                return "Text typed"

            # ── SCREENSHOT ──
            elif action == "screenshot":
                filename = params.get("filename", "screenshot.png")
                pyautogui.screenshot().save(filename)
                return f"Screenshot saved: {filename}"

            # ── VOLUME ──
            elif action == "volume":
                level = params.get("level", "up")
                key_map = {"up": "volumeup", "down": "volumedown", "mute": "volumemute"}
                pyautogui.press(key_map.get(level, "volumeup"))
                return f"Volume {level}"

            # ── SCROLL ──
            elif action == "scroll":
                direction = params.get("direction", "down")
                amount = params.get("amount", 3)
                clicks = amount if direction == "down" else -amount
                pyautogui.scroll(clicks)
                return f"Scrolled {direction}"

            # ── CLICK ──
            elif action == "click":
                button = params.get("button", "left")
                pyautogui.click(button=button)
                return f"Clicked {button}"

            # ── HOTKEY ──
            elif action == "hotkey":
                keys = params.get("keys", [])
                if keys:
                    pyautogui.hotkey(*keys)
                return f"Pressed {'+'.join(keys)}"

            # ── POST TO SOCIAL MEDIA ──
            elif action == "post_to_browser":
                urls = {
                    "twitter":   "https://twitter.com/compose/tweet",
                    "facebook":  "https://facebook.com",
                    "linkedin":  "https://linkedin.com/feed",
                    "instagram": "https://instagram.com",
                }
                url = urls.get(params.get("platform", ""), "https://google.com")
                webbrowser.open(url)
                return f"Opened {params.get('platform')} to post"

            # ── SYSTEM INFO ──
            elif action == "system_info":
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory()
                disk = psutil.disk_usage("C:\\")
                battery = psutil.sensors_battery()
                bat = f"{battery.percent:.0f}%" if battery else "N/A"
                return (
                    f"CPU: {cpu}% | "
                    f"RAM: {ram.percent}% ({ram.used // 1024**3}GB used) | "
                    f"Disk C: {disk.percent}% used | "
                    f"Battery: {bat}"
                )

            # ── CLOSE APP ──
            elif action == "close_app":
                app = params.get("app", "").lower()
                exe_map = {
                    "chrome":      "chrome.exe",
                    "notepad":     "notepad.exe",
                    "calculator":  "calculator.exe",
                    "spotify":     "spotify.exe",
                    "vscode":      "code.exe",
                    "word":        "winword.exe",
                    "excel":       "excel.exe",
                    "vlc":         "vlc.exe",
                }
                exe = exe_map.get(app, app + ".exe")
                killed = False
                for proc in psutil.process_iter(["name"]):
                    if proc.info["name"].lower() == exe.lower():
                        proc.kill()
                        killed = True
                return f"Closed {app} ✅" if killed else f"{app} was not running"

            # ── SPEAK ──
            elif action == "speak":
                text = params.get("text", "").replace("'", "")
                os.system(
                    f'powershell -Command "Add-Type -AssemblyName System.Speech; '
                    f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"'
                )
                return f"Spoke: {text}"

            # ── CREATE FILE ──
            elif action == "create_file":
                filepath = params.get("path", "")
                content = params.get("content", "")
                filepath = filepath.replace("{username}", self.username)
                with open(filepath, "w") as f:
                    f.write(content)
                return f"Created: {filepath}"

            # ── RUN CMD COMMAND ──
            elif action == "run_command":
                cmd = params.get("cmd", "")
                result = subprocess.run(
                    cmd, shell=True,
                    capture_output=True, text=True, timeout=10
                )
                output = result.stdout or result.stderr or "Done"
                return output[:500]

            # ── CHAT ──
            elif action == "chat":
                return params.get("response", "I'm here to help!")

            else:
                return f"Unknown action: {action}"

        except Exception as e:
            return f"Error: {str(e)}"

    def _open_app(self, app: str) -> str:
        """Open applications"""
        app = app.lower()
        commands = {
            "chrome":      'start chrome --profile-directory=Default',
            "notepad":     "notepad",
            "calculator":  "calc",
            "explorer":    "explorer",
            "cmd":         "start cmd",
            "spotify":     "start spotify",
            "vscode":      "code .",
            "whatsapp":    "start whatsapp",
            "word":        "start winword",
            "excel":       "start excel",
            "powerpoint":  "start powerpnt",
            "vlc":         "start vlc",
            "paint":       "mspaint",
            "opera":       "start opera",
            "zoom":        "start zoom",
            "teams":       "start teams",
            "telegram":    "start telegram",
        }
        cmd = commands.get(app)
        if cmd:
            os.system(cmd)
            return f"Opened {app} ✅"
        else:
            os.system(f"start {app}")
            return f"Tried to open {app}"
