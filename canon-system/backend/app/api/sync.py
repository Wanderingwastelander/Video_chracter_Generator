"""
Sync API Routes
Handles GitHub backup and sync
"""

import os
import subprocess
from datetime import datetime
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..services.database import get_db, SyncLog

router = APIRouter()

DATA_DIR = os.environ.get("CANON_DATA_DIR", "./data")
REPO_URL = os.environ.get("CANON_GITHUB_REPO", "")


def run_git_command(args: list, cwd: str = None) -> tuple:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or DATA_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


@router.get("/status")
async def get_sync_status(db: Session = Depends(get_db)):
    """Get current sync status"""
    # Check if git is initialized
    git_dir = Path(DATA_DIR) / ".git"
    is_git_repo = git_dir.exists()
    
    # Get last sync
    last_sync = db.query(SyncLog).filter(
        SyncLog.status == "success"
    ).order_by(SyncLog.created_at.desc()).first()
    
    # Check for uncommitted changes
    pending_changes = 0
    if is_git_repo:
        success, output = run_git_command(["status", "--porcelain"])
        if success:
            pending_changes = len([l for l in output.strip().split("\n") if l])
    
    # Get remote URL
    remote_url = None
    if is_git_repo:
        success, output = run_git_command(["remote", "get-url", "origin"])
        if success:
            remote_url = output.strip()
    
    return {
        "is_git_repo": is_git_repo,
        "remote_url": remote_url or REPO_URL,
        "last_sync": last_sync.created_at if last_sync else None,
        "last_commit": last_sync.commit_hash if last_sync else None,
        "pending_changes": pending_changes
    }


@router.post("/init")
async def init_repo(
    remote_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Initialize git repository"""
    repo_url = remote_url or REPO_URL
    
    if not repo_url:
        raise HTTPException(
            status_code=400,
            detail="No repository URL provided. Set CANON_GITHUB_REPO env var or provide remote_url."
        )
    
    # Check if already initialized
    git_dir = Path(DATA_DIR) / ".git"
    if git_dir.exists():
        return {"status": "already_initialized", "remote_url": repo_url}
    
    # Initialize
    success, output = run_git_command(["init"])
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to init: {output}")
    
    # Add remote
    success, output = run_git_command(["remote", "add", "origin", repo_url])
    if not success and "already exists" not in output:
        raise HTTPException(status_code=500, detail=f"Failed to add remote: {output}")
    
    # Create .gitignore
    gitignore_path = Path(DATA_DIR) / ".gitignore"
    gitignore_content = """
# Python
__pycache__/
*.pyc
.env

# Database
*.db-journal

# Temporary files
*.tmp
*.temp

# OS files
.DS_Store
Thumbs.db
"""
    gitignore_path.write_text(gitignore_content)
    
    # Initial commit
    run_git_command(["add", "."])
    success, output = run_git_command(["commit", "-m", "Initial commit - Canon System"])
    
    # Log
    log = SyncLog(
        action="init",
        status="success" if success else "failed",
        details=output
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "initialized",
        "remote_url": repo_url,
        "message": output
    }


@router.post("/push")
async def push_changes(
    message: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Commit and push changes to GitHub"""
    git_dir = Path(DATA_DIR) / ".git"
    if not git_dir.exists():
        raise HTTPException(status_code=400, detail="Git not initialized. Call /api/sync/init first.")
    
    # Stage all changes
    success, output = run_git_command(["add", "."])
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to stage: {output}")
    
    # Check if there are changes
    success, status_output = run_git_command(["status", "--porcelain"])
    if not status_output.strip():
        return {"status": "no_changes", "message": "Nothing to commit"}
    
    # Commit
    commit_message = message or f"Canon System auto-sync - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    success, output = run_git_command(["commit", "-m", commit_message])
    if not success and "nothing to commit" not in output:
        raise HTTPException(status_code=500, detail=f"Failed to commit: {output}")
    
    # Get commit hash
    success, hash_output = run_git_command(["rev-parse", "HEAD"])
    commit_hash = hash_output.strip() if success else None
    
    # Push
    success, output = run_git_command(["push", "-u", "origin", "main"])
    if not success:
        # Try master branch
        success, output = run_git_command(["push", "-u", "origin", "master"])
    
    # Log
    log = SyncLog(
        action="push",
        status="success" if success else "failed",
        commit_hash=commit_hash,
        details=output
    )
    db.add(log)
    db.commit()
    
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to push: {output}")
    
    return {
        "status": "success",
        "commit_hash": commit_hash,
        "message": commit_message
    }


@router.post("/pull")
async def pull_changes(db: Session = Depends(get_db)):
    """Pull changes from GitHub"""
    git_dir = Path(DATA_DIR) / ".git"
    if not git_dir.exists():
        raise HTTPException(status_code=400, detail="Git not initialized. Call /api/sync/init first.")
    
    # Pull
    success, output = run_git_command(["pull", "origin", "main"])
    if not success:
        # Try master branch
        success, output = run_git_command(["pull", "origin", "master"])
    
    # Get current commit
    _, hash_output = run_git_command(["rev-parse", "HEAD"])
    commit_hash = hash_output.strip()
    
    # Log
    log = SyncLog(
        action="pull",
        status="success" if success else "failed",
        commit_hash=commit_hash,
        details=output
    )
    db.add(log)
    db.commit()
    
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to pull: {output}")
    
    return {
        "status": "success",
        "commit_hash": commit_hash,
        "message": output
    }


@router.get("/log")
async def get_sync_log(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get sync history"""
    logs = db.query(SyncLog).order_by(SyncLog.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "action": log.action,
            "status": log.status,
            "commit_hash": log.commit_hash,
            "details": log.details,
            "created_at": log.created_at
        }
        for log in logs
    ]
