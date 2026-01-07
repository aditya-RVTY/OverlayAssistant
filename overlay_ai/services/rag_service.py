import os
import io
from pypdf import PdfReader
from PIL import Image as PILImage

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.docstore.document import Document

from overlay_ai.utils.config import OPENAI_API_KEY, AI_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL
from overlay_ai.services.llm_service import encode_image, client as openai_client
# We might need a generic caption function if we want local captioning too, 
# but for now captioning still uses OpenAI in the code below unless refactored.
# Let's import query_assistant to use the generic provider for captioning!
from overlay_ai.services.llm_service import query_assistant 

# Define persistence path
INDEX_PATH = os.path.join(os.path.dirname(__file__), "manual_store", "faiss_index")

class RAGService:
    def __init__(self):
        if AI_PROVIDER == "ollama":
            self.embeddings = OllamaEmbeddings(
                base_url=OLLAMA_BASE_URL, 
                model=OLLAMA_MODEL # Use the same model or a specific embedding model?
                # Usually 'llava' isn't an embedding model. 'nomic-embed-text' is better.
                # But for simplicity let's rely on user configuration or fallback.
                # Actually, OllamaEmbeddings defaults to 'llama2' if not specified.
                # Let's stick to OLLAMA_MODEL for now, or maybe hardcode a popular one like 'nomic-embed-text' if the user has it.
                # Safe bet: use 'nomic-embed-text' as recommendation or just OLLAMA_MODEL if it supports embeddings.
                # Llava DOES NOT support embeddings usually. 
                # We should probably default to 'nomic-embed-text' or 'all-minilm'.
            )
            # Override model for embeddings if main model is vision-only like llava?
            # Let's assume user installs 'nomic-embed-text' or similar. 
            # Ideally config should specify EMBEDDING_MODEL.
            # For this iteration, let's just use "nomic-embed-text" as default for embeddings if provider is ollama.
            self.embeddings.model = "nomic-embed-text"
        else:
            self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            
        self.db = None
        self.load_index()

    def load_index(self):
        if os.path.exists(INDEX_PATH) and os.path.isdir(INDEX_PATH):
            try:
                self.db = FAISS.load_local(INDEX_PATH, self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                print(f"Failed to load index: {e}")
                self.db = None

    def save_index(self):
        if self.db:
            self.db.save_local(INDEX_PATH)

    def ingest_file(self, file_path):
        """
        Ingests a file (PDF, DOCX, TXT).
        Extracts text AND images (PDF only for now).
        Captions images.
        Updates vector store.
        """
        ext = os.path.splitext(file_path)[1].lower()
        documents = []

        if ext == ".pdf":
            documents = self._process_pdf(file_path)
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                documents = [Document(page_content=f.read(), metadata={"source": file_path})]
        # Todo: DOCX support
        
        if not documents:
            return "No content found or unsupported format."

        # Split content
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        # Add to DB
        if self.db:
            self.db.add_documents(chunks)
        else:
            self.db = FAISS.from_documents(chunks, self.embeddings)
        
        self.save_index()
        return f"Ingested {len(chunks)} chunks from {os.path.basename(file_path)}."

    def _process_pdf(self, path):
        reader = PdfReader(path)
        documents = []
        
        for i, page in enumerate(reader.pages):
            # 1. Extract Text
            text = page.extract_text()
            if text:
                documents.append(Document(page_content=text, metadata={"source": path, "page": i + 1}))
            
            # 2. Extract Images
            for image_file_object in page.images:
                try:
                    # image_file_object.name, .data
                    img = PILImage.open(io.BytesIO(image_file_object.data))
                    
                    # Generate Caption using Vision LLM
                    caption = self._caption_image(img)
                    
                    if caption:
                        content = f"[IMAGE ON PAGE {i+1}]: {caption}"
                        documents.append(Document(page_content=content, metadata={"source": path, "page": i + 1, "type": "image_caption"}))
                except Exception as e:
                    print(f"Error processing image on page {i}: {e}")
                    
        return documents

    def _caption_image(self, pil_image):
        """
        Uses the configured AI Provider to describe the image.
        """
        try:
            # Re-use our generic query service!
            # We treat this as a simple query with an image.
            description = query_assistant(
                user_text="Describe this image in detail for a technical manual.",
                image=pil_image
            )
            return description
        except Exception as e:
            print(f"Captioning error: {e}")
            return ""

    def retrieve(self, query, k=3):
        if not self.db:
            return ""
        
        docs = self.db.similarity_search(query, k=k)
        return "\n\n".join([d.page_content for d in docs])

    def clear_index(self):
        self.db = None
        if os.path.exists(INDEX_PATH):
            import shutil
            try:
                shutil.rmtree(INDEX_PATH)
                return "Index cleared successfully."
            except Exception as e:
                return f"Failed to clear index: {e}"
        return "No index found to clear."

# Singleton instance
rag_service = RAGService()
