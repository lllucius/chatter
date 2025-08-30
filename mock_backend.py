#!/usr/bin/env python3
"""
Simple Mock Backend for Chatter Frontend Testing

This provides a minimal working backend that serves the core API endpoints
needed by the frontend without requiring full dependencies.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback

try:
    from fastapi import FastAPI, HTTPException, Depends, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("FastAPI not available. This mock requires: pip install fastapi uvicorn")
    exit(1)

app = FastAPI(title="Chatter Mock Backend", version="0.1.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Simple in-memory storage
mock_users = {
    "admin": {
        "id": "1",
        "username": "admin", 
        "email": "admin@chatter.com",
        "full_name": "Administrator",
        "password": "admin",  # In real app, this would be hashed
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
    }
}

mock_tokens = {}
mock_conversations = []
mock_agents = []
mock_documents = []
mock_profiles = []
mock_prompts = []

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int = 3600

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

# Auth helper
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in mock_tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    return mock_tokens[token]

# Routes
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Chatter Mock Backend API", "status": "running"}

@app.get("/health")
async def health():
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/v1/auth/login")
async def login(user_login: UserLogin):
    """Login endpoint"""
    username = user_login.username
    password = user_login.password
    
    if username not in mock_users:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = mock_users[username]
    if user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token = str(uuid.uuid4())
    mock_tokens[token] = user
    
    return LoginResponse(
        access_token=token,
        user=UserResponse(**user),
        expires_in=3600
    )

@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(**current_user)

@app.get("/api/v1/conversations")
async def list_conversations(current_user: dict = Depends(get_current_user)):
    """List conversations"""
    return {
        "conversations": mock_conversations,
        "total": len(mock_conversations),
        "page": 1,
        "per_page": 20
    }

@app.get("/api/v1/agents")
async def list_agents(current_user: dict = Depends(get_current_user)):
    """List agents"""
    return {
        "agents": mock_agents,
        "total": len(mock_agents),
        "page": 1,
        "per_page": 20
    }

@app.get("/api/v1/documents")
async def list_documents(current_user: dict = Depends(get_current_user)):
    """List documents"""
    return {
        "documents": mock_documents,
        "total": len(mock_documents),
        "page": 1,
        "per_page": 20
    }

@app.get("/api/v1/profiles")
async def list_profiles(current_user: dict = Depends(get_current_user)):
    """List profiles"""
    return {
        "profiles": mock_profiles,
        "total": len(mock_profiles),
        "page": 1,
        "per_page": 20
    }

@app.get("/api/v1/prompts")
async def list_prompts(current_user: dict = Depends(get_current_user)):
    """List prompts"""
    return {
        "prompts": mock_prompts,
        "total": len(mock_prompts),
        "page": 1,
        "per_page": 20
    }

@app.get("/api/v1/health")
async def api_health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "cache": "connected", 
            "llm": "available"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Chatter Mock Backend...")
    print("📍 Available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🔑 Default login: admin/admin")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")