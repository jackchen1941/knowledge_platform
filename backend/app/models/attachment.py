"""
Attachment Model

Database model for file attachments associated with knowledge items.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.core.database import Base


class Attachment(Base):
    """Attachment model for files associated with knowledge items."""
    
    __tablename__ = "attachments"
    
    id = Column(String, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)
    
    # File properties
    mime_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    file_hash = Column(String(64))  # SHA-256 hash for deduplication
    
    # Image/media specific properties
    width = Column(Integer)  # For images/videos
    height = Column(Integer)  # For images/videos
    duration = Column(Integer)  # For audio/video in seconds
    
    # Relationships
    knowledge_item_id = Column(String, ForeignKey("knowledge_items.id"), nullable=False, index=True)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Status
    is_processed = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)
    
    # Relationships
    knowledge_item = relationship("KnowledgeItem", back_populates="attachments")
    uploader = relationship("User")
    
    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, filename={self.filename}, size={self.file_size})>"
    
    @property
    def file_size_human(self) -> str:
        """Return human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @property
    def is_image(self) -> bool:
        """Check if attachment is an image."""
        return self.mime_type.startswith('image/')
    
    @property
    def is_video(self) -> bool:
        """Check if attachment is a video."""
        return self.mime_type.startswith('video/')
    
    @property
    def is_audio(self) -> bool:
        """Check if attachment is audio."""
        return self.mime_type.startswith('audio/')
    
    @property
    def is_document(self) -> bool:
        """Check if attachment is a document."""
        document_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/markdown'
        ]
        return self.mime_type in document_types