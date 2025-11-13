"""Main entry point for Screen Translate."""

import sys
import argparse
from .gui import MainGUI


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Screen Translate - Real-time OCR and translation for games"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(f"Screen Translate v{__version__}")
        sys.exit(0)
    
    # Run the GUI
    try:
        app = MainGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
