"""
Voice Module — Listen to microphone and convert to text
"""

import threading
import queue


class VoiceListener:
    def __init__(self, callback):
        """
        callback: function to call when voice is recognized
        """
        self.callback = callback
        self.listening = False
        self.result_queue = queue.Queue()

    def start_listening(self):
        """Start voice recognition in background thread"""
        self.listening = True
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()

    def stop_listening(self):
        self.listening = False

    def _listen_loop(self):
        """Continuously listen for voice commands"""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            mic = sr.Microphone()

            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.listening:
                try:
                    with mic as source:
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio)
                    if text and self.callback:
                        self.callback(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"Voice error: {e}")
                    continue
        except ImportError:
            print("SpeechRecognition not installed. Run: pip install SpeechRecognition")

    def listen_once(self) -> str:
        """Listen for one command and return it"""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
            return recognizer.recognize_google(audio)
        except ImportError:
            return "ERROR: SpeechRecognition not installed"
        except Exception as e:
            return f"ERROR: {str(e)}"
