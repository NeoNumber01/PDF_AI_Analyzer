# PDF AI Analyzer

<p align="center">
  <strong>🤖 Multi-Platform AI Image Analysis Automation Tool</strong>
</p>

<p align="center">
  English | <a href="./README.md">简体中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/GUI-PySide6-green.svg" alt="GUI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## ✨ Features

PDF AI Analyzer is an automation tool that converts PDF files page by page into images and automatically sends them to multiple mainstream AI platforms for analysis and explanation.

### 🎯 Core Features

- **📄 PDF to Image**: High-quality PDF page conversion using PyMuPDF (no Poppler required)
- **🤖 Multi-Platform Support**: Supports ChatGPT, Claude, Google Gemini, and DeepSeek
- **🔄 Automated Processing**: Automatic image upload, prompt sending, response waiting, and next page processing
- **💾 Session Persistence**: Browser login state automatically saved, no re-login required
- **🎨 Modern UI**: Beautiful Glassmorphism-style GUI

### 🌐 Supported AI Platforms

| Platform | URL | Status |
|----------|-----|--------|
| ChatGPT | chatgpt.com | ✅ Supported |
| Google Gemini | gemini.google.com | ✅ Supported |
| DeepSeek | chat.deepseek.com | ✅ Supported |
| Claude | claude.ai | ✅ Supported |

---

## 📦 Installation

### System Requirements

- **Operating System**: Windows 10/11, macOS, Linux
- **Python**: 3.11 or higher
- **Browser**: Chrome or Edge (Playwright handles this automatically)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/NeoNumber01/PDF_AI_Analyzer.git
cd PDF_AI_Analyzer

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright browser
playwright install chromium
```

> 💡 **Note**: This project uses PyMuPDF for PDF to image conversion, no external dependencies like Poppler required.

---

## 🚀 Usage

### Method 1: GUI (Recommended)

**Windows users**: Double-click `启动.bat` or run in PowerShell:

```powershell
.\启动.ps1
```

**Or run manually**:

```bash
python src/gui_pyside.py
```

### Method 2: Command Line

```bash
# Interactive mode
python src/main.py

# Specify PDF file
python src/main.py "path/to/your/file.pdf"
```

### Workflow

1. **Launch the program** - Run the startup script or GUI
2. **Select AI platform** - Choose the AI platform to use
3. **Start browser** - Click "Start Browser" button
4. **Login** - Log in to your AI platform account (first time only)
5. **Select PDF** - Choose the PDF file to analyze
6. **Start processing** - Click "Start Processing", the program will automatically send each page and wait for responses

> ⚠️ **First Run**: You need to manually log in to your AI platform account. The login state will be saved to the `browser_data/` directory for future sessions.

---

## ⚙️ Configuration

Edit `config.py` to customize the following settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `PROMPT_TEXT` | "Please explain..." | Prompt sent to AI |
| `PDF_DPI` | 200 | PDF to image resolution |
| `WAIT_TIMEOUT` | 120000 | Response timeout (ms) |
| `DELAY_BETWEEN_PAGES` | 3 | Delay between pages (seconds) |

---

## 📁 Project Structure

```
PDF_AI_Analyzer/
├── src/
│   ├── gui_pyside.py         # PySide6 GUI (main entry)
│   ├── base_automation.py    # AI platform base class
│   ├── chatgpt_automation.py # ChatGPT automation
│   ├── claude_automation.py  # Claude automation
│   ├── gemini_automation.py  # Gemini automation
│   ├── deepseek_automation.py# DeepSeek automation
│   ├── platform_factory.py   # Platform factory pattern
│   ├── pdf_converter.py      # PDF to image module
│   └── main.py               # CLI entry
├── browser_data/             # Browser data (login state)
├── output/                   # Converted images
├── config.py                 # Configuration file
├── requirements.txt          # Python dependencies
├── 启动.bat                  # Windows startup script
├── 启动.ps1                  # PowerShell startup script
└── 打包.bat                  # PyInstaller packaging script
```

---

## 🔧 Troubleshooting

### PDF Conversion Failed
- Ensure PyMuPDF is correctly installed: `pip install PyMuPDF`
- Check if the PDF file is corrupted or encrypted

### Browser Startup Failed
- Run `playwright install chromium` to install the browser
- Check `browser_data/` directory permissions

### Login State Lost
- Delete the `browser_data/` directory and log in again
- Ensure the browser is closed properly

### AI Response Timeout
- Increase the `WAIT_TIMEOUT` value in `config.py`
- Check network connection stability

---

## 📝 Dependencies

```
PyMuPDF>=1.23.0      # PDF processing
Pillow>=10.0.0       # Image processing
playwright>=1.40.0   # Browser automation
python-dotenv>=1.0.0 # Environment variables
PySide6>=6.6.0       # GUI framework
customtkinter>=5.2.0 # Alternative GUI (optional)
pywinstyles>=1.8     # Windows styles (optional)
```

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
