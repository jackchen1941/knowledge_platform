"""
Category Model

Database model for hierarchical categorization of knowledge items.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    """Category model for hierarchical organization of knowledge items."""
    
    __tablename__ = "categories"
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    
    # Hierarchy
    parent_id = Column(String, ForeignKey("categories.id"), nullable=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Display properties
    color = Column(String(7), default="#3498db")  # Hex color code
    icon = Column(String(50))  # Icon name or emoji
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="categories")
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    knowledge_items = relationship("KnowledgeItem", back_populates="category")
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, parent_id={self.parent_id})>"
    
    @property
    def full_path(self) -> str:
        """Get the full hierarchical path of the category."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    @property
    def depth(self) -> int:
        """Get the depth level of the category in the hierarchy."""
        if self.parent:
            return self.parent.depth + 1
        return 0
    
    def get_ancestors(self) -> list["Category"]:
        """Get all ancestor categories from root to parent."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors
    
    def get_descendants(self) -> list["Category"]:
        """Get all descendant categories recursively."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def is_ancestor_of(self, category: "Category") -> bool:
        """Check if this category is an ancestor of another category."""
        current = category.parent
        while current:
            if current.id == self.id:
                return True
            current = current.parent
        return False
    
    def is_descendant_of(self, category: "Category") -> bool:
        """Check if this category is a descendant of another category."""
        return category.is_ancestor_of(self)