# Scope
![Scope Icon](res/icon.png)
**Scope** is a powerful screen snipping tool for Linux built with Python and CustomTkinter. It allows you to capture any part of your screen and instantly perform OCR to extract text, translate it into over 100 languages, or scan QR codes directly from your desktop.

## Features

*   **Capture**: Select and screenshot any area of your screen using `slop` and `maim`.
*   **Extract**: Instantly convert images to text using Tesseract OCR.
*   **Translate**: Translate extracted text into 50+ languages on the fly.
*   **Interact**: Scan QR codes, search text on Google, or copy to clipboard with a single click.
*   **Modern UI**: Built with CustomTkinter for a sleek, dark-mode friendly interface.

## Requirements

*   Python 3.x
*   `slop`
*   `maim`
*   `tesseract-ocr`
*   `xclip`

## Installation

1.  Install system dependencies:
    ```bash
    sudo apt install slop maim tesseract-ocr xclip
    ```

2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the application:
```bash
python main.py
```

## Version History
*   **v1.0**: Initial Release. Features: Screen Capture, OCR, Clipboard Copy, Theme Support. ![More Info](./v1.0/README.md)
