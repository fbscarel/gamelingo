"""Gamepad detection and input handling using pygame."""

import threading
import time
from typing import Optional, Callable

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available, gamepad support disabled")


class GamepadManager:
    """Manages gamepad input detection."""

    def __init__(
        self,
        translate_callback: Callable,
        tts_callback: Callable,
        translated_tts_callback: Callable,
        translate_button: int = 0,  # A button
        tts_button: int = 1,  # B button
        translated_tts_button: int = 2  # X button
    ):
        """Initialize gamepad manager.

        Args:
            translate_callback: Function to call when translate button is pressed.
            tts_callback: Function to call when TTS button is pressed.
            translated_tts_callback: Function to call when translated TTS button is pressed.
            translate_button: Button index for translation (0=A/Cross, 1=B/Circle, etc)
            tts_button: Button index for TTS
            translated_tts_button: Button index for translated TTS
        """
        self.translate_callback = translate_callback
        self.tts_callback = tts_callback
        self.translated_tts_callback = translated_tts_callback
        self.translate_button = translate_button
        self.tts_button = tts_button
        self.translated_tts_button = translated_tts_button

        self.running = False
        self.poll_thread: Optional[threading.Thread] = None
        self.joystick: Optional[pygame.joystick.Joystick] = None

        # Track button states to prevent repeats
        self.last_translate_time = 0
        self.last_tts_time = 0
        self.last_translated_tts_time = 0
        self.debounce_time = 0.3  # 300ms debounce

        if PYGAME_AVAILABLE:
            pygame.init()
            pygame.joystick.init()

    def is_available(self) -> bool:
        """Check if pygame and gamepad support is available."""
        return PYGAME_AVAILABLE

    def detect_gamepad(self) -> bool:
        """Try to detect and initialize a gamepad.

        Returns:
            True if gamepad detected, False otherwise.
        """
        if not PYGAME_AVAILABLE:
            return False

        try:
            pygame.joystick.quit()
            pygame.joystick.init()

            joystick_count = pygame.joystick.get_count()

            if joystick_count > 0:
                # Use first detected joystick
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"✓ Gamepad detected: {self.joystick.get_name()}")
                print(f"  Buttons: {self.joystick.get_numbuttons()}")
                print(f"  Axes: {self.joystick.get_numaxes()}")
                return True
            else:
                print("✗ No gamepads detected")
                return False

        except Exception as e:
            print(f"Gamepad detection error: {e}")
            return False

    def start(self):
        """Start monitoring gamepad input."""
        if self.running or not PYGAME_AVAILABLE:
            return

        if not self.detect_gamepad():
            print("⚠ Starting without gamepad support")
            return

        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()

    def stop(self):
        """Stop monitoring gamepad input."""
        self.running = False

        if self.poll_thread:
            self.poll_thread = None

        if self.joystick:
            try:
                self.joystick.quit()
            except:
                pass
            self.joystick = None

    def _poll_loop(self):
        """Poll gamepad state (runs in background thread)."""
        while self.running:
            try:
                if not self.joystick:
                    # Try to reconnect
                    if self.detect_gamepad():
                        time.sleep(0.1)
                        continue
                    else:
                        time.sleep(2.0)
                        continue

                # Process pygame events
                pygame.event.pump()

                # Check button states
                num_buttons = self.joystick.get_numbuttons()

                for i in range(num_buttons):
                    button_state = self.joystick.get_button(i)

                    if button_state:  # Button pressed
                        current_time = time.time()

                        if i == self.translate_button:
                            if current_time - self.last_translate_time > self.debounce_time:
                                self.last_translate_time = current_time
                                print(f"🎮 Translate triggered by button {i}")
                                self.translate_callback()

                        elif i == self.tts_button:
                            if current_time - self.last_tts_time > self.debounce_time:
                                self.last_tts_time = current_time
                                print(f"🎮 TTS triggered by button {i}")
                                self.tts_callback()

                        elif i == self.translated_tts_button:
                            if current_time - self.last_translated_tts_time > self.debounce_time:
                                self.last_translated_tts_time = current_time
                                print(f"🎮 Translated TTS triggered by button {i}")
                                self.translated_tts_callback()

                # Poll at 60Hz
                time.sleep(1/60)

            except Exception as e:
                print(f"Gamepad polling error: {e}")
                # Try to reconnect
                self.joystick = None
                time.sleep(1.0)

    def wait_for_button_press(self, timeout: float = 10.0) -> Optional[int]:
        """Wait for a button press and return the button index.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            Button index if pressed, None if timeout.
        """
        if not PYGAME_AVAILABLE or not self.joystick:
            if not self.detect_gamepad():
                return None

        start_time = time.time()
        pressed_buttons = set()

        # Record currently pressed buttons to ignore them
        for i in range(self.joystick.get_numbuttons()):
            if self.joystick.get_button(i):
                pressed_buttons.add(i)

        print(f"🎮 Waiting for button press... (timeout: {timeout}s)")

        while time.time() - start_time < timeout:
            try:
                pygame.event.pump()

                # Check all buttons
                for i in range(self.joystick.get_numbuttons()):
                    button_state = self.joystick.get_button(i)

                    # New button press (wasn't pressed before)
                    if button_state and i not in pressed_buttons:
                        print(f"✓ Button {i} pressed")
                        return i

                time.sleep(0.01)  # Poll at 100Hz for responsiveness

            except Exception as e:
                print(f"Error waiting for button: {e}")
                return None

        print("⏱ Timeout - no button pressed")
        return None

    def get_button_name(self, button_index: int) -> str:
        """Get human-readable name for button index.

        Args:
            button_index: Button index (0-based).

        Returns:
            Button name string.
        """
        button_names = {
            0: "A (Xbox) / Cross (PS)",
            1: "B (Xbox) / Circle (PS)",
            2: "X (Xbox) / Square (PS)",
            3: "Y (Xbox) / Triangle (PS)",
            4: "LB / L1",
            5: "RB / R1",
            6: "Select / Share",
            7: "Start / Options",
            8: "L3 (Left Stick)",
            9: "R3 (Right Stick)",
        }
        return button_names.get(button_index, f"Button {button_index}")
