"""
Attachment Service

Business logic for file attachment management including upload, storage,
processing, and retrieval.
"""

import hashlib
import mimetypes
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, BinaryIO

from PIL import Image
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, PermissionError, ValidationError
from app.models.attachment import Attachment
from app.models.knowledge import KnowledgeItem
from app.schemas.attachment import (
    AttachmentCreate,
    AttachmentUpdate,
    AttachmentResponse,
    AttachmentListResponse,
    AttachmentStats
)

settings = get_settings()


class AttachmentService:
    """Service for managing file attachments."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_types = settings.ALLOWED_FILE_TYPES
        
        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different file types
        for subdir in ['images', 'videos', 'audio', 'documents', 'others', 'thumbnails']:
            (self.upload_dir / subdir).mkdir(exist_ok=True)
    
    def _get_file_category(self, mime_type: str) -> str:
        """Determine file category from MIME type."""
        if mime_type.startswith('image/'):
            return 'images'
        elif mime_type.startswith('video/'):
            return 'videos'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type in [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/markdown'
        ]:
            return 'documents'
        else:
            return 'others'
    
    def _validate_file(self, filename: str, file_size: int, mime_type: str) -> None:
        """Validate file before upload."""
        # Check file size
        if file_size > self.max_file_size:
            max_size_mb = self.max_file_size / (1024 * 1024)
            raise ValidationError(
                f"File size exceeds maximum allowed size of {max_size_mb}MB"
            )
        
        # Check MIME type
        if mime_type not in self.allowed_types:
            raise ValidationError(
                f"File type '{mime_type}' is not allowed. "
                f"Allowed types: {', '.join(self.allowed_types)}"
            )
        
        # Check filename
        if not filename or len(filename) > 255:
            raise ValidationError("Invalid filename")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent security issues."""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Replace unsafe characters
        unsafe_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        return filename
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename."""
        sanitized = self._sanitize_filename(original_filename)
        name, ext = os.path.splitext(sanitized)
        unique_id = str(uuid.uuid4())[:8]
        return f"{name}_{unique_id}{ext}"
    
    def _get_image_dimensions(self, file_path: Path) -> Optional[Tuple[int, int]]:
        """Get image dimensions."""
        try:
            with Image.open(file_path) as img:
                return img.size
        except Exception:
            return None
    
    def _generate_thumbnail(self, file_path: Path, attachment_id: str) -> Optional[str]:
        """Generate thumbnail for images."""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail (max 300x300)
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumbnail_filename = f"thumb_{attachment_id}.jpg"
                thumbnail_path = self.upload_dir / 'thumbnails' / thumbnail_filename
                img.save(thumbnail_path, 'JPEG', quality=85)
                
                return str(thumbnail_path.relative_to(self.upload_dir))
        except Exception as e:
            print(f"Failed to generate thumbnail: {e}")
            return None
    
    async def _check_duplicate(self, file_hash: str, user_id: str) -> Optional[Attachment]:
        """Check if file with same hash already exists for user."""
        query = select(Attachment).where(
            and_(
                Attachment.file_hash == file_hash,
                Attachment.uploaded_by == user_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _verify_knowledge_item_access(
        self, 
        knowledge_item_id: str, 
        user_id: str
    ) -> KnowledgeItem:
        """Verify user has access to the knowledge item."""
        query = select(KnowledgeItem).where(KnowledgeItem.id == knowledge_item_id)
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundError(f"Knowledge item {knowledge_item_id} not found")
        
        if item.author_id != user_id:
            raise PermissionError("You don't have permission to add attachments to this item")
        
        return item
    
    async def upload_file(
        self,
        user_id: str,
        knowledge_item_id: str,
        file: BinaryIO,
        filename: str,
        mime_type: Optional[str] = None
    ) -> Tuple[AttachmentResponse, bool, Optional[str]]:
        """
        Upload a file and create attachment record.
        
        Returns:
            Tuple of (attachment, is_duplicate, duplicate_of_id)
        """
        # Verify access to knowledge item
        await self._verify_knowledge_item_access(knowledge_item_id, user_id)
        
        # Detect MIME type if not provided
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = 'application/octet-stream'
        
        # Get file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        # Validate file
        self._validate_file(filename, file_size, mime_type)
        
        # Determine file category and generate unique filename
        category = self._get_file_category(mime_type)
        unique_filename = self._generate_unique_filename(filename)
        
        # Save file temporarily to calculate hash
        temp_path = self.upload_dir / 'temp' / unique_filename
        temp_path.parent.mkdir(exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            shutil.copyfileobj(file, f)
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(temp_path)
        
        # Check for duplicates
        duplicate = await self._check_duplicate(file_hash, user_id)
        if duplicate:
            # Remove temp file
            temp_path.unlink()
            
            # Return existing attachment
            response = AttachmentResponse.model_validate(duplicate)
            return response, True, duplicate.id
        
        # Move file to final location
        final_path = self.upload_dir / category / unique_filename
        shutil.move(str(temp_path), str(final_path))
        
        # Get image dimensions if applicable
        width, height = None, None
        if mime_type.startswith('image/'):
            dimensions = self._get_image_dimensions(final_path)
            if dimensions:
                width, height = dimensions
        
        # Create attachment record
        attachment_id = str(uuid.uuid4())
        attachment = Attachment(
            id=attachment_id,
            filename=self._sanitize_filename(filename),
            original_filename=filename,
            file_path=str(final_path.relative_to(self.upload_dir)),
            mime_type=mime_type,
            file_size=file_size,
            file_hash=file_hash,
            width=width,
            height=height,
            knowledge_item_id=knowledge_item_id,
            uploaded_by=user_id,
            is_processed=False,
            uploaded_at=datetime.utcnow()
        )
        
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        
        # Generate thumbnail for images (async in background would be better)
        if mime_type.startswith('image/'):
            self._generate_thumbnail(final_path, attachment_id)
            attachment.is_processed = True
            attachment.processed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(attachment)
        
        response = AttachmentResponse.model_validate(attachment)
        return response, False, None
    
    async def get_attachment(
        self, 
        attachment_id: str, 
        user_id: str
    ) -> AttachmentResponse:
        """Get attachment by ID."""
        query = select(Attachment).where(Attachment.id == attachment_id)
        result = await self.db.execute(query)
        attachment = result.scalar_one_or_none()
        
        if not attachment:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        
        # Check permission
        if attachment.uploaded_by != user_id and not attachment.is_public:
            # Check if user owns the knowledge item
            query = select(KnowledgeItem).where(
                KnowledgeItem.id == attachment.knowledge_item_id
            )
            result = await self.db.execute(query)
            item = result.scalar_one_or_none()
            
            if not item or item.author_id != user_id:
                raise PermissionError("You don't have permission to access this attachment")
        
        return AttachmentResponse.model_validate(attachment)
    
    async def get_attachment_file_path(
        self, 
        attachment_id: str, 
        user_id: str
    ) -> Path:
        """Get the file system path for an attachment."""
        attachment = await self.get_attachment(attachment_id, user_id)
        file_path = self.upload_dir / attachment.file_path
        
        if not file_path.exists():
            raise NotFoundError(f"Attachment file not found on disk")
        
        return file_path
    
    async def list_attachments(
        self,
        user_id: str,
        knowledge_item_id: Optional[str] = None,
        mime_type_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> AttachmentListResponse:
        """List attachments with filtering and pagination."""
        # Build query
        query = select(Attachment)
        
        # Filter by knowledge item if specified
        if knowledge_item_id:
            # Verify access
            await self._verify_knowledge_item_access(knowledge_item_id, user_id)
            query = query.where(Attachment.knowledge_item_id == knowledge_item_id)
        else:
            # Only show user's attachments or public ones
            query = query.where(
                (Attachment.uploaded_by == user_id) | (Attachment.is_public == True)
            )
        
        # Filter by MIME type if specified
        if mime_type_filter:
            if mime_type_filter == 'image':
                query = query.where(Attachment.mime_type.like('image/%'))
            elif mime_type_filter == 'video':
                query = query.where(Attachment.mime_type.like('video/%'))
            elif mime_type_filter == 'audio':
                query = query.where(Attachment.mime_type.like('audio/%'))
            elif mime_type_filter == 'document':
                doc_types = [
                    'application/pdf',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'text/plain',
                    'text/markdown'
                ]
                query = query.where(Attachment.mime_type.in_(doc_types))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination
        query = query.order_by(Attachment.uploaded_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        attachments = result.scalars().all()
        
        # Convert to response models
        items = [AttachmentResponse.model_validate(att) for att in attachments]
        
        return AttachmentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def update_attachment(
        self,
        attachment_id: str,
        user_id: str,
        data: AttachmentUpdate
    ) -> AttachmentResponse:
        """Update attachment metadata."""
        query = select(Attachment).where(Attachment.id == attachment_id)
        result = await self.db.execute(query)
        attachment = result.scalar_one_or_none()
        
        if not attachment:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        
        # Check permission
        if attachment.uploaded_by != user_id:
            raise PermissionError("You don't have permission to update this attachment")
        
        # Update fields
        if data.filename is not None:
            attachment.filename = self._sanitize_filename(data.filename)
        if data.is_public is not None:
            attachment.is_public = data.is_public
        
        await self.db.commit()
        await self.db.refresh(attachment)
        
        return AttachmentResponse.model_validate(attachment)
    
    async def delete_attachment(
        self,
        attachment_id: str,
        user_id: str
    ) -> None:
        """Delete an attachment and its file."""
        query = select(Attachment).where(Attachment.id == attachment_id)
        result = await self.db.execute(query)
        attachment = result.scalar_one_or_none()
        
        if not attachment:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        
        # Check permission
        if attachment.uploaded_by != user_id:
            raise PermissionError("You don't have permission to delete this attachment")
        
        # Delete file from disk
        file_path = self.upload_dir / attachment.file_path
        if file_path.exists():
            file_path.unlink()
        
        # Delete thumbnail if exists
        if attachment.is_image:
            thumbnail_path = self.upload_dir / 'thumbnails' / f"thumb_{attachment_id}.jpg"
            if thumbnail_path.exists():
                thumbnail_path.unlink()
        
        # Delete database record
        await self.db.delete(attachment)
        await self.db.commit()
    
    async def get_attachment_stats(
        self,
        user_id: str,
        knowledge_item_id: Optional[str] = None
    ) -> AttachmentStats:
        """Get attachment statistics."""
        # Build base query
        query = select(Attachment)
        
        if knowledge_item_id:
            await self._verify_knowledge_item_access(knowledge_item_id, user_id)
            query = query.where(Attachment.knowledge_item_id == knowledge_item_id)
        else:
            query = query.where(Attachment.uploaded_by == user_id)
        
        # Get all attachments
        result = await self.db.execute(query)
        attachments = result.scalars().all()
        
        # Calculate statistics
        total_count = len(attachments)
        total_size = sum(att.file_size for att in attachments)
        
        # Group by type
        by_type = {
            'images': 0,
            'videos': 0,
            'audio': 0,
            'documents': 0,
            'others': 0
        }
        
        by_mime_type = {}
        
        for att in attachments:
            # Count by category
            if att.is_image:
                by_type['images'] += 1
            elif att.is_video:
                by_type['videos'] += 1
            elif att.is_audio:
                by_type['audio'] += 1
            elif att.is_document:
                by_type['documents'] += 1
            else:
                by_type['others'] += 1
            
            # Count by MIME type
            by_mime_type[att.mime_type] = by_mime_type.get(att.mime_type, 0) + 1
        
        # Format total size
        size = total_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                total_size_human = f"{size:.1f} {unit}"
                break
            size /= 1024.0
        else:
            total_size_human = f"{size:.1f} TB"
        
        return AttachmentStats(
            total_count=total_count,
            total_size=total_size,
            total_size_human=total_size_human,
            by_type=by_type,
            by_mime_type=by_mime_type
        )
