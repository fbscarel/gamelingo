"""Text-to-speech functionality for language learning using Google TTS."""

import threading
import tempfile
import os
import time
from pathlib import Path
from typing import Optional
from gtts import gTTS
from playsound3 import playsound


class TTSEngine:
    """Handles text-to-speech using Google TTS for language learning."""

    def __init__(self, language: str = "it"):
        """Initialize Google TTS engine.

        Args:
            language: Language code for TTS (e.g., 'it', 'en', 'es').
        """
        self.language = language
        self.is_speaking = False
        self.temp_dir = Path(tempfile.gettempdir()) / "gamelingo_tts"
        self.temp_dir.mkdir(exist_ok=True)
        self._available = True
        self._stop_requested = False

    def speak(self, text: str, blocking: bool = False):
        """Speak the given text using Google TTS.

        Args:
            text: Text to speak.
            blocking: If True, waits for speech to complete. If False, speaks in background.
        """
        if not self._available or not text or not text.strip():
            return

        if self.is_speaking:
            # Stop current speech
            self.stop()
            time.sleep(0.2)  # Give it time to stop

        def _speak():
            temp_file = None
            try:
                self.is_speaking = True
                self._stop_requested = False

                # Generate speech using Google TTS
                tts = gTTS(text=text, lang=self.language, slow=False)

                # Save to temporary file
                temp_file = self.temp_dir / f"tts_{os.getpid()}_{int(time.time())}.mp3"
                tts.save(str(temp_file))

                # Play audio (blocks until complete)
                if not self._stop_requested:
                    playsound(str(temp_file), block=True)

            except Exception as e:
                print(f"TTS error: {e}")
            finally:
                # Clean up
                if temp_file and temp_file.exists():
                    try:
                        time.sleep(0.1)  # Small delay before cleanup
                        temp_file.unlink()
                    except Exception as e:
                        print(f"TTS cleanup error: {e}")
                self.is_speaking = False

        if blocking:
            _speak()
        else:
            # Speak in background thread
            thread = threading.Thread(target=_speak, daemon=True)
            thread.start()

    def stop(self):
        """Stop current speech."""
        self._stop_requested = True
        self.is_speaking = False

    def set_language(self, language: str):
        """Change TTS language.

        Args:
            language: New language code (e.g., 'it', 'en', 'es').
        """
        self.language = language

    def is_available(self) -> bool:
        """Check if TTS is available.

        Returns:
            True if Google TTS is available (requires internet).
        """
        return self._available

    def cleanup(self):
        """Clean up resources."""
        self.stop()
        # Clean up any leftover temp files
        try:
            for file in self.temp_dir.glob("tts_*.mp3"):
                try:
                    file.unlink()
                except:
                    pass
        except:
            pass
