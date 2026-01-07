from PySide6.QtCore import QThread, Signal
from overlay_ai.services.capture_service import capture_screen
from overlay_ai.services.ocr_service import extract_text
from overlay_ai.services.llm_service import query_assistant
from overlay_ai.services.rag_service import rag_service

class AIWorker(QThread):
    finished = Signal(str)

    def __init__(self, user_text, history=None, image=None):
        super().__init__()
        self.user_text = user_text
        self.history = history or []
        self.image = image

    def run(self):
        try:
            # 1. Image & OCR (Only if provided)
            image = self.image
            text_context = ""
            
            if image:
                # 2. OCR
                text_context = extract_text(image)
            
            # 3. RAG Retrieval
            manual_context = rag_service.retrieve(self.user_text)
            
            # 4. Query LLM
            response = query_assistant(self.user_text, image, text_context, manual_context, self.history)
            
            self.finished.emit(response)
        except Exception as e:
            self.finished.emit(f"Error processing request: {e}")

class IngestWorker(QThread):
    finished = Signal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            result = rag_service.ingest_file(self.file_path)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(f"Ingestion failed: {e}")

