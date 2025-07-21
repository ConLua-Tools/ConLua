from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import os
import zipfile
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# LOCAL FILE FROM REPO
from lib.cloudflareWorker import CloudflareWorker
from lib.pydantic_filters import UserRegister, UserLogin, QuestionRequest, CustomAIRequest, QuestionResponse, FileUploadResponse
from lib.SimpleKnowledgeStore import SimpleKnowledgeStore
from lib.lightrag_extensions import MyLightRAG
from lib.backRetrieval import backRetrieval

load_dotenv(dotenv_path=Path(__file__).parent / '.env')
# Configuration
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY", "INSERT API KEY")
API_BASE_URL = os.getenv("CLOUDFLARE_API_BASE_URL", "INSERT YOUR API BASE URL")
LLM_MODEL = os.getenv("LLM_MODEL", "INSERT YOUR LLM MODEL HERE")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "INSERT YOUR EMBEDDING MODEL")
WORKING_DIR = os.getenv("WORKING_DIR", "INSERT YOUR WORKING DIR")
USER_DATA_DIR = os.getenv("USER_DATA_IDR", "INSERT YOUR USER DATA DIR HERE")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this")

# Initialize FastAPI
app = FastAPI(title="YourAI Multi-Model API", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global instances
cloudflare_worker = None
fire_safety_store = None
user_knowledge_manager = None
users_db: Dict[str, dict] = {}
user_ais: Dict[str, List[dict]] = {}

# Initialize system
# WE NEED TO FIX THIS
async def initialize_system():
    global cloudflare_worker, fire_safety_store, user_knowledge_manager

    print("🔄 Initializing YourAI System...")

    # Initialize Cloudflare worker
    cloudflare_worker = CloudflareWorker(
        cloudflare_api_key=CLOUDFLARE_API_KEY,
        api_base_url=API_BASE_URL,
        llm_model_name=LLM_MODEL,
        embedding_model_name=EMBEDDING_MODEL,
    )

    # Initialize fire safety knowledge store (from existing dickens data)
    dickens_path = Path(WORKING_DIR)
    has_data = dickens_path.exists() and len(list(dickens_path.glob("*.json"))) > 0

    if not has_data:
        print(f"⚠️ Download failed: {e}")
        os.makedirs(WORKING_DIR, exist_ok=True)

    fire_safety_store = SimpleKnowledgeStore(WORKING_DIR)

    print("YourAI System ready!")

# API Endpoints
@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_system()   # equivalent to startup
    yield

@app.get("/")
async def root():
    return {"message": "YourAI Multi-Model API", "status": "running", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models": ["fire-safety", "general", "physics", "custom"],
        "users_count": len(users_db),
        "active_custom_ais": sum(len(ais) for ais in user_ais.values()),
        "fire_safety_chunks": len(fire_safety_store.chunks) if fire_safety_store else 0
    }

# Legacy endpoints
@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Legacy endpoint for fire safety questions"""
    if not cloudflare_worker or not fire_safety_store:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        print(f"🔥 Fire Safety AI processing: {request.question}")

        # Search for relevant context in fire safety knowledge
        relevant_chunks = fire_safety_store.search(request.question, limit=3)
        context = "\n".join(relevant_chunks) if relevant_chunks else "No specific context found."

        system_prompt = """You are a Fire Safety AI Assistant specializing in fire safety regulations. 
        Use the provided context to answer questions about building codes, emergency exits, and fire safety requirements."""

        user_prompt = f"""Context: {context}

Question: {request.question}

Please provide a helpful answer based on the context about fire safety regulations."""

        response = await cloudflare_worker.query(user_prompt, system_prompt)
        return QuestionResponse(answer=response, mode=request.mode, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/view_source", response_model=QuestionResponse)
async def view_source(request: QuestionRequest):
    cloudflare_worker = CloudflareWorker(
        cloudflare_api_key=CLOUDFLARE_API_KEY,
        api_base_url=API_BASE_URL,
        llm_model_name=LLM_MODEL,
    )
    back_retrieval = backRetrieval(keyword_generator=lambda user_prompt: cloudflare_worker.query(user_prompt))
    back_retrieval.load_regulations()

from docx import Document

@app.post("/upload_doc", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    # Read DOCX file content
    file_content = await file.read()

    # Save temporarily to read with python-docx
    temp_path = "/tmp/uploaded.docx"
    with open(temp_path, "wb") as temp_file:
        temp_file.write(file_content)

    # Convert DOCX to plain text
    doc = Document(temp_path)
    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    plain_text = "\n".join(paragraphs)

    # Optional: Remove the temporary file if needed
    # os.remove(temp_path)

    # Proceed with plain text
    lightrag_instance = MyLightRAG()
    await lightrag_instance.createKG(plain_text)

    return FileUploadResponse(
        filename=file.filename,
        size=len(file_content),
        message="DOCX converted to text and processed successfully."
    )

@app.get("/modes")
async def get_available_modes():
    return {
        "modes": [
            {"name": "hybrid", "description": "Combined approach (recommended)"},
            {"name": "local", "description": "Search specific document sections"},
            {"name": "global", "description": "Look at overall document themes"},
            {"name": "naive", "description": "Simple text search"}
        ]
    }

@app.get("/examples")
async def get_example_questions():
    return {
        "examples": [
            "What are the requirements for emergency exits?",
            "How many exits does a building need?",
            "What are fire safety rules for stairwells?",
            "What are building safety requirements?",
            "What are the fire safety regulations for high-rise buildings?",
            "What are the requirements for fire doors?",
            "How should evacuation routes be designed?"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
