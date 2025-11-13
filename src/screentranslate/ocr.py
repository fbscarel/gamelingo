"""OCR processing functionality."""

import sys
import platform
from typing import Optional
from pathlib import Path
from PIL import Image
import pytesseract

from .utils import preprocess_image_for_ocr, clean_ocr_text, calculate_image_hash


class OCREngine:
    """Handles OCR processing of images."""
    
    def __init__(self, tesseract_path: Optional[str] = None, preprocess: bool = True):
        """Initialize OCR engine.
        
        Args:
            tesseract_path: Path to tesseract executable. If None, auto-detect.
            preprocess: Whether to preprocess images before OCR.
        """
        self.preprocess = preprocess
        self._last_text = ""
        self._last_image_hash: Optional[str] = None
        
        # Set tesseract path if provided or try to auto-detect
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            self._auto_detect_tesseract()
    
    def _auto_detect_tesseract(self):
        """Auto-detect tesseract executable path based on platform."""
        system = platform.system()
        
        if system == "Windows":
            # Common Windows installation paths
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                Path.home() / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe",
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    pytesseract.pytesseract.tesseract_cmd = str(path)
                    return
        
        # On Linux/Mac, tesseract should be in PATH
        # pytesseract will handle it automatically
    
    def extract_text(self, image: Image.Image, language: str = "eng") -> str:
        """Extract text from image using OCR.

        Args:
            image: PIL Image to process.
            language: Language code for OCR (e.g., 'eng', 'ita', 'jpn').

        Returns:
            Extracted text string.
        """
        # Check if image is the same as last time (avoid redundant processing)
        image_hash = calculate_image_hash(image)
        if image_hash == self._last_image_hash:
            return self._last_text

        try:
            # Preprocess image if enabled
            if self.preprocess:
                processed_image = preprocess_image_for_ocr(image)
            else:
                processed_image = image

            # Smart PSM mode selection for multi-line game text
            # Detect if image is likely multi-line based on aspect ratio
            img_height, img_width = processed_image.height, processed_image.width
            aspect_ratio = img_height / img_width if img_width > 0 else 1.0

            # If tall/square image (multi-line), prioritize block modes
            # If wide image (single line), prioritize single-line mode
            if aspect_ratio > 0.3:  # Likely multi-line (height > 30% of width)
                # PSM 6: Uniform block of text (best for multi-line)
                # PSM 3: Fully automatic (handles any layout)
                # PSM 7: Single line (fallback)
                psm_modes = [6, 3, 7]
            else:  # Likely single line (very wide box)
                # PSM 7: Single text line (best for single line)
                # PSM 6: Block of text (fallback)
                # PSM 3: Automatic (last resort)
                psm_modes = [7, 6, 3]

            best_text = ""
            all_results = {}  # Store all results to pick best one

            for psm in psm_modes:
                try:
                    custom_config = f'--oem 3 --psm {psm}'

                    # Perform OCR
                    text = pytesseract.image_to_string(
                        processed_image,
                        lang=language,
                        config=custom_config
                    )

                    # Clean up the text
                    text = clean_ocr_text(text)

                    # Store result with character count as quality metric
                    if text.strip():
                        all_results[psm] = text

                        # For multi-line: accept first good result (PSM 6 or 3)
                        # For single-line: accept first good result (PSM 7)
                        if psm == psm_modes[0]:
                            best_text = text
                            break

                except Exception as e:
                    # Try next PSM mode
                    continue

            # If no result from primary mode, use any valid result
            if not best_text and all_results:
                # Pick the longest result (more text = better detection)
                best_text = max(all_results.values(), key=len)

            # Cache the result
            self._last_text = best_text
            self._last_image_hash = image_hash

            return best_text

        except pytesseract.TesseractNotFoundError:
            error_msg = self._get_tesseract_install_instructions()
            raise RuntimeError(error_msg)
        except Exception as e:
            print(f"OCR error: {e}", file=sys.stderr)
            return ""
    
    def _get_tesseract_install_instructions(self) -> str:
        """Get platform-specific instructions for installing Tesseract.
        
        Returns:
            Installation instructions string.
        """
        system = platform.system()
        
        if system == "Windows":
            return (
                "Tesseract OCR not found!\n\n"
                "Please install Tesseract:\n"
                "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Run the installer\n"
                "3. Add to PATH or set tesseract_path in config.json\n"
            )
        elif system == "Linux":
            return (
                "Tesseract OCR not found!\n\n"
                "Please install Tesseract:\n"
                "  Ubuntu/Debian: sudo apt-get install tesseract-ocr\n"
                "  Fedora: sudo dnf install tesseract\n"
                "  Arch: sudo pacman -S tesseract\n"
                "\n"
                "For non-English languages, install language packs:\n"
                "  Ubuntu/Debian: sudo apt-get install tesseract-ocr-ita (for Italian)\n"
            )
        elif system == "Darwin":  # macOS
            return (
                "Tesseract OCR not found!\n\n"
                "Please install Tesseract:\n"
                "  brew install tesseract\n"
                "\n"
                "For non-English languages:\n"
                "  brew install tesseract-lang\n"
            )
        else:
            return "Tesseract OCR not found! Please install Tesseract."
    
    def is_available(self) -> bool:
        """Check if Tesseract is available.
        
        Returns:
            True if Tesseract can be found, False otherwise.
        """
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
    
    def get_available_languages(self) -> list[str]:
        """Get list of installed Tesseract language packs.
        
        Returns:
            List of language codes.
        """
        try:
            langs = pytesseract.get_languages()
            return langs
        except:
            return ["eng"]  # Default fallback


def map_language_to_tesseract(lang_code: str) -> str:
    """Map standard language code to Tesseract language code.
    
    Args:
        lang_code: Standard language code (e.g., 'it', 'en', 'ja').
    
    Returns:
        Tesseract language code (e.g., 'ita', 'eng', 'jpn').
    """
    mapping = {
        'en': 'eng',
        'it': 'ita',
        'es': 'spa',
        'fr': 'fra',
        'de': 'deu',
        'pt': 'por',
        'ja': 'jpn',
        'ko': 'kor',
        'zh-CN': 'chi_sim',
        'zh-TW': 'chi_tra',
        'ru': 'rus',
        'ar': 'ara',
        'hi': 'hin',
        'nl': 'nld',
        'pl': 'pol',
        'tr': 'tur',
        'vi': 'vie',
        'th': 'tha',
    }
    
    return mapping.get(lang_code, 'eng')
