import os
from dotenv import load_dotenv

# Load env from .env file in the overlay_ai package directory or parent
# Adjust path as necessary
BASE_DIR = os.path.dirname(os.path.dirname("."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment.")

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower() # 'openai' or 'ollama'
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llava")

# Llama.cpp Config
LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "") # Path to .gguf file
LLAMA_CLIP_PATH = os.getenv("LLAMA_CLIP_PATH", "") # Path to mmproj .gguf (required for vision)
LLAMA_N_GPU_LAYERS = int(os.getenv("LLAMA_N_GPU_LAYERS", "0")) # -1 for all

TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
