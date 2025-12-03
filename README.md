# Screen Translation Application

A desktop application that allows you to capture text from any area of your screen using OCR and translate it to your preferred language.

## Features

- **Drag & Drop Selection**: Select any area on your screen to capture text
- **OCR Text Extraction**: Uses Tesseract OCR to extract text from screenshots
- **Multiple Translation Options**:
  - OpenAI API (GPT models)
  - Google Translate API
  - Ollama (offline, local models like Gemma)
- **Configurable Settings**: Choose OCR language, target language, and translation backend
- **Offline Support**: Use Ollama for completely offline translation

## Requirements

- Python 3.8+
- Tesseract OCR installed on your system
- (Optional) Ollama installed for offline translation

## Installation

1. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH or update path in code

2. (Optional) Install Ollama:
   - Download from: https://ollama.ai
   - Pull models: `ollama pull gemma`

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### Quick Start
1. Click "Start Capture" button or use hotkey
2. Drag to select the screen area with text
3. Text will be captured, translated, and displayed
4. Configure settings in the Settings tab

## Configuration

Edit `config.json` or use the Settings tab:
- `ocr_language`: Tesseract language code (e.g., "eng", "spa", "chi_sim")
- `target_language`: Translation target (e.g., "es", "en", "zh")
- `translation_backend`: "openai", "google", or "ollama"
- API keys and model configurations

## License

MIT
