"""Hotkey configuration dialog."""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pynput import keyboard
from .gamepad import GamepadManager

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class HotkeyConfigDialog:
    """Dialog for configuring hotkeys."""

    def __init__(self, parent, config_manager):
        """Initialize hotkey config dialog.

        Args:
            parent: Parent window.
            config_manager: ConfigManager instance.
        """
        self.parent = parent
        self.config_manager = config_manager
        self.config = config_manager.config

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configure Hotkeys")
        self.dialog.geometry("550x420")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Listening state
        self.listening = False
        self.listener: keyboard.Listener = None
        self.gamepad_thread: threading.Thread = None

        # Temporary hotkey storage
        self.temp_translate_key = self.config.translate_hotkey
        self.temp_tts_key = self.config.tts_hotkey
        self.temp_translate_gamepad = self.config.translate_gamepad
        self.temp_tts_gamepad = self.config.tts_gamepad

        # Initialize pygame joystick ONCE and reuse it
        self.joystick = None
        if PYGAME_AVAILABLE:
            self._init_pygame_joystick()

        self._create_widgets()

        # Clean up on close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_pygame_joystick(self):
        """Initialize pygame joystick once."""
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.joystick.get_init():
                pygame.joystick.init()

            joystick_count = pygame.joystick.get_count()
            if joystick_count > 0:
                self.joystick = pygame.joystick.Joystick(0)
                print(f"✓ Gamepad initialized: {self.joystick.get_name()}")
            else:
                print("⚠ No gamepad detected during initialization")
        except Exception as e:
            print(f"Gamepad init error: {e}")

    def _on_close(self):
        """Clean up when dialog closes."""
        self.listening = False
        if self.joystick:
            try:
                self.joystick.quit()
            except:
                pass
        self.dialog.destroy()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Title
        title = tk.Label(
            self.dialog,
            text="Hotkey Configuration",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        # Info label
        info = tk.Label(
            self.dialog,
            text="Click 'Set' and press a key or gamepad button to configure",
            fg="blue"
        )
        info.pack(pady=5)

        # Keyboard section
        kbd_frame = ttk.LabelFrame(self.dialog, text="Keyboard Hotkeys", padding=10)
        kbd_frame.pack(fill=tk.X, padx=10, pady=5)

        # Translate key
        tk.Label(kbd_frame, text="Translate:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.translate_key_label = tk.Label(
            kbd_frame,
            text=self._format_key(self.temp_translate_key),
            bg="white",
            width=20,
            relief=tk.SUNKEN
        )
        self.translate_key_label.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            kbd_frame,
            text="Set",
            command=lambda: self._listen_for_key("translate")
        ).grid(row=0, column=2, padx=5, pady=5)

        # TTS key
        tk.Label(kbd_frame, text="Speak (TTS):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.tts_key_label = tk.Label(
            kbd_frame,
            text=self._format_key(self.temp_tts_key),
            bg="white",
            width=20,
            relief=tk.SUNKEN
        )
        self.tts_key_label.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            kbd_frame,
            text="Set",
            command=lambda: self._listen_for_key("tts")
        ).grid(row=1, column=2, padx=5, pady=5)

        # Gamepad section
        gp_frame = ttk.LabelFrame(self.dialog, text="Gamepad Buttons", padding=10)
        gp_frame.pack(fill=tk.X, padx=10, pady=5)

        # Translate button
        tk.Label(gp_frame, text="Translate:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.translate_gp_label = tk.Label(
            gp_frame,
            text=self._format_gamepad(self.temp_translate_gamepad),
            bg="white",
            width=20,
            relief=tk.SUNKEN
        )
        self.translate_gp_label.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            gp_frame,
            text="Set",
            command=lambda: self._listen_for_gamepad("translate")
        ).grid(row=0, column=2, padx=5, pady=5)

        # TTS button
        tk.Label(gp_frame, text="Speak (TTS):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.tts_gp_label = tk.Label(
            gp_frame,
            text=self._format_gamepad(self.temp_tts_gamepad),
            bg="white",
            width=20,
            relief=tk.SUNKEN
        )
        self.tts_gp_label.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            gp_frame,
            text="Set",
            command=lambda: self._listen_for_gamepad("tts")
        ).grid(row=1, column=2, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Save",
            command=self._save,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)

    def _format_key(self, key_code: str) -> str:
        """Format key code for display."""
        # Map common key codes to readable names
        key_names = {
            "<65>": "Numpad 0",
            "<110>": "Numpad .",
            "<96>": "Numpad 0 (Alt)",
            "<97>": "Numpad 1",
            "<98>": "Numpad 2",
            "<99>": "Numpad 3",
            "<100>": "Numpad 4",
            "<101>": "Numpad 5",
            "<102>": "Numpad 6",
            "<103>": "Numpad 7",
            "<104>": "Numpad 8",
            "<105>": "Numpad 9",
        }
        return key_names.get(key_code, key_code)

    def _format_gamepad(self, button_index: int) -> str:
        """Format gamepad button index for display."""
        button_names = {
            0: "Button 0 (A/Cross)",
            1: "Button 1 (B/Circle)",
            2: "Button 2 (X/Square)",
            3: "Button 3 (Y/Triangle)",
            4: "Button 4 (LB/L1)",
            5: "Button 5 (RB/R1)",
            6: "Button 6 (Select)",
            7: "Button 7 (Start)",
            8: "Button 8 (L3)",
            9: "Button 9 (R3)",
        }
        return button_names.get(button_index, f"Button {button_index}")

    def _listen_for_key(self, action: str):
        """Listen for keyboard key press.

        Args:
            action: "translate" or "tts"
        """
        if self.listening:
            return

        # Update label
        label = self.translate_key_label if action == "translate" else self.tts_key_label
        label.config(text="Press a key...", bg="yellow")

        def on_press(key):
            try:
                # Get key code
                if hasattr(key, 'vk'):
                    key_code = f"<{key.vk}>"
                elif hasattr(key, 'char') and key.char:
                    key_code = key.char
                else:
                    key_code = str(key)

                # Update temp storage
                if action == "translate":
                    self.temp_translate_key = key_code
                    self.translate_key_label.config(
                        text=self._format_key(key_code),
                        bg="white"
                    )
                else:
                    self.temp_tts_key = key_code
                    self.tts_key_label.config(
                        text=self._format_key(key_code),
                        bg="white"
                    )

                # Stop listening
                self.listening = False
                return False  # Stop listener

            except:
                return True

        self.listening = True
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def _listen_for_gamepad(self, action: str):
        """Listen for gamepad button press.

        Args:
            action: "translate" or "tts"
        """
        if self.listening:
            return

        # Update label
        label = self.translate_gp_label if action == "translate" else self.tts_gp_label
        label.config(text="Detecting gamepad...", bg="yellow")

        def gamepad_listen():
            try:
                # Check if pygame and joystick are available
                if not PYGAME_AVAILABLE or not self.joystick:
                    label.config(text="No gamepad detected", bg="red")
                    time.sleep(2)
                    label.config(text=self._format_gamepad(
                        self.temp_translate_gamepad if action == "translate" else self.temp_tts_gamepad
                    ), bg="white")
                    self.listening = False
                    return

                # Listen for button press (timeout after 10 seconds)
                print(f"🎮 Waiting for button press on {self.joystick.get_name()}...")
                label.config(text="Press a button...", bg="yellow")

                start_time = time.time()
                timeout = 10.0

                clock = pygame.time.Clock()

                while self.listening and (time.time() - start_time) < timeout:
                    # Process pygame events
                    for event in pygame.event.get():
                        if event.type == pygame.JOYBUTTONDOWN:
                            button_index = event.button
                            print(f"✓ Captured gamepad button: {button_index}")

                            # Update temp storage
                            if action == "translate":
                                self.temp_translate_gamepad = button_index
                                self.translate_gp_label.config(
                                    text=self._format_gamepad(button_index),
                                    bg="white"
                                )
                            else:
                                self.temp_tts_gamepad = button_index
                                self.tts_gp_label.config(
                                    text=self._format_gamepad(button_index),
                                    bg="white"
                                )

                            self.listening = False
                            return

                    clock.tick(60)  # 60 FPS

                # Timeout
                if self.listening:
                    label.config(text="Timeout - no button pressed", bg="orange")
                    time.sleep(1)
                    label.config(text=self._format_gamepad(
                        self.temp_translate_gamepad if action == "translate" else self.temp_tts_gamepad
                    ), bg="white")

            except Exception as e:
                print(f"❌ Gamepad listen error: {e}")
                import traceback
                traceback.print_exc()
                label.config(text="Error - see console", bg="red")
                time.sleep(2)
                label.config(text=self._format_gamepad(
                    self.temp_translate_gamepad if action == "translate" else self.temp_tts_gamepad
                ), bg="white")
            finally:
                self.listening = False

        self.listening = True
        self.gamepad_thread = threading.Thread(target=gamepad_listen, daemon=True)
        self.gamepad_thread.start()

    def _save(self):
        """Save hotkey configuration."""
        self.config.translate_hotkey = self.temp_translate_key
        self.config.tts_hotkey = self.temp_tts_key
        self.config.translate_gamepad = self.temp_translate_gamepad
        self.config.tts_gamepad = self.temp_tts_gamepad
        self.config_manager.save()

        messagebox.showinfo(
            "Success",
            "Hotkeys saved!\n\n"
            "If hotkey mode is already running, please:\n"
            "1. Click 'Stop Monitoring'\n"
            "2. Click 'Start Monitoring' again\n\n"
            "This will reload the new hotkey settings."
        )
        self.dialog.destroy()
