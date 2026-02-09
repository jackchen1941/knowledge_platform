"""
User Model

Database model for user authentication and profile management.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(Text)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    # User preferences and settings
    preferences = Column(JSON, default=dict)
    
    # Relationships
    knowledge_items = relationship("KnowledgeItem", back_populates="author", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
    import_configs = relationship("ImportConfig", back_populates="user", cascade="all, delete-orphan")
    sync_devices = relationship("SyncDevice", back_populates="user", cascade="all, delete-orphan")
    
    # Role and Permission relationships
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", foreign_keys="[UserRole.user_id]")
    user_permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan", foreign_keys="[UserPermission.user_id]")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"