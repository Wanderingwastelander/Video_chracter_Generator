"""
Environments API Routes
"""

import uuid
import shutil
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os

from ..services.database import get_db, Environment, EnvironmentAsset
from ..models.schemas import EnvironmentCreate, EnvironmentResponse

router = APIRouter()

DATA_DIR = os.environ.get("CANON_DATA_DIR", "./data")


def generate_environment_id() -> str:
    """Generate a unique environment ID"""
    return f"ENV_{uuid.uuid4().hex[:8].upper()}"


@router.get("/", response_model=List[EnvironmentResponse])
async def list_environments(db: Session = Depends(get_db)):
    """List all environments"""
    environments = db.query(Environment).all()
    return environments


@router.post("/", response_model=EnvironmentResponse)
async def create_environment(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new environment"""
    env_id = generate_environment_id()
    
    # Create directory
    env_dir = Path(DATA_DIR) / "environments" / env_id
    env_dir.mkdir(parents=True, exist_ok=True)
    (env_dir / "layouts").mkdir(exist_ok=True)
    (env_dir / "lighting").mkdir(exist_ok=True)
    (env_dir / "camera").mkdir(exist_ok=True)
    
    # Create record
    environment = Environment(
        id=env_id,
        name=name,
        description=description,
        status="pending"
    )
    
    db.add(environment)
    db.commit()
    db.refresh(environment)
    
    return environment


@router.get("/{environment_id}", response_model=EnvironmentResponse)
async def get_environment(environment_id: str, db: Session = Depends(get_db)):
    """Get environment details"""
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    return environment


@router.put("/{environment_id}", response_model=EnvironmentResponse)
async def update_environment(
    environment_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update environment details"""
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    if name:
        environment.name = name
    if description is not None:
        environment.description = description
    
    environment.modified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(environment)
    
    return environment


@router.delete("/{environment_id}")
async def delete_environment(environment_id: str, db: Session = Depends(get_db)):
    """Delete an environment"""
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    # Delete directory
    env_dir = Path(DATA_DIR) / "environments" / environment_id
    if env_dir.exists():
        shutil.rmtree(env_dir)
    
    # Delete from database
    db.delete(environment)
    db.commit()
    
    return {"status": "deleted", "id": environment_id}


@router.post("/{environment_id}/assets")
async def upload_environment_asset(
    environment_id: str,
    asset_type: str = Form(...),  # 'layout', 'lighting', 'camera'
    asset_code: str = Form(...),  # 'WIDE', 'DAY', 'CAM_A', etc.
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an asset for an environment"""
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    # Validate asset type
    valid_types = ["layout", "lighting", "camera"]
    if asset_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid asset_type. Must be one of: {valid_types}")
    
    # Save file
    env_dir = Path(DATA_DIR) / "environments" / environment_id / asset_type
    env_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = str(env_dir / f"{asset_code}.png")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create or update asset record
    existing = db.query(EnvironmentAsset).filter(
        EnvironmentAsset.environment_id == environment_id,
        EnvironmentAsset.asset_type == asset_type,
        EnvironmentAsset.asset_code == asset_code
    ).first()
    
    if existing:
        existing.file_path = file_path
        existing.status = "review"
        asset = existing
    else:
        asset = EnvironmentAsset(
            environment_id=environment_id,
            asset_type=asset_type,
            asset_code=asset_code,
            file_path=file_path,
            status="review"
        )
        db.add(asset)
    
    db.commit()
    db.refresh(asset)
    
    return {
        "id": asset.id,
        "environment_id": environment_id,
        "asset_type": asset_type,
        "asset_code": asset_code,
        "file_path": file_path,
        "status": asset.status
    }


@router.get("/{environment_id}/assets")
async def list_environment_assets(environment_id: str, db: Session = Depends(get_db)):
    """List all assets for an environment"""
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    assets = db.query(EnvironmentAsset).filter(
        EnvironmentAsset.environment_id == environment_id
    ).all()
    
    return [
        {
            "id": a.id,
            "asset_type": a.asset_type,
            "asset_code": a.asset_code,
            "file_path": a.file_path,
            "status": a.status
        }
        for a in assets
    ]
