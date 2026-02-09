"""
Permission Model

Database model for permission-based access control.
"""

from datetime import datetime
from typing import List

from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Permission(Base):
    """Permission model for fine-grained access control."""
    
    __tablename__ = "permissions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(150), nullable=False)
    description = Column(Text)
    
    # Permission categorization
    resource = Column(String(50), nullable=False, index=True)  # e.g., 'knowledge_item', 'user', 'system'
    action = Column(String(50), nullable=False, index=True)    # e.g., 'create', 'read', 'update', 'delete'
    
    # Permission properties
    is_system = Column(Boolean, default=False, nullable=False)  # System permissions cannot be deleted
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    user_permissions = relationship("UserPermission", back_populates="permission", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name}, resource={self.resource}, action={self.action})>"


class RolePermission(Base):
    """Association table for Role-Permission many-to-many relationship."""
    
    __tablename__ = "role_permissions"
    
    role_id = Column(String, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(String, ForeignKey("permissions.id"), primary_key=True)
    
    # Grant properties
    granted = Column(Boolean, default=True, nullable=False)  # True for grant, False for explicit deny
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)  # User who granted this permission
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id}, granted={self.granted})>"


class UserRole(Base):
    """Association table for User-Role many-to-many relationship."""
    
    __tablename__ = "user_roles"
    
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    role_id = Column(String, ForeignKey("roles.id"), primary_key=True)
    
    # Assignment properties
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = Column(String, ForeignKey("users.id"), nullable=False)  # User who assigned this role
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="user_roles")
    
    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id}, is_active={self.is_active})>"


class UserPermission(Base):
    """Direct user permissions (overrides role permissions)."""
    
    __tablename__ = "user_permissions"
    
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    permission_id = Column(String, ForeignKey("permissions.id"), primary_key=True)
    
    # Grant properties
    granted = Column(Boolean, default=True, nullable=False)  # True for grant, False for explicit deny
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    granted_by = Column(String, ForeignKey("users.id"), nullable=False)  # User who granted this permission
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_permissions", foreign_keys=[user_id])
    permission = relationship("Permission", back_populates="user_permissions")
    
    def __repr__(self) -> str:
        return f"<UserPermission(user_id={self.user_id}, permission_id={self.permission_id}, granted={self.granted})>"