"""Global hotkey and gamepad input handling."""

import threading
import time
from typing import Optional, Callable
from pynput import keyboard
from .gamepad import GamepadManager


class HotkeyManager:
    """Manages global keyboard and gamepad hotkeys."""

    def __init__(
        self,
        translate_callback: Callable,
        tts_callback: Callable,
        translate_key: str = "<65>",  # Keypad 0
        tts_key: str = "<110>",  # Keypad .
        translate_gamepad: int = 0,  # Button 0 (A/Cross)
        tts_gamepad: int = 1  # Button 1 (B/Circle)
    ):
        """Initialize hotkey manager.

        Args:
            translate_callback: Function to call when translate hotkey is pressed.
            tts_callback: Function to call when TTS hotkey is pressed.
            translate_key: Key code for translation (format: "<keycode>")
            tts_key: Key code for TTS (format: "<keycode>")
            translate_gamepad: Gamepad button index for translation
            tts_gamepad: Gamepad button index for TTS
        """
        self.translate_callback = translate_callback
        self.tts_callback = tts_callback
        self.translate_key = translate_key
        self.tts_key = tts_key

        self.running = False
        self.keyboard_listener: Optional[keyboard.Listener] = None

        # Initialize gamepad manager
        self.gamepad_manager = GamepadManager(
            translate_callback=translate_callback,
            tts_callback=tts_callback,
            translate_button=translate_gamepad,
            tts_button=tts_gamepad
        )

        # Track button states to prevent repeats
        self.last_translate_time = 0
        self.last_tts_time = 0
        self.debounce_time = 0.3  # 300ms debounce

    def start(self):
        """Start listening for hotkeys."""
        if self.running:
            return

        self.running = True

        # Start keyboard listener (global, works even when window not focused)
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            suppress=False  # Don't suppress keys, let them pass through
        )
        self.keyboard_listener.start()

        # Start gamepad manager
        self.gamepad_manager.start()

    def stop(self):
        """Stop listening for hotkeys."""
        self.running = False

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

        # Stop gamepad manager
        self.gamepad_manager.stop()

    def _on_key_press(self, key):
        """Handle keyboard key press.

        Args:
            key: The key that was pressed.
        """
        try:
            # Get key code as string
            key_code = None

            # Try to get vk (virtual key code) for special keys
            if hasattr(key, 'vk'):
                key_code = f"<{key.vk}>"
            # Try to get char for character keys
            elif hasattr(key, 'char') and key.char:
                key_code = key.char

            print(f"⌨️  Key pressed: {key_code} (looking for translate={self.translate_key}, tts={self.tts_key})")

            # Check against configured hotkeys
            if key_code == self.translate_key:
                current_time = time.time()
                if current_time - self.last_translate_time > self.debounce_time:
                    self.last_translate_time = current_time
                    print(f"⌨️  Translate triggered by {key_code}")
                    self.translate_callback()

            elif key_code == self.tts_key:
                current_time = time.time()
                if current_time - self.last_tts_time > self.debounce_time:
                    self.last_tts_time = current_time
                    print(f"⌨️  TTS triggered by {key_code}")
                    self.tts_callback()

        except Exception as e:
            print(f"Hotkey error: {e}")
