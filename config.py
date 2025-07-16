import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Model Configuration
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    FAST_MODEL = "llama3-8b-8192"
    
    # Document Processing
    MAX_CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 300
    MAX_CONTEXTS = 8
    
    # Vector Database
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    VECTOR_DIMENSIONS = 384
    
    # Performance
    BATCH_SIZE = 50
    MAX_TOKENS = 1200
    TEMPERATURE = 0.1
    
    # UI Configuration - DocuGPT
    PAGE_TITLE = "DocuGPT - AI-Powered Document Assistant"
    PAGE_ICON = "🤖"
    
    # File Upload
    MAX_FILE_SIZE = 50  # MB
    ALLOWED_EXTENSIONS = ["pdf"]
