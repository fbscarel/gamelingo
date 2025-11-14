"""GUI components for GameLingo."""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional, Callable

from .config import ConfigManager, RegionConfig
from .capture import ScreenCapture, get_screen_info
from .ocr import OCREngine, map_language_to_tesseract
from .translate import Translator, get_supported_languages
from .display import TranslationDisplay
from .tts import TTSEngine
from .hotkeys import HotkeyManager
from .hotkey_dialog import HotkeyConfigDialog


class RegionSelector:
    """Interactive screen region selector."""
    
    def __init__(self, callback: Callable[[int, int, int, int], None]):
        """Initialize region selector.
        
        Args:
            callback: Function to call with selected region (x, y, width, height).
        """
        self.callback = callback
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.selecting = False
        
        # Create fullscreen transparent window
        self.window = tk.Toplevel()
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-alpha", 0.3)
        self.window.attributes("-topmost", True)
        
        # Create canvas for drawing selection rectangle
        self.canvas = tk.Canvas(
            self.window,
            bg="black",
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Escape>", lambda e: self.cancel())
        
        # Rectangle object
        self.rect = None
        
        # Instructions
        self.canvas.create_text(
            self.window.winfo_screenwidth() // 2,
            50,
            text="Click and drag to select screen region. Press ESC to cancel.",
            fill="white",
            font=("Arial", 16)
        )
    
    def on_mouse_down(self, event):
        """Handle mouse button press."""
        self.start_x = event.x
        self.start_y = event.y
        self.selecting = True
        
        # Create rectangle
        if self.rect:
            self.canvas.delete(self.rect)
        
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red",
            width=2
        )
    
    def on_mouse_move(self, event):
        """Handle mouse movement."""
        if self.selecting and self.rect:
            self.current_x = event.x
            self.current_y = event.y
            
            # Update rectangle
            self.canvas.coords(
                self.rect,
                self.start_x, self.start_y,
                self.current_x, self.current_y
            )
    
    def on_mouse_up(self, event):
        """Handle mouse button release."""
        if not self.selecting:
            return
        
        self.selecting = False
        self.current_x = event.x
        self.current_y = event.y
        
        # Calculate region coordinates
        x = min(self.start_x, self.current_x)
        y = min(self.start_y, self.current_y)
        width = abs(self.current_x - self.start_x)
        height = abs(self.current_y - self.start_y)
        
        # Close window
        self.window.destroy()
        
        # Call callback with region
        if width > 10 and height > 10:  # Minimum size
            self.callback(x, y, width, height)
    
    def cancel(self):
        """Cancel selection."""
        self.window.destroy()


