# GameLingo

Real-time OCR and translation tool for games and other applications. Perfect for translating non-localized games like Pokémon ROMs running in emulators, with advanced features for language learning.

## Features

- **Dual Operating Modes**:
  - **Continuous Mode**: Automatically monitors and translates text as it appears
  - **Hotkey Mode**: Manual translation on keypress/gamepad button (perfect for turn-based games!)
- **Multi-Region Support**: Select multiple single-line regions for perfect multi-line OCR accuracy
- **Language Learning**: Built-in Google TTS to hear original text pronunciation
- **Global Hotkeys**: Works even when game window has focus (keyboard + gamepad support!)
- **Gamepad Support**: Configure any controller button (Xbox, PlayStation, 8BitDo, etc.)
- **Free Services**: Uses Tesseract OCR (free, local) and Google Translate (free, no API key required)
- **Multi-language Support**: 18+ languages including Italian, Japanese, Korean, Chinese, and more
- **Optimized for Pixel Fonts**: Advanced preprocessing specifically tuned for game text
- **Debug Display**: Shows both OCR-detected text and translation for troubleshooting
- **Cross-platform**: Works on Windows and Linux
- **Smart Caching**: Avoids redundant translations for better performance
- **Floating Display**: Clean, color-coded translation overlay window

## Requirements

- Python 3.14 or higher
- Tesseract OCR (see installation instructions below)
- uv (Python package manager)
- Optional: Game controller (Xbox, PlayStation, 8BitDo, etc.) for hotkey mode

## Installation

### 1. Install Python and uv

**Windows:**
```bash
# Download Python 3.14+ from python.org
# Install uv
pip install uv
```

**Linux:**
```bash
# Install Python 3.14+ via your package manager
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Tesseract OCR

Tesseract is required for text recognition.

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Add Tesseract to your PATH, or note the installation path (usually `C:\Program Files\Tesseract-OCR\tesseract.exe`)

**IMPORTANT**: Install the language pack for your source language:
- During installation, check the box for additional languages (e.g., Italian, Japanese, etc.)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr

# For Italian language support (if translating from Italian)
sudo apt-get install tesseract-ocr-ita

# For other languages:
# Japanese: tesseract-ocr-jpn
# Korean: tesseract-ocr-kor
# Spanish: tesseract-ocr-spa
```

**Linux (Fedora):**
```bash
sudo dnf install tesseract
sudo dnf install tesseract-langpack-ita  # Italian
```

**Linux (Arch):**
```bash
sudo pacman -S tesseract
sudo pacman -S tesseract-data-ita  # Italian
```

### 3. Install Screen Translate

```bash
cd gamelingo
uv sync
```

This will automatically create a virtual environment and install all dependencies.

## Usage

### Starting the Application

```bash
# Using uv (recommended)
uv run gamelingo

# Or after activating the virtual environment
source .venv/bin/activate  # Linux
.venv\Scripts\activate     # Windows
python -m gamelingo
```

## Operating Modes

### Continuous Mode (Auto-Translation)

Best for: Cutscenes, visual novels, streaming text

1. **Launch the application**: Run `uv run gamelingo`

2. **Select Mode**: Choose "continuous" from the Mode dropdown

3. **Set Up Region(s)**:
   - **For single-line text**: Click "Set Region", drag over the text line
   - **For multi-line text** (RECOMMENDED for best accuracy):
     - Click "Set Region", drag over the FIRST line only
     - Click "Add Region", drag over the SECOND line only
     - Repeat for additional lines
     - Each line will be OCR'd separately and concatenated

4. **Configure Languages**:
   - Select source language (e.g., `it` for Italian)
   - Select target language (e.g., `en` for English)

5. **Start Monitoring**:
   - Click "Start Monitoring"
   - A floating window will appear showing both OCR text (orange) and translation (green)
   - Translations update automatically every interval

6. **Stop Monitoring**: Click "Stop Monitoring" when done

### Hotkey Mode (Manual Translation) 🎮

Best for: Turn-based games, language learning, on-demand translation

1. **Launch the application**: Run `uv run gamelingo`

2. **Select Mode**: Choose "hotkey" from the Mode dropdown

3. **Configure Hotkeys** (optional):
   - Click "Configure Hotkeys" button
   - **Keyboard**: Click "Set" and press any key (default: Numpad 0 for translate, Numpad . for TTS)
   - **Gamepad**: Click "Set" and press any controller button (default: Button 0 for translate, Button 1 for TTS)
   - Click "Save"

