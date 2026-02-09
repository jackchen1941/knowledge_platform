"""
Role Model

Database model for role-based access control.
"""

from datetime import datetime
from typing import List

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Role(Base):
    """Role model for role-based access control."""
    
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Role properties
    is_system = Column(Boolean, default=False, nullable=False)  # System roles cannot be deleted
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher priority roles override lower ones
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name}, display_name={self.display_name})>"