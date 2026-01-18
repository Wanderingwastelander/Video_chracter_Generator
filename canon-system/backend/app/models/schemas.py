"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============== ENUMS ==============

class Sex(str, Enum):
    MALE = "M"
    FEMALE = "F"


class Skeleton(str, Enum):
    H075 = "H075"  # Extra Small (0.75x)
    H085 = "H085"  # Small (0.85x)
    H100 = "H100"  # Medium (1.0x)
    H110 = "H110"  # Tall (1.1x)
    H120 = "H120"  # Extra Tall (1.2x)


class BodyComposition(str, Enum):
    ECTO = "ECTO"  # Ectomorph
    THIN = "THIN"  # Thin
    BASE = "BASE"  # Base/Average
    ATHL = "ATHL"  # Athletic
    HEVY = "HEVY"  # Heavy
    OVER = "OVER"  # Overweight
    OBES = "OBES"  # Obese


class Species(str, Enum):
    HUM = "HUM"  # Human
    GHO = "GHO"  # Ghoul
    MUT = "MUT"  # Mutant
    AND = "AND"  # Android
    CYB = "CYB"  # Cyborg


class FaceExpression(str, Enum):
    NEUT = "NEUT"  # Neutral
    HPPY = "HPPY"  # Happy
    SAD = "SAD"   # Sad
    ANGR = "ANGR"  # Angry
    EYEC = "EYEC"  # Eyes Closed


class BodyAngle(str, Enum):
    FRNT = "FRNT"  # Front
    Q34F = "Q34F"  # 3/4 Front
    SIDE = "SIDE"  # Side
    Q34B = "Q34B"  # 3/4 Back
    BACK = "BACK"  # Back


class AssetStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"


# ============== CHARACTER SCHEMAS ==============

class CanonLayers(BaseModel):
    sex: Sex
    skeleton: Skeleton
    body_composition: BodyComposition
    species: Species


class CharacterSource(BaseModel):
    type: str  # 'dndbeyond', 'manual', 'description'
    id: Optional[str] = None
    url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class CharacterCreate(BaseModel):
    """Input for creating a character"""
    source_url: Optional[str] = None  # D&D Beyond URL or other source
    source_type: str = "manual"
    name: Optional[str] = None
    description: Optional[str] = None
    reference_image_base64: Optional[str] = None  # Base64 encoded image


class CharacterResponse(BaseModel):
    id: str
    name: str
    source_type: Optional[str]
    source_url: Optional[str]
    sex: str
    skeleton: str
    body_composition: str
    species: str
    reference_image_path: Optional[str]
    status: str
    created_at: datetime
    modified_at: datetime
    
    class Config:
        from_attributes = True


class CharacterDetail(CharacterResponse):
    source_data: Optional[Dict[str, Any]]
    assets: List["AssetResponse"]


# ============== ASSET SCHEMAS ==============

class AssetResponse(BaseModel):
    id: int
    character_id: str
    asset_type: str
    asset_code: str
    file_path: Optional[str]
    status: str
    rejection_notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== APPROVAL SCHEMAS ==============

class ApprovalAction(BaseModel):
    """Input for approving/rejecting an asset"""
    approved: bool
    notes: Optional[str] = None


class ApprovalQueueItem(BaseModel):
    id: int
    item_type: str
    item_id: int
    status: str
    notes: Optional[str]
    created_at: datetime
    
    # Include related asset info
    asset: Optional[AssetResponse] = None
    character_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============== GENERATION SCHEMAS ==============

class GenerationRequest(BaseModel):
    """Request to generate assets for a character"""
    character_id: str
    generate_faces: bool = True
    generate_body: bool = True
    tool: str = "stability"  # Which AI tool to use


class GenerationJobResponse(BaseModel):
    id: int
    character_id: str
    asset_type: str
    asset_code: str
    status: str
    prompt: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== ENVIRONMENT SCHEMAS ==============

class EnvironmentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class EnvironmentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    modified_at: datetime
    
    class Config:
        from_attributes = True


# ============== SYNC SCHEMAS ==============

class SyncStatus(BaseModel):
    last_sync: Optional[datetime]
    pending_changes: int
    repo_url: Optional[str]


class SyncResult(BaseModel):
    success: bool
    action: str
    commit_hash: Optional[str]
    message: str


# ============== INPUT MAPPING SCHEMAS ==============

class StandardCharacterInput(BaseModel):
    """Standardized character input from any connector"""
    source: CharacterSource
    character: Dict[str, Any]
    reference_image_path: Optional[str] = None


class AutoMapResult(BaseModel):
    """Result of auto-mapping character data to canon layers"""
    layers: CanonLayers
    confidence: Dict[str, float]  # Confidence score for each layer mapping
    warnings: List[str]  # Any issues encountered


# Update forward references
CharacterDetail.model_rebuild()
