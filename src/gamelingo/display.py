"""Translation display window."""

import tkinter as tk
from tkinter import font as tkfont
from typing import Optional


class TranslationDisplay:
    """Floating window to display translated text."""
    
    def __init__(
        self,
        width: int = 600,
        height: int = 150,
        opacity: float = 0.9,
        font_size: int = 16,
        always_on_top: bool = True
    ):
        """Initialize translation display window.
        
        Args:
            width: Window width in pixels.
            height: Window height in pixels.
            opacity: Window opacity (0.0 to 1.0).
            font_size: Font size for translated text.
            always_on_top: Keep window always on top.
        """
        self.width = width
        self.height = height
        self.opacity = opacity
        self.font_size = font_size
        self.always_on_top = always_on_top
        
        # Create window
        self.window: Optional[tk.Toplevel] = None
        self.text_widget: Optional[tk.Text] = None
        self.is_visible = False
    
    def create_window(self, parent: Optional[tk.Tk] = None):
        """Create the display window.
        
        Args:
            parent: Parent window. If None, creates standalone window.
        """
        if self.window is not None:
            return
        
        # Create toplevel window
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            root = tk.Tk()
            root.withdraw()  # Hide root window
            self.window = tk.Toplevel(root)
        
        self.window.title("Translation")
        self.window.geometry(f"{self.width}x{self.height}")
        
        # Set window properties
        self.window.attributes("-alpha", self.opacity)
        if self.always_on_top:
            self.window.attributes("-topmost", True)
        
        # Remove window decorations (optional - makes it cleaner)
        # Uncomment the next line for borderless window
        # self.window.overrideredirect(True)
        
        # Create text widget with tags for different sections
        custom_font = tkfont.Font(family="Arial", size=self.font_size, weight="bold")
        label_font = tkfont.Font(family="Arial", size=self.font_size - 2, weight="normal")

        self.text_widget = tk.Text(
            self.window,
            font=custom_font,
            wrap=tk.WORD,
            bg="#2b2b2b",
            fg="#ffffff",
            padx=10,
            pady=10,
            relief=tk.FLAT,
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for formatting
        self.text_widget.tag_configure("label", font=label_font, foreground="#888888")
        self.text_widget.tag_configure("ocr", foreground="#ffcc66")  # Orange for OCR
        self.text_widget.tag_configure("translation", foreground="#66ff66")  # Green for translation
        self.text_widget.tag_configure("separator", foreground="#444444")

        # Make text widget read-only
        self.text_widget.config(state=tk.DISABLED)
        
        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        self.is_visible = True
    
    def update_text(self, ocr_text: str = "", translated_text: str = ""):
        """Update displayed text with both OCR and translation.

        Args:
            ocr_text: Original OCR detected text.
            translated_text: Translated text.
        """
        if self.text_widget is None:
            return

        # Enable editing temporarily
        self.text_widget.config(state=tk.NORMAL)

        # Clear previous text
        self.text_widget.delete(1.0, tk.END)

        # Insert OCR text section
        if ocr_text:
            self.text_widget.insert(tk.END, "🔍 OCR: ", "label")
            self.text_widget.insert(tk.END, f"{ocr_text}\n", "ocr")

        # Insert separator
        if ocr_text and translated_text:
            self.text_widget.insert(tk.END, "─" * 50 + "\n", "separator")

        # Insert translation section
        if translated_text:
            self.text_widget.insert(tk.END, "🌐 Translation: ", "label")
            self.text_widget.insert(tk.END, translated_text, "translation")

        # Disable editing again
        self.text_widget.config(state=tk.DISABLED)
    
    def show(self):
        """Show the window."""
        if self.window is None:
            self.create_window()
        
        if self.window:
            self.window.deiconify()
            self.is_visible = True
    
    def hide(self):
        """Hide the window."""
        if self.window:
            self.window.withdraw()
            self.is_visible = False
    
    def destroy(self):
        """Destroy the window."""
        if self.window:
            self.window.destroy()
            self.window = None
            self.text_widget = None
            self.is_visible = False
    
    def set_position(self, x: int, y: int):
        """Set window position.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        if self.window:
            self.window.geometry(f"+{x}+{y}")
    
    def set_opacity(self, opacity: float):
        """Set window opacity.
        
        Args:
            opacity: Opacity value (0.0 to 1.0).
        """
        self.opacity = max(0.0, min(1.0, opacity))
        if self.window:
            self.window.attributes("-alpha", self.opacity)
    
    def update(self):
        """Update the window (process events)."""
        if self.window:
            self.window.update()
