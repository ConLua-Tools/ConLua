from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import requests
import json
import os
import zipfile
import hashlib
import uuid
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
import jwt

from cloudflareWorker import CloudflareWorker # LOCAL FILE FROM REPO

# Simple knowledge store that loads your RAG data
class SimpleKnowledgeStore:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.chunks = []
        self.entities = []
        self.load_data()
    
    def load_data(self):
        try:
            # Load text chunks
            chunks_file = Path(self.data_dir) / "kv_store_text_chunks.json"
            if chunks_file.exists():
                with open(chunks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chunks = list(data.values()) if data else []
            
            # Load custom knowledge if exists
            knowledge_file = Path(self.data_dir) / "knowledge.json"
            if knowledge_file.exists():
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'chunks' in data:
                        self.chunks = data['chunks']
            
            # Load entities
            entities_file = Path(self.data_dir) / "vdb_entities.json"
            if entities_file.exists():
                with open(entities_file, 'r', encoding='utf-8') as f:
                    entities_data = json.load(f)
                    if isinstance(entities_data, dict) and 'data' in entities_data:
                        self.entities = entities_data['data']
                    elif isinstance(entities_data, list):
                        self.entities = entities_data
                    else:
                        self.entities = []
                    
            print(f"✅ Loaded {len(self.chunks)} chunks and {len(self.entities)} entities")
            
        except Exception as e:
            print(f"⚠️ Error loading data: {e}")
            self.chunks = []
            self.entities = []
    
    def search(self, query: str, limit: int = 5) -> List[str]:
        query_lower = query.lower()
        results = []
        
        # Search through chunks
        for chunk in self.chunks:
            if isinstance(chunk, str):
                if any(word in chunk.lower() for word in query_lower.split()):
                    results.append(chunk)
            elif isinstance(chunk, dict) and 'content' in chunk:
                content = chunk['content']
                if any(word in content.lower() for word in query_lower.split()):
                    results.append(content)
        
        # Search through entities
        for entity in self.entities:
            if isinstance(entity, dict):
                entity_text = json.dumps(entity, ensure_ascii=False)
                if any(word in entity_text.lower() for word in query_lower.split()):
                    results.append(entity_text)
        
        return results[:limit]

# Configuration
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY", "INSERT API KEY")
API_BASE_URL = os.getenv("CLOUDFLARE_API_BASE_URL", "INSERT YOUR API BASE URL")
LLM_MODEL = os.getenv("LLM_MODEL", "INSERT YOUR LLM MODEL HERE")
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

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    name: str

class UserLogin(BaseModel):
    email: EmailStr

class QuestionRequest(BaseModel):
    question: str
    mode: str = "hybrid"

class CustomAIRequest(BaseModel):
    name: str
    description: str

class QuestionResponse(BaseModel):
    answer: str
    mode: str
    status: str

class FileUploadResponse(BaseModel):
    filename: str
    size: int
    message: str

# Helper functions
def create_jwt_token(user_data: dict) -> str:
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user_id = payload["user_id"]
    
    if user_id not in [user["id"] for user in users_db.values()]:
        raise HTTPException(status_code=401, detail="User not found")
    
    return next(user for user in users_db.values() if user["id"] == user_id)

def hash_email(email: str) -> str:
    return hashlib.md5(email.encode()).hexdigest()[:12]

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
    )
    
    # Initialize fire safety knowledge store (from existing dickens data)
    dickens_path = Path(WORKING_DIR)
    has_data = dickens_path.exists() and len(list(dickens_path.glob("*.json"))) > 0
    
    if not has_data:
        print("📥 Downloading RAG database...")
        try:
            # Use the same download logic as your original app.py
            data_url = "https://github.com/YOUR_USERNAME/fire-safety-ai/releases/download/v1.0-data/dickens.zip"
            
            print(f"Downloading from: {data_url}")
            response = requests.get(data_url, timeout=60)
            response.raise_for_status()
            
            with open("dickens.zip", "wb") as f:
                f.write(response.content)
            
            with zipfile.ZipFile("dickens.zip", 'r') as zip_ref:
                zip_ref.extractall(".")
            
            os.remove("dickens.zip")
            print("Data downloaded!")
            
        except Exception as e:
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

# Authentication endpoints
@app.post("/auth/register")
async def register_user(user_data: UserRegister):
    user_id = hash_email(user_data.email)
    
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "created_at": datetime.now().isoformat()
    }
    
    users_db[user_data.email] = user
    user_ais[user_id] = []
    
    token = create_jwt_token(user)
    
    return {
        "user": user,
        "token": token,
        "message": "User registered successfully"
    }

@app.post("/auth/login")
async def login_user(login_data: UserLogin):
    if login_data.email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[login_data.email]
    token = create_jwt_token(user)
    
    return {
        "user": user,
        "token": token,
        "message": "Login successful"
    }

# File upload for custom AI
# Chat endpoints for different models
@app.post("/chat/fire-safety", response_model=QuestionResponse)
async def chat_fire_safety(request: QuestionRequest):
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

@app.post("/chat/general", response_model=QuestionResponse)
async def chat_general(request: QuestionRequest):
    if not cloudflare_worker:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    system_prompt = """You are a helpful general AI assistant. Provide accurate, helpful, and engaging responses to user questions."""
    
    try:
        response = await cloudflare_worker.query(request.question, system_prompt)
        return QuestionResponse(answer=response, mode=request.mode, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/chat/custom/{ai_id}", response_model=QuestionResponse)
async def chat_custom_ai(
    ai_id: str,
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    if not cloudflare_worker or not user_knowledge_manager:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    user_id = current_user["id"]
    
    # Find the AI
    user_ai_list = user_ais.get(user_id, [])
    ai_info = next((ai for ai in user_ai_list if ai["id"] == ai_id), None)
    
    if not ai_info:
        raise HTTPException(status_code=404, detail="Custom AI not found")
    
    try:
        # Get the knowledge store for this custom AI
        custom_store = user_knowledge_manager.get_user_store(user_id, ai_id)
        
        # Search for relevant context
        relevant_chunks = custom_store.search(request.question, limit=3)
        context = "\n".join(relevant_chunks) if relevant_chunks else "No specific context found."
        
        system_prompt = f"""You are {ai_info['name']}, a custom AI assistant. {ai_info['description']}
        Use the provided context from the uploaded knowledge base to answer questions accurately."""
        
        user_prompt = f"""Context: {context}

Question: {request.question}

Please provide a helpful answer based on the uploaded knowledge base."""
        
        response = await cloudflare_worker.query(user_prompt, system_prompt)
        return QuestionResponse(answer=response, mode=request.mode, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Legacy endpoints (for compatibility with your existing frontend)
@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Legacy endpoint that routes to fire safety chat"""
    return await chat_fire_safety(request)

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
