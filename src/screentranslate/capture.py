"""Screen capture functionality."""

from typing import Optional
import threading
import mss
from PIL import Image
from .config import RegionConfig


class ScreenCapture:
    """Handles screen region capture."""

    def __init__(self):
        """Initialize screen capture."""
        self._sct_local = threading.local()
        self._last_image_hash: Optional[str] = None

    @property
    def sct(self):
        """Get or create thread-local MSS instance.

        MSS uses thread-local storage for Windows device contexts.
        This property ensures each thread gets its own MSS instance.
        """
        if not hasattr(self._sct_local, 'instance'):
            self._sct_local.instance = mss.mss()
        return self._sct_local.instance

    def get_monitors(self) -> list[dict]:
        """Get information about available monitors.

        Returns:
            List of monitor information dictionaries.
        """
        return self.sct.monitors[1:]  # Skip monitor 0 (all monitors combined)
    
    def capture_region(self, region: RegionConfig) -> Image.Image:
        """Capture a specific screen region.
        
        Args:
            region: Region configuration with coordinates and size.
        
        Returns:
            PIL Image of the captured region.
        """
        # Get monitor info to handle multi-monitor setups
        monitors = self.sct.monitors
        
        # Validate monitor index
        if region.monitor < 0 or region.monitor >= len(monitors):
            region.monitor = 0  # Use all monitors combined
        
        # If monitor is 0, use absolute coordinates
        # Otherwise, coordinates are relative to the specific monitor
        if region.monitor == 0:
            monitor_offset = {"left": 0, "top": 0}
        else:
            monitor = monitors[region.monitor]
            monitor_offset = {"left": monitor["left"], "top": monitor["top"]}
        
        # Define the capture region
        capture_area = {
            "left": monitor_offset["left"] + region.x,
            "top": monitor_offset["top"] + region.y,
            "width": region.width,
            "height": region.height,
            "mon": region.monitor,
        }
        
        # Capture the screen
        screenshot = self.sct.grab(capture_area)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        
        return img
    
    def capture_full_screen(self, monitor: int = 0) -> Image.Image:
        """Capture entire screen or specific monitor.
        
        Args:
            monitor: Monitor number (0 for all monitors, 1+ for specific).
        
        Returns:
            PIL Image of the screen.
        """
        # Validate monitor index
        monitors = self.sct.monitors
        if monitor < 0 or monitor >= len(monitors):
            monitor = 1  # Default to primary monitor
        
        screenshot = self.sct.grab(monitors[monitor])
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        
        return img
    
    def close(self):
        """Clean up resources."""
        if hasattr(self._sct_local, 'instance'):
            self._sct_local.instance.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def get_screen_info() -> dict:
    """Get information about available screens.
    
    Returns:
        Dictionary with screen information.
    """
    with mss.mss() as sct:
        monitors = sct.monitors
        
        return {
            "monitor_count": len(monitors) - 1,  # Exclude "all monitors"
            "monitors": [
                {
                    "index": i,
                    "left": mon["left"],
                    "top": mon["top"],
                    "width": mon["width"],
                    "height": mon["height"],
                }
                for i, mon in enumerate(monitors[1:], start=1)
            ],
        }
