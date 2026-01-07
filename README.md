# Overlay AI Assistant

A transparent, context-aware desktop overlay assistant that sees what you see. Built with Python and PySide6.

## Features

*   **Context-Aware**: Captures your screen to understand what you are working on.
*   **Transparent Overlay**: Always-on-top, non-intrusive UI that blends into your workflow.
*   **Smart Capture**: Only captures the screen when you ask (e.g., "Look at this error", "Help @screen").
*   **Multimodal AI Support**:
    *   **OpenAI**: Uses GPT-4o for state-of-the-art reasoning and vision.
    *   **Ollama**: Free local inference using Llava (Vision) and other models.
    *   **Llama.cpp**: Standalone local AI (no server required) using `.gguf` models.
*   **RAG (Retrieval Augmented Generation)**: Upload your own PDF/TXT manuals, and the assistant will answer based on them.
*   **Privacy First**: Your screen data never leaves your machine if you use Local AI providers.

## Installation

1.  **Clone the Repo** (or download source).
2.  **Install Python 3.10+**.
3.  **Install Dependencies**:
    ```bash
    pip install -r overlay_ai/requirements.txt
    ```
4.  **Install Tesseract OCR**:
    *   Download and install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
    *   Note the installation path (default: `C:\Program Files\Tesseract-OCR\tesseract.exe`).

## Configuration

1.  Copy `.env.example` to `.env` inside `overlay_ai/`.
2.  Choose your **AI Provider**:

    **Option A: OpenAI (Best Quality)**
    ```env
    AI_PROVIDER=openai
    OPENAI_API_KEY=sk-...
    ```

    **Option B: Ollama (Free, Local)**
    *   Install [Ollama](https://ollama.com).
    *   Run `ollama run llava` (for vision support).
    ```env
    AI_PROVIDER=ollama
    OLLAMA_MODEL=llava
    ```

    **Option C: Llama.cpp (Standalone)**
    *   Download a `.gguf` model (e.g., `llava-v1.5-7b-Q4_K.gguf`)(https://huggingface.co/mozilla-ai/llava-v1.5-7b-llamafile/blob/main/llava-v1.5-7b-Q4_K.gguf) and its projector (`mmproj-model-f16.gguf`)(https://huggingface.co/mys/ggml_llava-v1.5-7b/blob/main/mmproj-model-f16.gguf).
    ```env
    AI_PROVIDER=llamacpp
    LLAMA_MODEL_PATH=C:/path/to/llava.gguf
    LLAMA_CLIP_PATH=C:/path/to/mmproj.gguf
    LLAMA_N_GPU_LAYERS=-1
    ```

## Usage

1.  **Run the App**:
    ```bash
    python main.py
    ```
2.  **Toggle Overlay**: Press `Ctrl + Shift + A`.

3.  **Upload Manuals(NOT tested)S**: Click the `+` button to add PDFs for the AI to reference.


