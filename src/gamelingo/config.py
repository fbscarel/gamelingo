"""Configuration management for GameLingo."""

import json
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class RegionConfig:
    """Screen region coordinates."""
    x: int = 0
    y: int = 0
    width: int = 800
    height: int = 200
    monitor: int = 0  # Monitor number for multi-monitor setups


@dataclass
class Config:
    """Application configuration."""
    # Language settings
    source_language: str = "it"  # Italian
    target_language: str = "en"  # English

    # Screen capture settings
    region: RegionConfig = None  # Deprecated: use regions instead
    regions: list[RegionConfig] = None  # Multiple regions for multi-line text
    capture_interval: float = 1.5  # Seconds between captures

    # Hotkey mode settings
    hotkey_mode: bool = False  # If True, use hotkeys instead of continuous monitoring
    translate_hotkey: str = "<65>"  # Default: Keypad 0 (key code)
    tts_hotkey: str = "<110>"  # Default: Keypad . (key code)
    translated_tts_hotkey: str = "<107>"  # Default: Keypad + (key code)
    translate_gamepad: int = 0  # Default: Button 0 (A/Cross)
    tts_gamepad: int = 1  # Default: Button 1 (B/Circle)
    translated_tts_gamepad: int = 2  # Default: Button 2 (X/Square)

    # OCR settings
    ocr_engine: str = "tesseract"  # "tesseract" or "easyocr"
    tesseract_path: Optional[str] = None  # Auto-detect if None
    preprocess_image: bool = True

    # Translation settings
    translation_cache_size: int = 100
    similarity_threshold: float = 0.85  # Text similarity to skip re-translation

    # Display settings
    display_window_opacity: float = 0.9
    display_font_size: int = 16
    display_width: int = 600
    display_height: int = 250  # Increased from 150 to fit both OCR and translation
    display_on_top: bool = True

    def __post_init__(self):
        """Initialize nested objects."""
        # Backward compatibility: migrate single region to regions list
        if self.regions is None:
            if self.region is None:
                self.regions = [RegionConfig()]
            elif isinstance(self.region, dict):
                self.regions = [RegionConfig(**self.region)]
            else:
                self.regions = [self.region]
        else:
            # Convert dict regions to RegionConfig objects
            self.regions = [
                RegionConfig(**r) if isinstance(r, dict) else r
                for r in self.regions
            ]

        # Keep first region as primary for backward compatibility
        if self.regions:
            self.region = self.regions[0]
        else:
            self.region = RegionConfig()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        result = asdict(self)
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Config':
        """Create config from dictionary."""
        return cls(**data)


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            config_path = Path.home() / ".gamelingo" / "config.json"
        
        self.config_path = config_path
        self.config = Config()
    
    def load(self) -> Config:
        """Load configuration from file.
        
        Returns:
            Loaded configuration.
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.config = Config.from_dict(data)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Failed to load config: {e}")
                print("Using default configuration")
        
        return self.config
    
    def save(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config.to_dict(), f, indent=2)
    
    def update(self, **kwargs) -> None:
        """Update configuration values.
        
        Args:
            **kwargs: Configuration values to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        self.save()
    
    def update_region(self, x: int, y: int, width: int, height: int, monitor: int = 0) -> None:
        """Update screen region configuration (single region mode).

        Args:
            x: X coordinate of top-left corner.
            y: Y coordinate of top-left corner.
            width: Region width.
            height: Region height.
            monitor: Monitor number.
        """
        new_region = RegionConfig(x=x, y=y, width=width, height=height, monitor=monitor)
        self.config.region = new_region
        self.config.regions = [new_region]
        self.save()

    def add_region(self, x: int, y: int, width: int, height: int, monitor: int = 0) -> None:
        """Add a new region to multi-region configuration.

        Args:
            x: X coordinate of top-left corner.
            y: Y coordinate of top-left corner.
            width: Region width.
            height: Region height.
            monitor: Monitor number.
        """
        new_region = RegionConfig(x=x, y=y, width=width, height=height, monitor=monitor)
        if not self.config.regions:
            self.config.regions = []
        self.config.regions.append(new_region)
        self.config.region = self.config.regions[0]  # Keep first as primary
        self.save()

    def clear_regions(self) -> None:
        """Clear all regions."""
        self.config.regions = [RegionConfig()]
        self.config.region = self.config.regions[0]
        self.save()

    def remove_region(self, index: int) -> None:
        """Remove a region by index.

        Args:
            index: Index of region to remove.
        """
        if self.config.regions and 0 <= index < len(self.config.regions):
            self.config.regions.pop(index)
            if not self.config.regions:
                self.config.regions = [RegionConfig()]
            self.config.region = self.config.regions[0]
            self.save()
