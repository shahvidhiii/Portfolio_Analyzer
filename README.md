Analyzer Prototype

Simple Streamlit prototype to upload investment screenshots, run OCR, parse holdings, and show a basic dashboard with suggestions.

Prerequisites
- Python 3.9+
- Tesseract OCR installed on your system (https://github.com/tesseract-ocr/tesseract). On Windows, add Tesseract to PATH or set pytesseract.pytesseract.tesseract_cmd.

Quick start
```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Files
- `app.py` — Streamlit app
- `ocr_utils.py` — image preprocessing + pytesseract wrapper
- `parser.py` — simple heuristics to extract holdings from OCR text

Notes
- This is an MVP. OCR accuracy depends on screenshot quality; consider using a cloud OCR for production.
