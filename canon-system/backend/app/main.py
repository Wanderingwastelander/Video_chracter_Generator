"""
Canon System - Main FastAPI Application
Character and environment consistency system for AI-generated video production
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import characters, environments, approval, generation, sync
from app.services.database import init_db

app = FastAPI(
    title="Canon System",
    description="Character and environment consistency system for AI-generated video production",
    version="1.1.0"
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving images
DATA_DIR = os.environ.get("CANON_DATA_DIR", "./data")
# Create data directory and subdirectories if they don't exist
os.makedirs(os.path.join(DATA_DIR, "characters"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "environments"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "templates"), exist_ok=True)

if os.path.exists(DATA_DIR):
    app.mount("/files", StaticFiles(directory=DATA_DIR), name="files")

# Include routers
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(environments.router, prefix="/api/environments", tags=["environments"])
app.include_router(approval.router, prefix="/api/approval", tags=["approval"])
app.include_router(generation.router, prefix="/api/generate", tags=["generation"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    return {
        "name": "Canon System",
        "version": "1.1.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
