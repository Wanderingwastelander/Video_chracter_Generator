"""
Characters API Routes
"""

import os
import uuid
import base64
import shutil
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from ..services.database import get_db, Character, CharacterAsset
from ..services.auto_mapper import auto_mapper
from ..services.prompt_generator import prompt_generator
from ..connectors.dndbeyond import dndbeyond_connector
from ..models.schemas import (
    CharacterCreate,
    CharacterResponse,
    CharacterDetail,
    AssetResponse,
    CanonLayers,
    FaceExpression,
    BodyAngle
)

router = APIRouter()

DATA_DIR = os.environ.get("CANON_DATA_DIR", "./data")


def generate_character_id() -> str:
    """Generate a unique character ID"""
    return f"CHAR_{uuid.uuid4().hex[:8].upper()}"


@router.get("/", response_model=List[CharacterResponse])
async def list_characters(db: Session = Depends(get_db)):
    """List all characters"""
    characters = db.query(Character).all()
    return characters


@router.post("/", response_model=CharacterDetail)
async def create_character(
    source_url: Optional[str] = Form(None),
    source_type: str = Form("manual"),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    sex: Optional[str] = Form(None),
    height: Optional[str] = Form(None),
    reference_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create a new character
    
    Accepts either:
    - D&D Beyond URL (source_type='dndbeyond')
    - Manual entry (source_type='manual')
    - Description for AI parsing (source_type='description')
    """
    
    char_id = generate_character_id()
    char_dir = Path(DATA_DIR) / "characters" / char_id
    char_dir.mkdir(parents=True, exist_ok=True)
    
    # Handle reference image upload
    ref_image_path = None
    if reference_image:
        ref_image_path = str(char_dir / "reference_image.png")
        with open(ref_image_path, "wb") as f:
            content = await reference_image.read()
            f.write(content)
    
    # Process based on source type
    source_data = {}
    
    if source_type == "dndbeyond" and source_url:
        # Fetch from D&D Beyond
        try:
            dnd_data = await dndbeyond_connector.fetch_character(source_url)
            source_data = dnd_data
            
            # Use D&D Beyond name if not provided
            if not name and dnd_data.get("name"):
                name = dnd_data["name"]
            
            # Map to standard format
            standard_input = dndbeyond_connector.map_to_standard(dnd_data, ref_image_path)
            map_result = dndbeyond_connector.auto_map_layers(standard_input)
            
        except Exception as e:
            # Still create character but flag as needing manual entry
            source_data = {"error": str(e), "_requires_manual_entry": True}
            map_result = auto_mapper.map_from_description(
                description=description or "",
                name=name,
                sex=sex,
                height=height
            )
    else:
        # Manual or description-based
        map_result = auto_mapper.map_from_description(
            description=description or "",
            name=name,
            sex=sex,
            height=height
        )
        source_data = {
            "description": description,
            "provided_sex": sex,
            "provided_height": height
        }
    
    # Create character record
    character = Character(
        id=char_id,
        name=name or "Unnamed Character",
        source_type=source_type,
        source_id=source_data.get("id"),
        source_url=source_url,
        source_data=source_data,
        sex=map_result.layers.sex.value,
        skeleton=map_result.layers.skeleton.value,
        body_composition=map_result.layers.body_composition.value,
        species=map_result.layers.species.value,
        reference_image_path=ref_image_path,
        status="pending"
    )
    
    db.add(character)
    db.commit()
    db.refresh(character)
    
    # Create placeholder assets for all expressions and angles
    for expr in FaceExpression:
        asset = CharacterAsset(
            character_id=char_id,
            asset_type="face",
            asset_code=expr.value,
            status="pending"
        )
        db.add(asset)
    
    for angle in BodyAngle:
        asset = CharacterAsset(
            character_id=char_id,
            asset_type="body",
            asset_code=angle.value,
            status="pending"
        )
        db.add(asset)
    
    db.commit()
    db.refresh(character)
    
    return CharacterDetail(
        id=character.id,
        name=character.name,
        source_type=character.source_type,
        source_url=character.source_url,
        source_data=character.source_data,
        sex=character.sex,
        skeleton=character.skeleton,
        body_composition=character.body_composition,
        species=character.species,
        reference_image_path=character.reference_image_path,
        status=character.status,
        created_at=character.created_at,
        modified_at=character.modified_at,
        assets=[AssetResponse.model_validate(a) for a in character.assets]
    )


@router.get("/{character_id}", response_model=CharacterDetail)
async def get_character(character_id: str, db: Session = Depends(get_db)):
    """Get character details including all assets"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return CharacterDetail(
        id=character.id,
        name=character.name,
        source_type=character.source_type,
        source_url=character.source_url,
        source_data=character.source_data,
        sex=character.sex,
        skeleton=character.skeleton,
        body_composition=character.body_composition,
        species=character.species,
        reference_image_path=character.reference_image_path,
        status=character.status,
        created_at=character.created_at,
        modified_at=character.modified_at,
        assets=[AssetResponse.model_validate(a) for a in character.assets]
    )


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    name: Optional[str] = Form(None),
    sex: Optional[str] = Form(None),
    skeleton: Optional[str] = Form(None),
    body_composition: Optional[str] = Form(None),
    species: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update character details (manual layer adjustment)"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if name:
        character.name = name
    if sex:
        character.sex = sex
    if skeleton:
        character.skeleton = skeleton
    if body_composition:
        character.body_composition = body_composition
    if species:
        character.species = species
    
    character.modified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(character)
    
    return character


@router.delete("/{character_id}")
async def delete_character(character_id: str, db: Session = Depends(get_db)):
    """Delete a character and all associated assets"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Delete character directory
    char_dir = Path(DATA_DIR) / "characters" / character_id
    if char_dir.exists():
        shutil.rmtree(char_dir)
    
    # Delete from database (cascade will delete assets)
    db.delete(character)
    db.commit()
    
    return {"status": "deleted", "id": character_id}


@router.get("/{character_id}/prompts")
async def get_character_prompts(character_id: str, db: Session = Depends(get_db)):
    """Get all generated prompts for a character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    layers = CanonLayers(
        sex=character.sex,
        skeleton=character.skeleton,
        body_composition=character.body_composition,
        species=character.species
    )
    
    return {
        "character_id": character_id,
        "face_prompts": prompt_generator.generate_all_face_prompts(character.name, layers),
        "body_prompts": prompt_generator.generate_all_body_prompts(character.name, layers)
    }
