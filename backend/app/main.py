# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import llm_agent, auth
from app.core.database import init_db
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# You should define this list based on where your React app is running.
# In development, it's often http://localhost:3000 or http://localhost:5173
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",  # Added for fallback port
    # Add your production domain when you deploy
]

app = FastAPI(
    title="TeamSync AI Productivity API",
    version="0.2.0",
    description="Backend API for TeamSync using FARM Stack, Gemini, SQLAlchemy, and Celery.",
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    init_db()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Allows specific origins
    allow_credentials=True,             # Allows cookies/auth headers
    allow_methods=["*"],                # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],                # Allows all headers
)

# --- Include Routers ---
app.include_router(auth.router)
app.include_router(llm_agent.router, prefix="/api/v1/agent", tags=["AI Agent & Chat"])

# --- Health Check Endpoint (Optional but Recommended) ---
@app.get("/")
async def root():
    return {"message": "TeamSync API is running!"}

# You will run the app using Uvicorn: 
# uvicorn app.main:app --reload --port 8001
