"""Translation functionality."""

import sys
from typing import Optional
from collections import OrderedDict
from deep_translator import GoogleTranslator

from .utils import calculate_text_similarity_levenshtein


class TranslationCache:
    """LRU cache for translations."""
    
    def __init__(self, max_size: int = 100):
        """Initialize translation cache.
        
        Args:
            max_size: Maximum number of cached translations.
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, str] = OrderedDict()
    
    def get(self, text: str) -> Optional[str]:
        """Get cached translation.
        
        Args:
            text: Text to look up.
        
        Returns:
            Cached translation or None if not found.
        """
        if text in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(text)
            return self.cache[text]
        return None
    
    def put(self, text: str, translation: str):
        """Store translation in cache.
        
        Args:
            text: Original text.
            translation: Translated text.
        """
        if text in self.cache:
            # Update existing entry
            self.cache.move_to_end(text)
            self.cache[text] = translation
        else:
            # Add new entry
            self.cache[text] = translation
            
            # Remove oldest entry if cache is full
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
    
    def clear(self):
        """Clear all cached translations."""
        self.cache.clear()


class Translator:
    """Handles text translation."""
    
    def __init__(
        self,
        source_lang: str = "it",
        target_lang: str = "en",
        cache_size: int = 100,
        similarity_threshold: float = 0.85
    ):
        """Initialize translator.
        
        Args:
            source_lang: Source language code.
            target_lang: Target language code.
            cache_size: Maximum number of cached translations.
            similarity_threshold: Minimum similarity to reuse cached translation.
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.similarity_threshold = similarity_threshold
        self.cache = TranslationCache(max_size=cache_size)
        self._last_source_text = ""
        self._last_translation = ""
        
        # Initialize Google Translator
        try:
            self.translator = GoogleTranslator(source=source_lang, target=target_lang)
        except Exception as e:
            print(f"Warning: Failed to initialize translator: {e}", file=sys.stderr)
            self.translator = None
    
    def translate(self, text: str, force: bool = False) -> str:
        """Translate text from source to target language.
        
        Args:
            text: Text to translate.
            force: Force translation even if similar to last text.
        
        Returns:
            Translated text.
        """
        if not text or not text.strip():
            return ""
        
        # Normalize text
        text = text.strip()
        
        # Check if text is very similar to last translation (avoid redundant API calls)
        if not force and self._last_source_text:
            similarity = calculate_text_similarity_levenshtein(text, self._last_source_text)
            if similarity >= self.similarity_threshold:
                return self._last_translation
        
        # Check cache
        cached = self.cache.get(text)
        if cached is not None:
            self._last_source_text = text
            self._last_translation = cached
            return cached
        
        # Perform translation
        try:
            if self.translator is None:
                # Reinitialize if needed
                self.translator = GoogleTranslator(
                    source=self.source_lang,
                    target=self.target_lang
                )
            
            translation = self.translator.translate(text)
            
            # Cache the result
            self.cache.put(text, translation)
            
            # Remember for similarity check
            self._last_source_text = text
            self._last_translation = translation
            
            return translation
            
        except Exception as e:
            print(f"Translation error: {e}", file=sys.stderr)
            
            # Return the last successful translation if available
            if self._last_translation:
                return f"{self._last_translation} [error]"
            
            # Return original text as fallback
            return text
    
    def set_languages(self, source_lang: str, target_lang: str):
        """Update source and target languages.
        
        Args:
            source_lang: New source language code.
            target_lang: New target language code.
        """
        if source_lang != self.source_lang or target_lang != self.target_lang:
            self.source_lang = source_lang
            self.target_lang = target_lang
            
            # Reinitialize translator
            try:
                self.translator = GoogleTranslator(source=source_lang, target=target_lang)
                # Clear cache since language pair changed
                self.cache.clear()
                self._last_source_text = ""
                self._last_translation = ""
            except Exception as e:
                print(f"Failed to update translator languages: {e}", file=sys.stderr)
    
    def clear_cache(self):
        """Clear translation cache."""
        self.cache.clear()
        self._last_source_text = ""
        self._last_translation = ""


def get_supported_languages() -> dict[str, str]:
    """Get dictionary of supported language codes and names.
    
    Returns:
        Dictionary mapping language codes to language names.
    """
    # Common languages for gaming
    return {
        'en': 'English',
        'it': 'Italian',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'pt': 'Portuguese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-CN': 'Chinese (Simplified)',
        'zh-TW': 'Chinese (Traditional)',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'nl': 'Dutch',
        'pl': 'Polish',
        'tr': 'Turkish',
        'vi': 'Vietnamese',
        'th': 'Thai',
    }
