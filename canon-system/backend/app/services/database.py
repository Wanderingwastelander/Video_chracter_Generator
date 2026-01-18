"""
Database service - SQLite with SQLAlchemy
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/canon_system.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============== MODELS ==============

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    
    # Source info
    source_type = Column(String)  # 'dndbeyond', 'manual', 'description', etc.
    source_id = Column(String)
    source_url = Column(String)
    source_data = Column(JSON)  # Raw data from source
    
    # Canon layers
    sex = Column(String, nullable=False)
    skeleton = Column(String, nullable=False)
    body_composition = Column(String, nullable=False)
    species = Column(String, nullable=False)
    
    # Reference image
    reference_image_path = Column(String)
    
    # Status
    status = Column(String, default="pending")  # pending, generating, review, approved
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assets = relationship("CharacterAsset", back_populates="character", cascade="all, delete-orphan")


class CharacterAsset(Base):
    __tablename__ = "character_assets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    
    # Asset identification
    asset_type = Column(String, nullable=False)  # 'face', 'body', 'costume'
    asset_code = Column(String, nullable=False)  # 'NEUT', 'HPPY', 'FRNT', etc.
    
    # File info
    file_path = Column(String)
    
    # Generation info
    prompt_used = Column(Text)
    generation_tool = Column(String)
    
    # Approval
    status = Column(String, default="pending")  # pending, generating, review, approved, rejected
    rejection_notes = Column(Text)
    approved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    character = relationship("Character", back_populates="assets")


class Environment(Base):
    __tablename__ = "environments"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Status
    status = Column(String, default="pending")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assets = relationship("EnvironmentAsset", back_populates="environment", cascade="all, delete-orphan")


class EnvironmentAsset(Base):
    __tablename__ = "environment_assets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    environment_id = Column(String, ForeignKey("environments.id"), nullable=False)
    
    # Asset identification
    asset_type = Column(String, nullable=False)  # 'layout', 'lighting', 'camera'
    asset_code = Column(String, nullable=False)
    
    # File info
    file_path = Column(String)
    
    # Approval
    status = Column(String, default="pending")
    rejection_notes = Column(Text)
    approved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    environment = relationship("Environment", back_populates="assets")


class ApprovalQueue(Base):
    __tablename__ = "approval_queue"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # What's being approved
    item_type = Column(String, nullable=False)  # 'character_asset', 'environment_asset'
    item_id = Column(Integer, nullable=False)
    
    # Status
    status = Column(String, default="pending")  # pending, approved, rejected
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)


class SyncLog(Base):
    __tablename__ = "sync_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String, nullable=False)  # 'push', 'pull'
    status = Column(String, nullable=False)  # 'success', 'failed'
    commit_hash = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # What's being generated
    character_id = Column(String, ForeignKey("characters.id"))
    asset_type = Column(String)  # 'face', 'body'
    asset_code = Column(String)  # 'NEUT', 'FRNT', etc.
    
    # Generation details
    prompt = Column(Text)
    tool = Column(String)  # 'stability', 'replicate', etc.
    
    # Status
    status = Column(String, default="pending")  # pending, running, completed, failed
    error_message = Column(Text)
    result_path = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


# ============== INITIALIZATION ==============

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
