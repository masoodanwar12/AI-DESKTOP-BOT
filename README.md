# 🤖 AI Desktop Bot

Full system control through voice or text commands — powered by Groq AI + LangChain.

---

## 📦 Installation

### Step 1 — Install Python packages
```bash
pip install -r requirements.txt
```

### Step 2 — For Voice (Windows only extra step)
```bash
pip install pipwin
pipwin install pyaudio
```

### Step 3 — Get Free Groq API Key
1. Go to https://console.groq.com
2. Sign up free
3. Go to API Keys → Create new key
4. Copy the key

### Step 4 — Run the app
```bash
python main.py
```

---

## 🎮 How to Use

1. Paste your Groq API key in the box
2. Click **CONNECT**
3. Type or speak any command!

---

## 💬 Example Commands

### Open Apps
```
open chrome
open notepad
open calculator
open spotify
open vscode
```

### Browser & Web
```
open youtube
search python tutorials on google
open https://github.com
search cricket scores
```

### System Control
```
take a screenshot
show system info
volume up
volume down
mute volume
scroll down
press ctrl c
press ctrl v
press alt tab
```

### Posting / Social Media
```
open twitter to post
open linkedin
open facebook
```

### YouTube
```
search lofi music on youtube
find python tutorial on youtube
```

### Fun
```
how are you
what can you do
tell me a joke
```

---

## 🗂️ Project Structure

```
ai_desktop_bot/
├── main.py          ← UI (run this!)
├── bot_brain.py     ← AI command processor
├── voice_module.py  ← Voice recognition
├── requirements.txt ← Install these
└── README.md        ← This file
```

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|---------|
| LangChain + Groq | AI brain (understand commands) |
| PyAutoGUI | Control mouse, keyboard, screenshot |
| SpeechRecognition | Voice to text |
| psutil | System info (CPU, RAM, battery) |
| Tkinter | Desktop UI |
| webbrowser | Open URLs and Chrome |

---

## ❗ Troubleshooting

**Voice not working?**
```bash
pip install pipwin
pipwin install pyaudio
```

**Chrome not opening?**
- Make sure Chrome is installed
- Try: `open https://google.com` instead

**API key error?**
- Get free key from https://console.groq.com
- Make sure no spaces when pasting

---

Built with ❤️ using Python + LangChain + Groq