class MainGUI:
    """Main application GUI."""
    
    def __init__(self):
        """Initialize main GUI."""
        self.config_manager = ConfigManager()
        self.config_manager.load()
        self.config = self.config_manager.config
        
        # Initialize components
        self.capture = ScreenCapture()
        self.ocr_engine: Optional[OCREngine] = None
        self.translator: Optional[Translator] = None
        self.display: Optional[TranslationDisplay] = None
        self.tts_engine: Optional[TTSEngine] = None

        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Hotkey state
        self.hotkey_manager: Optional[HotkeyManager] = None
        self.last_ocr_text: str = ""  # Store last OCR'd text for TTS
        self.last_translated_text: str = ""  # Store last translated text for TTS
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("GameLingo")
        self.root.geometry("550x480")
        self.root.resizable(False, False)
        
        self._create_widgets()
        self._initialize_engines()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _create_widgets(self):
        """Create GUI widgets."""
        # Title
        title_label = tk.Label(
            self.root,
            text="GameLingo",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)
        
        # Region selection frame
        region_frame = ttk.LabelFrame(self.root, text="Screen Regions (Multi-Line Support)", padding=10)
        region_frame.pack(fill=tk.X, padx=10, pady=5)

        # Region info label
        self.region_info_label = tk.Label(
            region_frame,
            text=self._get_region_info_text()
        )
        self.region_info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Button frame for region controls
        button_frame = ttk.Frame(region_frame)
        button_frame.pack(side=tk.RIGHT)

        ttk.Button(
            button_frame,
            text="Set Region",
            command=lambda: self.select_region(replace=True)
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="Add Region",
            command=lambda: self.select_region(replace=False)
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="Clear All",
            command=self.clear_regions
        ).pack(side=tk.LEFT, padx=2)
        
        # Language selection frame
        lang_frame = ttk.LabelFrame(self.root, text="Languages", padding=10)
        lang_frame.pack(fill=tk.X, padx=10, pady=5)
        
        languages = get_supported_languages()
        lang_codes = list(languages.keys())
        
        # Source language
        tk.Label(lang_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.source_lang_var = tk.StringVar(value=self.config.source_language)
        source_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.source_lang_var,
            values=lang_codes,
            state="readonly",
            width=10
        )
        source_combo.grid(row=0, column=1, padx=5)
        
        # Target language
        tk.Label(lang_frame, text="To:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.target_lang_var = tk.StringVar(value=self.config.target_language)
        target_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.target_lang_var,
            values=lang_codes,
            state="readonly",
            width=10
        )
        target_combo.grid(row=0, column=3, padx=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(self.root, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Mode selection
        tk.Label(settings_frame, text="Mode:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.mode_var = tk.StringVar(value="hotkey" if self.config.hotkey_mode else "continuous")
        mode_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.mode_var,
            values=["continuous", "hotkey"],
            state="readonly",
            width=12
        )
        mode_combo.grid(row=0, column=1, padx=5)
        mode_combo.bind('<<ComboboxSelected>>', self._on_mode_changed)

        # Capture interval (only for continuous mode)
        tk.Label(settings_frame, text="Capture Interval (s):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.interval_var = tk.DoubleVar(value=self.config.capture_interval)
        interval_spin = ttk.Spinbox(
            settings_frame,
            from_=0.5,
            to=10.0,
            increment=0.5,
            textvariable=self.interval_var,
            width=10
        )
        interval_spin.grid(row=1, column=1, padx=5)

        # Hotkey configuration button
        ttk.Button(
            settings_frame,
            text="Configure Hotkeys",
            command=self._open_hotkey_config
        ).grid(row=2, column=0, columnspan=2, pady=10)

        # Hotkey info label
        self.hotkey_info = tk.Label(
            settings_frame,
            text="Hotkeys work globally (even when window not focused)",
            fg="blue",
            font=("Arial", 9)
        )
        self.hotkey_info.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = ttk.Button(
            control_frame,
            text="Start Monitoring",
            command=self.start_monitoring,
            width=20
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            control_frame,
            text="Stop Monitoring",
            command=self.stop_monitoring,
            state=tk.DISABLED,
            width=20
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            fg="green",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)
    
    def _initialize_engines(self):
        """Initialize OCR and translation engines."""
        try:
            # Initialize OCR
            tesseract_lang = map_language_to_tesseract(self.config.source_language)
            self.ocr_engine = OCREngine(
                tesseract_path=self.config.tesseract_path,
                preprocess=self.config.preprocess_image
            )
            
            # Check if Tesseract is available
            if not self.ocr_engine.is_available():
                messagebox.showwarning(
                    "Tesseract Not Found",
                    "Tesseract OCR is not installed or not in PATH.\n"
                    "Please install Tesseract to use this application.\n\n"
                    "See README for installation instructions."
                )
            
            # Initialize translator
            self.translator = Translator(
                source_lang=self.config.source_language,
                target_lang=self.config.target_language,
                cache_size=self.config.translation_cache_size,
                similarity_threshold=self.config.similarity_threshold
            )
            
            # Initialize display window
            self.display = TranslationDisplay(
                width=self.config.display_width,
                height=self.config.display_height,
                opacity=self.config.display_window_opacity,
                font_size=self.config.display_font_size,
                always_on_top=self.config.display_on_top
            )

            # Initialize TTS engine
            self.tts_engine = TTSEngine(language=self.config.source_language)
            if not self.tts_engine.is_available():
                print("Warning: TTS engine not available")

        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize: {e}")
    
    def _get_region_info_text(self) -> str:
        """Get display text for region info."""
        if not self.config.regions:
            return "No regions selected"

        num_regions = len(self.config.regions)
        if num_regions == 1:
            r = self.config.regions[0]
            return f"1 region: ({r.x}, {r.y}, {r.width}x{r.height})"
        else:
            return f"{num_regions} regions selected (lines will be concatenated)"

    def select_region(self, replace: bool = True):
        """Open region selector.

        Args:
            replace: If True, replaces all regions. If False, adds to existing.
        """
        def on_region_selected(x, y, width, height):
            if replace:
                self.config_manager.update_region(x, y, width, height)
                msg = f"Region set to: {x}, {y}, {width}x{height}"
            else:
                self.config_manager.add_region(x, y, width, height)
                num_regions = len(self.config_manager.config.regions)
                msg = f"Added region #{num_regions}: {x}, {y}, {width}x{height}"

            self.config = self.config_manager.config
            self.region_info_label.config(text=self._get_region_info_text())
            messagebox.showinfo("Region Selected", msg)
            self.root.focus_force()

        # Hide main window
        self.root.withdraw()

        # Show region selector
        selector = RegionSelector(on_region_selected)

        # Wait for selector to close, then show main window
        self.root.after(100, self._check_selector_closed)

    def clear_regions(self):
        """Clear all regions."""
        self.config_manager.clear_regions()
        self.config = self.config_manager.config
        self.region_info_label.config(text=self._get_region_info_text())
        messagebox.showinfo("Regions Cleared", "All regions have been cleared.")

    def _on_mode_changed(self, event=None):
        """Handle mode change in dropdown."""
        mode = self.mode_var.get()
        if mode == "hotkey":
            self.hotkey_info.config(text="Hotkeys work globally (even when window not focused)")
        else:
            self.hotkey_info.config(text="Continuous monitoring (auto-updates every interval)")

    def _open_hotkey_config(self):
        """Open hotkey configuration dialog."""
        HotkeyConfigDialog(self.root, self.config_manager)

    def _check_selector_closed(self):
        """Check if region selector is closed and restore main window."""
        try:
            # Try to access selector window
            self.root.deiconify()
            self.root.focus_force()
        except:
            # Selector still open, check again
            self.root.after(100, self._check_selector_closed)
    
    def _do_manual_translation(self):
        """Perform a single translation (triggered by hotkey)."""
        print("🔵 Manual translation triggered!")
        try:
            # Capture and OCR each region separately
            tesseract_lang = map_language_to_tesseract(self.config.source_language)
            text_lines = []

            for i, region in enumerate(self.config.regions):
                # Capture this region
                image = self.capture.capture_region(region)

                # Extract text from this region
                text = self.ocr_engine.extract_text(image, language=tesseract_lang)

                print(f"   Region {i+1} OCR: '{text}'")

                # Add to lines if not empty
                if text and text.strip():
                    text_lines.append(text.strip())

            # Concatenate all lines with space
            combined_text = " ".join(text_lines) if text_lines else ""

            if combined_text:
                # Store for TTS
                self.last_ocr_text = combined_text
                print(f"✓ Combined OCR: '{combined_text}'")

                # Translate
                translation = self.translator.translate(combined_text)
                print(f"✓ Translation: '{translation}'")
                
                # Store translated text for TTS
                self.last_translated_text = translation if translation else ""

                # Update display
                if self.display:
                    self.display.update_text(
                        ocr_text=combined_text,
                        translated_text=translation if translation else "(translation failed)"
                    )
            else:
                print("⚠ No text detected in any region")

        except Exception as e:
            print(f"❌ Manual translation error: {e}")
            import traceback
            traceback.print_exc()

    def _do_tts_speak(self):
        """Speak the last OCR'd text in source language (triggered by hotkey)."""
        if self.last_ocr_text and self.tts_engine:
            # Ensure TTS is set to source language
            self.tts_engine.set_language(self.config.source_language)
            print(f"🔊 Speaking original text: {self.last_ocr_text}")
            self.tts_engine.speak(self.last_ocr_text, blocking=False)

    def _do_translated_tts_speak(self):
        """Speak the last translated text in target language (triggered by hotkey)."""
        if self.last_translated_text and self.tts_engine:
            # Set TTS to target language for translated text
            self.tts_engine.set_language(self.config.target_language)
            print(f"🔊 Speaking translation: {self.last_translated_text}")
            self.tts_engine.speak(self.last_translated_text, blocking=False)

    def start_monitoring(self):
        """Start monitoring and translation."""
        if self.is_monitoring:
            return

        # Update configuration from UI
        mode = self.mode_var.get()
        self.config.hotkey_mode = (mode == "hotkey")
        self.config.source_language = self.source_lang_var.get()
        self.config.target_language = self.target_lang_var.get()
        self.config.capture_interval = self.interval_var.get()
        self.config_manager.save()

        # Verify Tesseract language pack is installed
        if self.ocr_engine:
            available_langs = self.ocr_engine.get_available_languages()
            tesseract_lang = map_language_to_tesseract(self.config.source_language)

            if tesseract_lang not in available_langs:
                messagebox.showwarning(
                    "Language Pack Missing",
                    f"Tesseract language pack '{tesseract_lang}' is not installed!\n\n"
                    f"OCR may produce poor results. Please install the language pack:\n"
                    f"  Windows: Download from https://github.com/tesseract-ocr/tessdata\n"
                    f"  Linux: sudo apt-get install tesseract-ocr-{tesseract_lang[:3]}\n\n"
                    f"Available languages: {', '.join(available_langs)}"
                )

        # Update translator languages
        if self.translator:
            self.translator.set_languages(
                self.config.source_language,
                self.config.target_language
            )

        # Update TTS language
        if self.tts_engine:
            self.tts_engine.set_language(self.config.source_language)

        # Show display window
        if self.display:
            self.display.create_window(self.root)
            self.display.show()

        # Start based on mode
        self.is_monitoring = True

        # Reload config to ensure we have latest hotkey settings
        self.config_manager.load()
        self.config = self.config_manager.config

        print(f"🔧 Starting in mode: {'HOTKEY' if self.config.hotkey_mode else 'CONTINUOUS'}")
        print(f"   Translate key: {self.config.translate_hotkey}")
        print(f"   TTS key: {self.config.tts_hotkey}")
        print(f"   Translated TTS key: {self.config.translated_tts_hotkey}")
        print(f"   Translate gamepad: {self.config.translate_gamepad}")
        print(f"   TTS gamepad: {self.config.tts_gamepad}")
        print(f"   Translated TTS gamepad: {self.config.translated_tts_gamepad}")

        if self.config.hotkey_mode:
            # Hotkey mode: Start global hotkey manager (keyboard + gamepad)
            self.hotkey_manager = HotkeyManager(
                translate_callback=self._do_manual_translation,
                tts_callback=self._do_tts_speak,
                translated_tts_callback=self._do_translated_tts_speak,
                translate_key=self.config.translate_hotkey,
                tts_key=self.config.tts_hotkey,
                translated_tts_key=self.config.translated_tts_hotkey,
                translate_gamepad=self.config.translate_gamepad,
                tts_gamepad=self.config.tts_gamepad,
                translated_tts_gamepad=self.config.translated_tts_gamepad
            )
            self.hotkey_manager.start()
            print("✓ Hotkey manager started (global keyboard + gamepad)")
            status_text = "Hotkey Mode Active (Global - works in game!)"
        else:
            # Continuous mode: Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("✓ Continuous monitoring started")
            status_text = "Monitoring..."

        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text=status_text, fg="blue")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.is_monitoring = False

        # Stop monitoring thread if running
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

        # Stop hotkey manager if running
        if self.hotkey_manager:
            self.hotkey_manager.stop()
            self.hotkey_manager = None

        # Stop any ongoing TTS
        if self.tts_engine:
            self.tts_engine.stop()

        # Hide display window
        if self.display:
            self.display.hide()

        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", fg="red")
    
    def _monitor_loop(self):
        """Main monitoring loop (runs in separate thread)."""
        last_text = ""

        while self.is_monitoring:
            try:
                # Capture and OCR each region separately
                tesseract_lang = map_language_to_tesseract(self.config.source_language)
                text_lines = []

                for region in self.config.regions:
                    # Capture this region
                    image = self.capture.capture_region(region)

                    # Extract text from this region (single-line OCR works best)
                    text = self.ocr_engine.extract_text(image, language=tesseract_lang)

                    # Add to lines if not empty
                    if text and text.strip():
                        text_lines.append(text.strip())

                # Concatenate all lines with space
                combined_text = " ".join(text_lines) if text_lines else ""

                # If text changed significantly, translate it
                if combined_text and combined_text != last_text:
                    translation = self.translator.translate(combined_text)

                    # Update display with BOTH OCR and translation
                    if self.display:
                        self.display.update_text(
                            ocr_text=combined_text,
                            translated_text=translation if translation else "(translation failed)"
                        )

                    last_text = combined_text

                # Wait before next capture
                time.sleep(self.config.capture_interval)

            except Exception as e:
                print(f"Monitor loop error: {e}")
                time.sleep(1.0)  # Wait a bit before retry
    
    def on_close(self):
        """Handle window close event."""
        self.stop_monitoring()

        if self.display:
            self.display.destroy()

        if self.capture:
            self.capture.close()

        if self.tts_engine:
            self.tts_engine.cleanup()

        self.root.destroy()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