4. **Set Up Region(s)**:
   - **For multi-line dialogue**: Set up multiple single-line regions (see above)
   - This gives perfect OCR accuracy on game text!

5. **Start Hotkey Mode**: Click "Start Monitoring"

6. **Play Your Game**:
   - When dialogue appears, press your **translate hotkey** (e.g., Numpad 0 or Button 0)
   - Translation appears instantly in the overlay window
   - To hear the original Italian pronunciation, press your **TTS hotkey** (e.g., Numpad . or Button 1)
   - **Hotkeys work globally** - even when game window has focus!

7. **Language Learning Workflow**:
   ```
   Dialogue appears → Press translate → Read English → Press TTS → Hear Italian
   ```

## Multi-Region Setup for Multi-Line Text

**Why use multi-region?**
- Each line is OCR'd separately using single-line mode (PSM 7)
- Prevents Tesseract from blurring lines together
- Results in 95%+ OCR accuracy on game text!

**How to set up:**

For this two-line dialogue:
```
┌─────────────────────────────┐
│ Tu e la tua squadra di      │ ← Line 1
│ Pokémon siete in forma!     │ ← Line 2
└─────────────────────────────┘
```

1. Click "Set Region" (or "Clear All" first)
2. Drag over JUST the first line
3. Click "Add Region"
4. Drag over JUST the second line
5. Status shows: "2 regions selected (lines will be concatenated)"

**Result:**
- OCR: "Tu e la tua squadra di Pokémon siete in forma!"
- Translation: "You and your Pokémon team are in shape!"

## Gamepad Support

### Compatible Controllers

- Xbox 360/One/Series controllers
- PlayStation 4/5 controllers (via USB or DS4Windows)
- 8BitDo controllers (M30, SN30 Pro+, etc.)
- Any XInput or DirectInput compatible gamepad

### 8BitDo Controller Setup

**Make sure your 8BitDo is in the right mode:**
- Press **START + R** to switch to XInput mode
- Check Windows "Set up USB game controllers" (run `joy.cpl`) to verify it's detected
- The controller should appear as "6B controller" or similar

### Configuring Buttons

1. Click "Configure Hotkeys"
2. Under "Gamepad Buttons", click "Set"
3. Press the button you want to use
4. The dialog shows which button was captured (e.g., "Button 3 (Y/Triangle)")
5. Repeat for the TTS button
6. Click "Save"

**Recommended Mapping:**
- Button 0 (A/Cross) → Translate
- Button 1 (B/Circle) → Speak Original Text (TTS)

## Tips for Best Results

### For Pokémon Games (MelonDS/other emulators)

- **Use multi-region mode** for multi-line dialogue (select each line separately!)
- Select just the textbox area, not the entire screen
- Make sure the text is clearly visible (good contrast)
- Adjust emulator window size for clearer text if needed
- Use hotkey mode for turn-based gameplay
- Use continuous mode for cutscenes

### For Better OCR Accuracy on Game Text

- **Multi-line text**: ALWAYS use multi-region mode (select each line separately)
- **Single-line text**: Use single region
- Ensure good contrast between text and background
- Select regions that include only the text area (no borders)
- Avoid including decorative borders or animations in the selection
- The app is optimized for pixel fonts (uses 4x NEAREST neighbor upscaling)

### Language Learning Tips

- Use **hotkey mode** to control the pace
- Press translate hotkey when dialogue appears
- Read the English translation
- Press TTS hotkey to hear perfect Italian pronunciation (Google TTS)
- The dual display shows both original and translation for learning

### Language-Specific Tips

- Japanese/Korean: Install the appropriate Tesseract language pack
- Chinese: Use `zh-CN` (Simplified) or `zh-TW` (Traditional)
- Right-to-left languages (Arabic): May require additional configuration

## Configuration

Configuration is stored in `~/.gamelingo/config.json` (Linux) or `C:\Users\<username>\.gamelingo\config.json` (Windows).

You can manually edit this file to adjust advanced settings:

