# Screen Translation Application

A modern desktop application that allows you to capture text from any area of your screen using OCR and translate it to your preferred language.

## Features

- **🎨 Modern UI Design**: Beautiful dark mode theme
- **📸 Image Preview**: View captured screenshots before translation
- **🖱️ Drag & Drop Selection**: Select any area on your screen to capture text
- **🔍 Multiple OCR Engines**:
  - **Tesseract OCR**: Open source, supports 100+ languages
  - **Windows OCR**: Built-in Windows 10/11 OCR, faster and lighter (requires language packs)
- **🌐 Multiple Translation Options**:
  - Google Translate API
  - Ollama (offline, local models like Llama3, Gemma)
- **⚙️ Configurable Settings**: Choose OCR engine, target language, and translation backend
- **💾 Offline Support**: Use Ollama + Windows OCR for completely offline translation

## Requirements

- Python 3.8+
- Windows 10/11 (for Windows OCR) or Tesseract OCR installed
- (Optional) Ollama installed for offline translation

## Installation

### Option 1: Quick Install (Windows)
```bash
# Run the install script
install.bat
```

### Option 2: Manual Installation

1. **Install Python package for Windows OCR**:
   ```bash
   pip install winocr
   ```

2. **Install Windows OCR Language Packs** (for non-English text):
   
   Windows OCR requires language packs to recognize text in different languages. Install the required language pack for your target language:

   **Japanese:**
   ```powershell
   Add-WindowsCapability -Online -Name "Language.OCR~~~ja-JP~0.0.1.0"
   ```

   **Korean:**
   ```powershell
   Add-WindowsCapability -Online -Name "Language.OCR~~~ko-KR~0.0.1.0"
   ```

   **Chinese (Simplified):**
   ```powershell
   Add-WindowsCapability -Online -Name "Language.OCR~~~zh-CN~0.0.1.0"
   ```

   **Other languages:**
   - Go to Settings → Time & Language → Language & Region
   - Add your desired language (e.g., Japanese, Korean, Chinese)
   - Download the language pack (includes OCR support)

   **Note:** Administrator privileges are required to install language packs via PowerShell.

3. **(Alternative) Install Tesseract OCR**:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Download additional language packs from: https://github.com/tesseract-ocr/tessdata
     - Common language packs: jpn.traineddata, jpn_vert.traineddata, fra.traineddata
     - Save to tessdata folder (default: C:\Program Files\Tesseract-OCR\tessdata)
     - Verify by running `tesseract --list-langs` in Command Prompt
   - Add to PATH or update path in code

4. **(Optional) Install Ollama for offline translation**:
   - Download from: https://ollama.ai
   - Pull models: `ollama pull llama3` or `ollama pull gemma`

5. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### Quick Start
1. Click the **📷 Start Capture** button
2. Drag to select the screen area with text
3. View the captured image and extracted text
4. Translation appears automatically
5. Copy results with one click

### Settings
Access the **⚙️ Settings** tab to configure:
- 🎨 **Display**: Font size for result display
- 🔍 **OCR Engine**: Tesseract or Windows OCR
- 🌐 **Translation**: Source language (auto-detected), target language, backend (Ollama/Google)
- 🦙 **Ollama**: URL, model selection, connection test

## Configuration

Settings are saved in `config.json`:

```json
{
  "ocr_backend": "windows",
  "target_language": "en",
  "translation_backend": "ollama",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama3",
  "result_font_size": 14
}
```

### Available Options

| Setting | Options | Description |
|---------|---------|-------------|
| `ocr_backend` | `tesseract`, `windows` | OCR engine to use |
| `target_language` | `en`, `vi`, `ja`, `ko`, `zh`, etc. | Translation target language |
| `translation_backend` | `ollama`, `google` | Translation service |
| `ollama_url` | URL string | Ollama server URL |
| `ollama_model` | Model name | Ollama model (e.g., llama3, gemma) |
| `result_font_size` | Integer (10-28) | Font size for display |

## License

MIT
