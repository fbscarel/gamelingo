"""Utility functions for Screen Translate."""

import hashlib
from typing import Optional
from PIL import Image, ImageEnhance, ImageOps


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts using simple ratio.
    
    Args:
        text1: First text string.
        text2: Second text string.
    
    Returns:
        Similarity score between 0.0 and 1.0.
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize texts (strip whitespace, lowercase)
    t1 = text1.strip().lower()
    t2 = text2.strip().lower()
    
    if t1 == t2:
        return 1.0
    
    # Simple character-based similarity
    # Count matching characters in order
    matches = sum(c1 == c2 for c1, c2 in zip(t1, t2))
    max_len = max(len(t1), len(t2))
    
    if max_len == 0:
        return 0.0
    
    return matches / max_len


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings.
    
    Args:
        s1: First string.
        s2: Second string.
    
    Returns:
        Edit distance between strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def calculate_text_similarity_levenshtein(text1: str, text2: str) -> float:
    """Calculate similarity using Levenshtein distance.
    
    Args:
        text1: First text string.
        text2: Second text string.
    
    Returns:
        Similarity score between 0.0 and 1.0.
    """
    if not text1 or not text2:
        return 0.0
    
    t1 = text1.strip().lower()
    t2 = text2.strip().lower()
    
    if t1 == t2:
        return 1.0
    
    distance = levenshtein_distance(t1, t2)
    max_len = max(len(t1), len(t2))
    
    if max_len == 0:
        return 0.0
    
    return 1.0 - (distance / max_len)


def calculate_image_hash(image: Image.Image) -> str:
    """Calculate hash of an image for quick comparison.
    
    Args:
        image: PIL Image object.
    
    Returns:
        MD5 hash string.
    """
    # Convert to bytes and hash
    img_bytes = image.tobytes()
    return hashlib.md5(img_bytes).hexdigest()


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """Preprocess image to improve OCR accuracy for PIXEL FONTS.

    CRITICAL for pixel/bitmap fonts (game text):
    - Uses NEAREST neighbor upscaling (preserves sharp pixel edges)
    - Minimal enhancement (Tesseract handles the rest)
    - NO binary thresholding (Tesseract's internal is better)

    Args:
        image: Input PIL Image.

    Returns:
        Preprocessed PIL Image optimized for pixel fonts.
    """
    # Upscale image 4x using NEAREST neighbor for pixel fonts!
    # NEAREST preserves sharp pixel boundaries (no blur/smoothing)
    # CRITICAL: DO NOT use LANCZOS/BICUBIC - they blur pixel fonts!
    width, height = image.size
    img = image.resize((width * 4, height * 4), Image.Resampling.NEAREST)

    # Convert to grayscale for consistent processing
    img = ImageOps.grayscale(img)

    # MINIMAL contrast enhancement (let Tesseract do the heavy lifting)
    # Pixel fonts don't need much - they're already high contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)  # Very gentle enhancement

    # Return grayscale image - NO sharpening, NO binary threshold
    # Tesseract's internal algorithms work best on clean, unmodified pixels
    return img


def clean_ocr_text(text: str) -> str:
    """Clean up OCR output text.
    
    Removes extra whitespace, common OCR errors, etc.
    
    Args:
        text: Raw OCR text.
    
    Returns:
        Cleaned text.
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove common OCR artifacts
    text = text.replace('|', 'I')  # Common mistake
    text = text.replace('０', '0')  # Full-width to half-width
    
    return text.strip()


def format_translation_text(original: str, translated: str) -> str:
    """Format original and translated text for display.
    
    Args:
        original: Original text.
        translated: Translated text.
    
    Returns:
        Formatted string for display.
    """
    return f"{translated}"


def validate_language_code(lang_code: str) -> bool:
    """Validate if language code is supported.
    
    Args:
        lang_code: Two-letter language code (e.g., 'en', 'it').
    
    Returns:
        True if valid, False otherwise.
    """
    # Common language codes
    valid_codes = {
        'en', 'it', 'es', 'fr', 'de', 'pt', 'ja', 'ko', 'zh-CN', 'zh-TW',
        'ru', 'ar', 'hi', 'nl', 'pl', 'tr', 'vi', 'th', 'id', 'ms'
    }
    
    return lang_code in valid_codes