```json
{
  "source_language": "it",
  "target_language": "en",
  "capture_interval": 1.5,
  "hotkey_mode": true,
  "translate_hotkey": "<65>",
  "tts_hotkey": "<110>",
  "translate_gamepad": 0,
  "tts_gamepad": 1,
  "regions": [
    {"x": 100, "y": 550, "width": 600, "height": 25, "monitor": 0},
    {"x": 100, "y": 580, "width": 600, "height": 25, "monitor": 0}
  ],
  "tesseract_path": null,
  "preprocess_image": true,
  "translation_cache_size": 100,
  "similarity_threshold": 0.85,
  "display_window_opacity": 0.9,
  "display_font_size": 16,
  "display_width": 600,
  "display_height": 250
}
```

### Configuration Options

**Language Settings:**
- `source_language`: Source language code (it, ja, ko, etc.)
- `target_language`: Target language code (en, es, fr, etc.)

**Capture Settings:**
- `capture_interval`: Seconds between screen captures in continuous mode (0.5-10.0)
- `regions`: Array of screen regions to capture (supports multi-region for multi-line text)
- `region`: Single region (deprecated, use `regions` instead)

**Hotkey Settings:**
- `hotkey_mode`: true = hotkey mode, false = continuous mode
- `translate_hotkey`: Keyboard key code (e.g., `"<65>"` for Numpad 0)
- `tts_hotkey`: Keyboard key code for TTS (e.g., `"<110>"` for Numpad .)
- `translate_gamepad`: Gamepad button index (0-9, e.g., 0 = A/Cross)
- `tts_gamepad`: Gamepad button index for TTS

**OCR Settings:**
- `tesseract_path`: Path to tesseract executable (null = auto-detect)
- `preprocess_image`: Apply image enhancement before OCR (recommended: true)

**Translation Settings:**
- `translation_cache_size`: Number of translations to cache
- `similarity_threshold`: Text similarity ratio to reuse cached translation (0.0-1.0)

**Display Settings:**
- `display_window_opacity`: Translation window opacity (0.0-1.0)
- `display_font_size`: Font size for translations
- `display_width/height`: Translation window dimensions

## Supported Languages

Source/Target languages:
- English (en)
- Italian (it)
- Spanish (es)
- French (fr)
- German (de)
- Portuguese (pt)
- Japanese (ja)
- Korean (ko)
- Chinese Simplified (zh-CN)
- Chinese Traditional (zh-TW)
- Russian (ru)
- Arabic (ar)
- Hindi (hi)
- Dutch (nl)
- Polish (pl)
- Turkish (tr)
- Vietnamese (vi)
- Thai (th)

Note: For OCR, you need to install the corresponding Tesseract language pack.

## Troubleshooting

### "Tesseract not found" error

**Windows:**
- Ensure Tesseract is installed
- Add Tesseract to PATH or set `tesseract_path` in config.json
- Example: `"tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"`

**Linux:**
- Install tesseract-ocr package: `sudo apt-get install tesseract-ocr`
- Verify installation: `tesseract --version`

### OCR not detecting text correctly

**For Multi-Line Text:**
- Use multi-region mode! Select each line separately
- This is the #1 solution for poor multi-line OCR

**General OCR Issues:**
- Try toggling `preprocess_image` in config (true/false)
- Ensure the source language is correct
- Install the appropriate Tesseract language pack
- Make sure text in the selected region is clear and readable
- Try increasing the emulator/game window size

**The dual display shows:**
- Orange text = What OCR detected
- Green text = Translation
- If orange text is wrong, it's an OCR issue
- If orange is right but green is wrong, it's a translation issue

### Translation not working

- Check internet connection (Google Translate requires internet)
- Verify source and target language codes are correct
- Check if the OCR is extracting text (look at orange text in display)
- Try clearing the cache by restarting the application

### TTS (Text-to-Speech) not working

- Check internet connection (Google TTS requires internet)
- Verify source language has TTS support
- Check console for TTS errors
- Make sure OCR detected text first (press translate hotkey before TTS hotkey)

### Hotkeys not working

**Keyboard hotkeys:**
- Check console output when pressing keys
- Console shows: `⌨️ Key pressed: <65>` for every key
- If you see the key but no trigger, reconfigure the hotkey
- Make sure you're in "hotkey" mode, not "continuous"

**Gamepad hotkeys:**
- Make sure gamepad is detected: `✓ Gamepad detected: [name]`
- If "No gamepad detected", check Windows Game Controllers (run `joy.cpl`)
- For 8BitDo: Press START + R to switch to XInput mode
- Press any button to verify the gamepad is responding
- Check console for `🎮 Gamepad button: X` messages

### Gamepad not detected

