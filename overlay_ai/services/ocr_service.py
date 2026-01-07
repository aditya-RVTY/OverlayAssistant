import pytesseract
from overlay_ai.utils.config import TESSERACT_CMD
import os

# Set tesseract command path
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
else:
    # If not found, hope it's in PATH, or warn
    pass

def extract_text(image):
    """
    Extracts text from a PIL Image using Tesseract.
    """
    try:
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""
