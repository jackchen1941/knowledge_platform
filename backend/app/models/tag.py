"""
Tag Model

Database model for tagging system with many-to-many relationships.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.core.database import Base

# Association table for many-to-many relationship between knowledge items and tags
knowledge_item_tags = Table(
    'knowledge_item_tags',
    Base.metadata,
    Column('knowledge_item_id', String, ForeignKey('knowledge_items.id'), primary_key=True),
    Column('tag_id', String, ForeignKey('tags.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False)
)


class Tag(Base):
    """Tag model for flexible labeling and categorization."""
    
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    description = Column(String(500))
    
    # Ownership
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Display properties
    color = Column(String(7), default="#95a5a6")  # Hex color code
    
    # Statistics
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System-generated tags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="tags")
    knowledge_items = relationship("KnowledgeItem", secondary=knowledge_item_tags, back_populates="tags")
    
    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name}, usage_count={self.usage_count})>"
    
    def increment_usage(self) -> None:
        """Increment the usage count when tag is applied to a knowledge item."""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()
    
    def decrement_usage(self) -> None:
        """Decrement the usage count when tag is removed from a knowledge item."""
        if self.usage_count > 0:
            self.usage_count -= 1
            self.updated_at = datetime.utcnow()
    
    def merge_into(self, target_tag: "Tag") -> None:
        """Merge this tag into another tag, transferring all knowledge items."""
        # Transfer all knowledge items to the target tag
        for item in self.knowledge_items:
            if target_tag not in item.tags:
                item.tags.append(target_tag)
                target_tag.increment_usage()
            item.tags.remove(self)
        
        # Mark this tag as inactive
        self.is_active = False
        self.updated_at = datetime.utcnow()