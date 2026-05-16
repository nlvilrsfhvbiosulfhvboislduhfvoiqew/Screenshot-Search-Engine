# Screenshot Search Engine

A fully offline, Python-based desktop application that automatically indexes your screenshots and allows you to search through them using natural language or keywords via OCR.

![App Preview](assets/preview.png) *(Preview image placeholder)*

## Features

- **Fully Offline**: No API keys, no cloud dependencies. Your data stays on your machine.
- **Background OCR**: Extracts text from images using PyTesseract without freezing the UI.
- **Smart Search**: Combines exact keyword matching with fuzzy matching to tolerate typos.
- **Auto-Indexing**: Uses a file watcher to automatically index new screenshots added to watched folders.
- **Duplicate Detection**: Uses Perceptual Hashing (pHash) to prevent indexing exact duplicates.
- **Modern UI**: Built with CustomTkinter for a sleek, dark-mode ready interface.

## Architecture

This app uses a clean architecture pattern:
- **GUI**: CustomTkinter handles the modern look and feel.
- **Database**: SQLite3 stores image paths, metadata, hashes, and OCR text.
- **OCR Engine**: PyTesseract handles text extraction. OpenCV is used for image preprocessing (grayscale, Otsu's thresholding) to improve accuracy on UI screenshots.
- **Background Workers**: `watchdog` monitors folders, while a threaded queue processes images sequentially.
- **Search Engine**: `thefuzz` ranks results based on filename exact matches, OCR text exact matches, and fuzzy token ratio scores.

## Prerequisites

Before running the application, you **must** install Tesseract-OCR on your system.

### Installing Tesseract-OCR (Windows)
1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the installer.
3. Ensure Tesseract is installed in a standard location like `C:\Program Files\Tesseract-OCR\tesseract.exe`. The app will attempt to auto-detect it.

## Installation (Source)

1. Clone this repository or download the source code.
2. Install Python 3.9+ and pip.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app/main.py
   ```

## Packaging as an Executable

You can build a standalone `.exe` using PyInstaller. 

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run the following build command from the root directory:
   ```bash
   pyinstaller --noconfirm --onedir --windowed --add-data "app/database/schema.sql;app/database/" --add-data "assets;assets/" --name "ScreenshotSearchEngine" app/main.py
   ```
3. The built application will be located in the `dist/ScreenshotSearchEngine` folder.

> **Note**: Even as an executable, the user's system must have Tesseract-OCR installed. To create a completely standalone app, you would need to bundle the Tesseract binaries within the `assets/` folder and update `app/ocr/engine.py` to point to the bundled executable relative path.

## Usage

1. Open the App.
2. Go to **Settings** and click **Add Folder**. Select your screenshots folder.
3. The app will immediately start indexing in the background. You can see logs in `app.log`.
4. Go to the **Search** tab and type keywords.
5. Click a thumbnail to see a large preview and copy the extracted text.

## Future Improvements

- Semantic search using local sentence-transformers.
- Image similarity search (finding visually similar screenshots).
- Multi-language OCR configuration from the UI.
