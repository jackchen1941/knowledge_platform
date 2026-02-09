"""
Knowledge Item Model

Database model for knowledge items (articles, notes, documents).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class KnowledgeItem(Base):
    """Knowledge item model for storing articles, notes, and documents."""
    
    __tablename__ = "knowledge_items"
    
    id = Column(String, primary_key=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="markdown", nullable=False)  # markdown, html, plain
    summary = Column(Text)  # Auto-generated or manual summary
    
    # Ownership and categorization
    author_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(String, ForeignKey("categories.id"), nullable=True, index=True)
    
    # Source information (for imported content)
    source_platform = Column(String(50))  # csdn, wechat, notion, etc.
    source_url = Column(String(1000))
    source_id = Column(String(255))  # Original ID from source platform
    
    # Status and visibility
    is_published = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    visibility = Column(String(20), default="private", nullable=False)  # private, shared, public
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime)
    deleted_at = Column(DateTime)
    
    # Metadata and statistics
    meta_data = Column(JSON, default=dict)  # Flexible metadata storage
    view_count = Column(Integer, default=0, nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    reading_time = Column(Integer, default=0, nullable=False)  # Estimated reading time in minutes
    
    # Relationships
    author = relationship("User", back_populates="knowledge_items")
    category = relationship("Category", back_populates="knowledge_items")
    attachments = relationship("Attachment", back_populates="knowledge_item", cascade="all, delete-orphan")
    versions = relationship("KnowledgeVersion", back_populates="knowledge_item", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="knowledge_item_tags", back_populates="knowledge_items")
    
    # Knowledge graph relationships
    outgoing_links = relationship(
        "KnowledgeLink",
        foreign_keys="KnowledgeLink.from_item_id",
        back_populates="from_item",
        cascade="all, delete-orphan"
    )
    incoming_links = relationship(
        "KnowledgeLink",
        foreign_keys="KnowledgeLink.to_item_id",
        back_populates="to_item",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgeItem(id={self.id}, title={self.title[:50]}...)>"
    
    def soft_delete(self) -> None:
        """Soft delete the knowledge item."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft-deleted knowledge item."""
        self.is_deleted = False
        self.deleted_at = None
    
    @property
    def is_recoverable(self) -> bool:
        """Check if the item can still be recovered (within 30 days)."""
        if not self.is_deleted or not self.deleted_at:
            return False
        days_deleted = (datetime.utcnow() - self.deleted_at).days
        return days_deleted <= 30
    
    @property
    def days_until_permanent_deletion(self) -> int:
        """Get the number of days until permanent deletion."""
        if not self.is_deleted or not self.deleted_at:
            return -1
        days_deleted = (datetime.utcnow() - self.deleted_at).days
        return max(0, 30 - days_deleted)
    
    def create_version(self, user_id: str, change_summary: Optional[str] = None, 
                      change_type: str = "edit") -> "KnowledgeVersion":
        """Create a new version snapshot of the current content."""
        import uuid
        
        # Get the next version number
        version_number = len(self.versions) + 1
        
        version = KnowledgeVersion(
            id=str(uuid.uuid4()),
            knowledge_item_id=self.id,
            version_number=version_number,
            title=self.title,
            content=self.content,
            content_type=self.content_type,
            change_summary=change_summary,
            change_type=change_type,
            created_by=user_id,
            created_at=datetime.utcnow(),
            meta_data=self.meta_data.copy() if self.meta_data else {}
        )
        
        return version


class KnowledgeVersion(Base):
    """Version history for knowledge items."""
    
    __tablename__ = "knowledge_versions"
    
    id = Column(String, primary_key=True)
    knowledge_item_id = Column(String, ForeignKey("knowledge_items.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    
    # Content snapshot
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), nullable=False)
    
    # Change information
    change_summary = Column(String(500))
    change_type = Column(String(20), default="edit")  # create, edit, restore, import
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Metadata
    meta_data = Column(JSON, default=dict)
    
    # Relationships
    knowledge_item = relationship("KnowledgeItem", back_populates="versions")
    creator = relationship("User")
    
    def __repr__(self) -> str:
        return f"<KnowledgeVersion(id={self.id}, item_id={self.knowledge_item_id}, version={self.version_number})>"
    
    def restore_to_item(self, user_id: str) -> None:
        """Restore this version's content to the knowledge item."""
        if self.knowledge_item:
            # Create a version of the current state before restoring
            self.knowledge_item.create_version(
                user_id=user_id,
                change_summary=f"Before restoring to version {self.version_number}",
                change_type="backup"
            )
            
            # Restore the content from this version
            self.knowledge_item.title = self.title
            self.knowledge_item.content = self.content
            self.knowledge_item.content_type = self.content_type
            self.knowledge_item.updated_at = datetime.utcnow()
            
            # Create a new version for the restore action
            restore_version = self.knowledge_item.create_version(
                user_id=user_id,
                change_summary=f"Restored from version {self.version_number}",
                change_type="restore"
            )
            
            return restore_version


class KnowledgeLink(Base):
    """Links between knowledge items for knowledge graph."""
    
    __tablename__ = "knowledge_links"
    
    id = Column(String, primary_key=True)
    from_item_id = Column(String, ForeignKey("knowledge_items.id"), nullable=False, index=True)
    to_item_id = Column(String, ForeignKey("knowledge_items.id"), nullable=False, index=True)
    
    # Link properties
    link_type = Column(String(50), default="reference")  # reference, related, prerequisite, etc.
    description = Column(String(500))
    strength = Column(Integer, default=1)  # Link strength for graph algorithms
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    is_bidirectional = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    from_item = relationship("KnowledgeItem", foreign_keys=[from_item_id], back_populates="outgoing_links")
    to_item = relationship("KnowledgeItem", foreign_keys=[to_item_id], back_populates="incoming_links")
    creator = relationship("User")
    
    def __repr__(self) -> str:
        return f"<KnowledgeLink(id={self.id}, from={self.from_item_id}, to={self.to_item_id}, type={self.link_type})>"