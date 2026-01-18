"""
Generation API Routes
Handles AI image generation for character assets
"""

import os
import asyncio
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from ..services.database import get_db, Character, CharacterAsset, GenerationJob, ApprovalQueue
from ..services.prompt_generator import prompt_generator
from ..services.image_generator import image_generation_service
from ..models.schemas import (
    GenerationRequest,
    GenerationJobResponse,
    CanonLayers,
    FaceExpression,
    BodyAngle
)

router = APIRouter()

DATA_DIR = os.environ.get("CANON_DATA_DIR", "./data")


async def run_generation_job(
    job_id: int,
    character_id: str,
    asset_type: str,
    asset_code: str,
    prompt: str,
    reference_image_path: Optional[str],
    output_path: str,
    generator: str,
    db_url: str
):
    """Background task to run image generation"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Update job status
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Run generation
        result_path = await image_generation_service.generate(
            prompt=prompt,
            generator=generator,
            reference_image_path=reference_image_path,
            output_path=output_path
        )
        
        # Update job as completed
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.result_path = result_path
        
        # Update the asset
        asset = db.query(CharacterAsset).filter(
            CharacterAsset.character_id == character_id,
            CharacterAsset.asset_type == asset_type,
            CharacterAsset.asset_code == asset_code
        ).first()
        
        if asset:
            asset.file_path = result_path
            asset.status = "review"
            asset.prompt_used = prompt
            asset.generation_tool = generator
            
            # Add to approval queue
            approval_item = ApprovalQueue(
                item_type="character_asset",
                item_id=asset.id,
                status="pending"
            )
            db.add(approval_item)
        
        db.commit()
        
    except Exception as e:
        # Update job as failed
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()


@router.get("/generators")
async def list_generators():
    """List available image generators"""
    return {
        "available": image_generation_service.get_available_generators(),
        "default": "mock"
    }


@router.post("/character/{character_id}")
async def generate_character_assets(
    character_id: str,
    generate_faces: bool = True,
    generate_body: bool = True,
    generator: str = "mock",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Generate all assets for a character
    
    This queues generation jobs for all face expressions and body angles.
    Jobs run in the background and results go to the approval queue.
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Validate generator
    available = image_generation_service.get_available_generators()
    if generator not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Generator '{generator}' not available. Available: {available}"
        )
    
    # Build canon layers
    layers = CanonLayers(
        sex=character.sex,
        skeleton=character.skeleton,
        body_composition=character.body_composition,
        species=character.species
    )
    
    # Create output directory
    char_dir = Path(DATA_DIR) / "characters" / character_id
    char_dir.mkdir(parents=True, exist_ok=True)
    (char_dir / "face").mkdir(exist_ok=True)
    (char_dir / "body").mkdir(exist_ok=True)
    
    jobs_created = []
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./data/canon_system.db")
    
    # Generate face expressions
    if generate_faces:
        face_prompts = prompt_generator.generate_all_face_prompts(character.name, layers)
        
        for expr_code, prompt in face_prompts.items():
            output_path = str(char_dir / "face" / f"{expr_code}.png")
            
            # Create job record
            job = GenerationJob(
                character_id=character_id,
                asset_type="face",
                asset_code=expr_code,
                prompt=prompt,
                tool=generator,
                status="pending"
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            
            jobs_created.append({
                "id": job.id,
                "type": "face",
                "code": expr_code
            })
            
            # Queue background task
            if background_tasks:
                background_tasks.add_task(
                    run_generation_job,
                    job.id,
                    character_id,
                    "face",
                    expr_code,
                    prompt,
                    character.reference_image_path,
                    output_path,
                    generator,
                    db_url
                )
    
    # Generate body angles
    if generate_body:
        body_prompts = prompt_generator.generate_all_body_prompts(character.name, layers)
        
        for angle_code, prompt in body_prompts.items():
            output_path = str(char_dir / "body" / f"{angle_code}.png")
            
            # Create job record
            job = GenerationJob(
                character_id=character_id,
                asset_type="body",
                asset_code=angle_code,
                prompt=prompt,
                tool=generator,
                status="pending"
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            
            jobs_created.append({
                "id": job.id,
                "type": "body",
                "code": angle_code
            })
            
            # Queue background task
            if background_tasks:
                background_tasks.add_task(
                    run_generation_job,
                    job.id,
                    character_id,
                    "body",
                    angle_code,
                    prompt,
                    character.reference_image_path,
                    output_path,
                    generator,
                    db_url
                )
    
    # Update character status
    character.status = "generating"
    db.commit()
    
    return {
        "character_id": character_id,
        "generator": generator,
        "jobs_queued": len(jobs_created),
        "jobs": jobs_created,
        "message": "Generation jobs queued. Check approval queue for results."
    }


@router.get("/jobs")
async def list_generation_jobs(
    status: Optional[str] = None,
    character_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List generation jobs with optional filters"""
    query = db.query(GenerationJob)
    
    if status:
        query = query.filter(GenerationJob.status == status)
    if character_id:
        query = query.filter(GenerationJob.character_id == character_id)
    
    jobs = query.order_by(GenerationJob.created_at.desc()).all()
    
    return [GenerationJobResponse.model_validate(j) for j in jobs]


@router.get("/jobs/{job_id}", response_model=GenerationJobResponse)
async def get_generation_job(job_id: int, db: Session = Depends(get_db)):
    """Get details of a specific generation job"""
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.post("/regenerate/{asset_id}")
async def regenerate_asset(
    asset_id: int,
    feedback: Optional[str] = None,
    generator: str = "mock",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Regenerate a specific asset (after rejection)
    
    Optionally include feedback to adjust the prompt.
    """
    asset = db.query(CharacterAsset).filter(CharacterAsset.id == asset_id).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    character = db.query(Character).filter(Character.id == asset.character_id).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Build layers
    layers = CanonLayers(
        sex=character.sex,
        skeleton=character.skeleton,
        body_composition=character.body_composition,
        species=character.species
    )
    
    # Generate new prompt
    if asset.asset_type == "face":
        prompt = prompt_generator.generate_face_prompt(
            character.name,
            layers,
            FaceExpression(asset.asset_code)
        )
    else:
        prompt = prompt_generator.generate_body_prompt(
            character.name,
            layers,
            BodyAngle(asset.asset_code)
        )
    
    # Add feedback to prompt if provided
    if feedback:
        prompt += f"\n\nAdditional guidance: {feedback}"
    
    # Create output path
    char_dir = Path(DATA_DIR) / "characters" / character.id
    output_path = str(char_dir / asset.asset_type / f"{asset.asset_code}.png")
    
    # Create job
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./data/canon_system.db")
    
    job = GenerationJob(
        character_id=character.id,
        asset_type=asset.asset_type,
        asset_code=asset.asset_code,
        prompt=prompt,
        tool=generator,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Update asset status
    asset.status = "generating"
    db.commit()
    
    # Queue background task
    if background_tasks:
        background_tasks.add_task(
            run_generation_job,
            job.id,
            character.id,
            asset.asset_type,
            asset.asset_code,
            prompt,
            character.reference_image_path,
            output_path,
            generator,
            db_url
        )
    
    return {
        "job_id": job.id,
        "asset_id": asset_id,
        "message": "Regeneration job queued"
    }
