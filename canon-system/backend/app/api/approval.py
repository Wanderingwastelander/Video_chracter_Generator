"""
Approval API Routes
Handles the approval queue for generated assets
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..services.database import get_db, Character, CharacterAsset, ApprovalQueue
from ..models.schemas import ApprovalAction, ApprovalQueueItem, AssetResponse

router = APIRouter()


@router.get("/queue")
async def get_approval_queue(
    status: str = "pending",
    character_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get items pending approval
    
    Args:
        status: Filter by status (pending, approved, rejected)
        character_id: Filter by character
    """
    query = db.query(ApprovalQueue).filter(ApprovalQueue.status == status)
    
    items = query.order_by(ApprovalQueue.created_at.desc()).all()
    
    result = []
    for item in items:
        # Get the related asset
        if item.item_type == "character_asset":
            asset = db.query(CharacterAsset).filter(CharacterAsset.id == item.item_id).first()
            if asset:
                character = db.query(Character).filter(Character.id == asset.character_id).first()
                
                # Filter by character if specified
                if character_id and asset.character_id != character_id:
                    continue
                
                result.append({
                    "id": item.id,
                    "item_type": item.item_type,
                    "item_id": item.item_id,
                    "status": item.status,
                    "notes": item.notes,
                    "created_at": item.created_at,
                    "asset": {
                        "id": asset.id,
                        "character_id": asset.character_id,
                        "asset_type": asset.asset_type,
                        "asset_code": asset.asset_code,
                        "file_path": asset.file_path,
                        "status": asset.status,
                        "prompt_used": asset.prompt_used,
                        "rejection_notes": asset.rejection_notes
                    } if asset else None,
                    "character_name": character.name if character else None
                })
    
    return result


@router.get("/queue/{item_id}")
async def get_approval_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific approval queue item"""
    item = db.query(ApprovalQueue).filter(ApprovalQueue.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Approval item not found")
    
    # Get related asset
    asset = None
    character_name = None
    
    if item.item_type == "character_asset":
        asset = db.query(CharacterAsset).filter(CharacterAsset.id == item.item_id).first()
        if asset:
            character = db.query(Character).filter(Character.id == asset.character_id).first()
            character_name = character.name if character else None
    
    return {
        "id": item.id,
        "item_type": item.item_type,
        "item_id": item.item_id,
        "status": item.status,
        "notes": item.notes,
        "created_at": item.created_at,
        "reviewed_at": item.reviewed_at,
        "asset": {
            "id": asset.id,
            "character_id": asset.character_id,
            "asset_type": asset.asset_type,
            "asset_code": asset.asset_code,
            "file_path": asset.file_path,
            "status": asset.status,
            "prompt_used": asset.prompt_used,
            "rejection_notes": asset.rejection_notes
        } if asset else None,
        "character_name": character_name
    }


@router.post("/approve/{item_id}")
async def approve_item(
    item_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Approve an item in the queue"""
    item = db.query(ApprovalQueue).filter(ApprovalQueue.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Approval item not found")
    
    if item.status != "pending":
        raise HTTPException(status_code=400, detail=f"Item already {item.status}")
    
    # Update queue item
    item.status = "approved"
    item.notes = notes
    item.reviewed_at = datetime.utcnow()
    
    # Update the related asset
    if item.item_type == "character_asset":
        asset = db.query(CharacterAsset).filter(CharacterAsset.id == item.item_id).first()
        if asset:
            asset.status = "approved"
            asset.approved_at = datetime.utcnow()
            
            # Check if all assets for this character are approved
            character = db.query(Character).filter(Character.id == asset.character_id).first()
            if character:
                all_assets = db.query(CharacterAsset).filter(
                    CharacterAsset.character_id == character.id
                ).all()
                
                all_approved = all(a.status == "approved" for a in all_assets)
                if all_approved:
                    character.status = "approved"
    
    db.commit()
    
    return {
        "status": "approved",
        "item_id": item_id,
        "message": "Item approved successfully"
    }


@router.post("/reject/{item_id}")
async def reject_item(
    item_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Reject an item in the queue
    
    Provide notes to guide regeneration.
    """
    item = db.query(ApprovalQueue).filter(ApprovalQueue.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Approval item not found")
    
    if item.status != "pending":
        raise HTTPException(status_code=400, detail=f"Item already {item.status}")
    
    # Update queue item
    item.status = "rejected"
    item.notes = notes
    item.reviewed_at = datetime.utcnow()
    
    # Update the related asset
    asset_id = None
    if item.item_type == "character_asset":
        asset = db.query(CharacterAsset).filter(CharacterAsset.id == item.item_id).first()
        if asset:
            asset.status = "rejected"
            asset.rejection_notes = notes
            asset_id = asset.id
            
            # Update character status
            character = db.query(Character).filter(Character.id == asset.character_id).first()
            if character:
                character.status = "review"
    
    db.commit()
    
    return {
        "status": "rejected",
        "item_id": item_id,
        "asset_id": asset_id,
        "message": "Item rejected. Use /api/generate/regenerate/{asset_id} to regenerate with feedback.",
        "notes": notes
    }


@router.get("/stats")
async def get_approval_stats(db: Session = Depends(get_db)):
    """Get approval queue statistics"""
    pending = db.query(ApprovalQueue).filter(ApprovalQueue.status == "pending").count()
    approved = db.query(ApprovalQueue).filter(ApprovalQueue.status == "approved").count()
    rejected = db.query(ApprovalQueue).filter(ApprovalQueue.status == "rejected").count()
    
    return {
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "total": pending + approved + rejected
    }


@router.post("/bulk-approve")
async def bulk_approve(
    item_ids: List[int],
    db: Session = Depends(get_db)
):
    """Approve multiple items at once"""
    approved_count = 0
    
    for item_id in item_ids:
        item = db.query(ApprovalQueue).filter(ApprovalQueue.id == item_id).first()
        
        if item and item.status == "pending":
            item.status = "approved"
            item.reviewed_at = datetime.utcnow()
            
            if item.item_type == "character_asset":
                asset = db.query(CharacterAsset).filter(CharacterAsset.id == item.item_id).first()
                if asset:
                    asset.status = "approved"
                    asset.approved_at = datetime.utcnow()
            
            approved_count += 1
    
    db.commit()
    
    return {
        "approved": approved_count,
        "total_requested": len(item_ids)
    }