**8BitDo Controllers:**
- Press **START + R** to switch to XInput mode
- The LED should change pattern
- Verify in Windows: Run `joy.cpl` and check if controller appears
- Try reconnecting the 2.4GHz dongle

**General:**
- Make sure controller is turned on and connected
- Check batteries/charge level
- Try a different USB port
- Restart the application
- Check Windows Device Manager for driver issues

### "DirectX error" when configuring gamepad

- This is fixed - make sure you're using the latest version
- If it still happens, restart the application
- Try closing and reopening the "Configure Hotkeys" dialog

### High CPU usage

- Increase `capture_interval` (e.g., 2.0 or 2.5 seconds)
- Select smaller screen regions
- Use hotkey mode instead of continuous mode
- Close other applications

### Application crashes or freezes

- Check that Python 3.14+ is installed: `python --version`
- Reinstall dependencies: `uv sync --force`
- Check for error messages in the console
- Try running with verbose output: `python -m gamelingo`

## Development

### Project Structure

```
gamelingo/
├── src/
│   └── gamelingo/
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Entry point
│       ├── config.py           # Configuration management
│       ├── capture.py          # Screen capture (thread-safe)
│       ├── ocr.py              # OCR processing (optimized for games)
│       ├── translate.py        # Translation
│       ├── display.py          # Translation display window
│       ├── gui.py              # Main GUI
│       ├── hotkeys.py          # Global hotkey manager
│       ├── hotkey_dialog.py    # Hotkey configuration dialog
│       ├── gamepad.py          # Gamepad input handling
│       ├── tts.py              # Google TTS for language learning
│       └── utils.py            # Utility functions
├── pyproject.toml              # Package configuration
├── README.md                   # This file
└── .python-version             # Python version

```

### Running from Source

```bash
cd gamelingo
uv sync
uv run gamelingo
```

## How It Works

1. **Screen Capture**: Uses `mss` library with thread-safe design to capture screen regions
2. **Multi-Region Processing**: Captures and processes each region separately for perfect multi-line OCR
3. **Image Preprocessing**:
   - 4x upscaling using NEAREST neighbor (preserves pixel font edges)
   - Gentle contrast enhancement
   - Optimized specifically for pixelated game fonts
4. **OCR**: Uses Tesseract with adaptive PSM mode selection based on region aspect ratio
5. **Text Concatenation**: Combines multi-region results intelligently
6. **Translation**: Uses Google Translate (via deep-translator) to translate the text
7. **TTS**: Uses Google TTS for natural pronunciation in source language
8. **Caching**: Caches translations to improve performance and reduce API calls
9. **Global Hotkeys**: Uses pynput for keyboard, pygame for gamepad (works even when unfocused)
10. **Display**: Shows both OCR and translation in a color-coded floating window

## Privacy & Data

- All OCR processing happens **locally** on your machine
- Screenshots are **never uploaded** anywhere
- Translation uses Google Translate's public API (same as translate.google.com)
- TTS uses Google TTS public API (same as Google Translate's speak feature)
- No data is collected or stored except local configuration and cache
- Temporary TTS audio files are automatically deleted after playback

## License

MIT License - Feel free to use, modify, and distribute.

## Credits

Built with:
- [pytesseract](https://github.com/madmaze/pytesseract) - Tesseract OCR wrapper
- [deep-translator](https://github.com/nidhaloff/deep-translator) - Google Translate wrapper
- [gTTS](https://github.com/pndurette/gTTS) - Google Text-to-Speech
- [mss](https://github.com/BoboTiG/python-mss) - Fast cross-platform screen capture
- [Pillow](https://python-pillow.org/) - Image processing
- [pynput](https://github.com/moses-palmer/pynput) - Global keyboard input
- [pygame-ce](https://github.com/pygame-community/pygame-ce) - Gamepad input handling
- [playsound3](https://github.com/sjmikler/playsound3) - Audio playback

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## Roadmap

Completed features:
- [x] Hotkey support for manual translation
- [x] Multiple region monitoring (multi-line support)
- [x] Text-to-speech for language learning
- [x] Gamepad/controller support
- [x] Dual display (OCR + translation)

Potential future improvements:
- [ ] EasyOCR support as alternative OCR engine
- [ ] System tray icon
- [ ] Save/load region presets
- [ ] Custom translation services (DeepL, etc.)
- [ ] Offline translation models
- [ ] Adjustable preprocessing settings in GUI
- [ ] OCR confidence scoring
- [ ] Translation history view
