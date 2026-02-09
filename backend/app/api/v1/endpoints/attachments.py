"""
Attachment Management Endpoints

Handles file upload, download, and management operations.
"""

from typing import Any, Optional

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status, 
    Query, 
    UploadFile, 
    File
)
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import security, get_current_user_id
from app.services.attachment import AttachmentService
from app.schemas.attachment import (
    AttachmentResponse,
    AttachmentListResponse,
    AttachmentUpdate,
    AttachmentUploadResponse,
    AttachmentBatchUploadResponse,
    AttachmentStats
)
from app.core.exceptions import NotFoundError, PermissionError, ValidationError

router = APIRouter()


@router.post(
    "/knowledge/{knowledge_item_id}/attachments",
    response_model=AttachmentUploadResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_attachment(
    knowledge_item_id: str,
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Upload a file attachment to a knowledge item.
    
    - **file**: File to upload (multipart/form-data)
    - **knowledge_item_id**: ID of the knowledge item to attach to
    
    Supports:
    - Images: JPEG, PNG, GIF, WebP
    - Documents: PDF, Word, Plain text, Markdown
    - Audio: MP3, WAV
    - Video: MP4, WebM
    
    Features:
    - Automatic file type validation
    - File size limits (configurable)
    - Duplicate detection via hash
    - Automatic thumbnail generation for images
    - Secure filename handling
    """
    user_id = get_current_user_id(credentials)
    service = AttachmentService(db)
    
    try:
        # Upload file
        attachment, is_duplicate, duplicate_of = await service.upload_file(
            user_id=user_id,
            knowledge_item_id=knowledge_item_id,
            file=file.file,
            filename=file.filename,
            mime_type=file.content_type
        )
        
        return AttachmentUploadResponse(
            attachment=attachment,
            message="File uploaded successfully" if not is_duplicate else "File already exists",
            is_duplicate=is_duplicate,
            duplicate_of=duplicate_of
        )
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post(
    "/knowledge/{knowledge_item_id}/attachments/batch",
    response_model=AttachmentBatchUploadResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_attachments_batch(
    knowledge_item_id: str,
    files: list[UploadFile] = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Upload multiple file attachments to a knowledge item.
    
    - **files**: List of files to upload (multipart/form-data)
    - **knowledge_item_id**: ID of the knowledge item to attach to
    
    Returns information about all uploaded files including duplicates.
    """
    user_id = get_current_user_id(credentials)
    service = AttachmentService(db)
    
    attachments = []
    duplicates = []
    total_size = 0
    errors = []
    
    for file in files:
        try:
            attachment, is_duplicate, duplicate_of = await service.upload_file(
                user_id=user_id,
                knowledge_item_id=knowledge_item_id,
                file=file.file,
                filename=file.filename,
                mime_type=file.content_type
            )
            
            attachments.append(attachment)
            total_size += attachment.file_size
            
            if is_duplicate:
                duplicates.append(file.filename)
        
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    if errors and not attachments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"All uploads failed: {'; '.join(errors)}"
        )
    
    message = f"Uploaded {len(attachments)} files successfully"
    if errors:
        message += f" ({len(errors)} failed)"
    
    return AttachmentBatchUploadResponse(
        attachments=attachments,
        total_uploaded=len(attachments),
        total_size=total_size,
        message=message,
        duplicates=duplicates
    )


@router.get(
    "/knowledge/{knowledge_item_id}/attachments",
    response_model=AttachmentListResponse
)
async def get_knowledge_item_attachments(
    knowledge_item_id: str,
    mime_type_filter: Optional[str] = Query(
        None, 
        description="Filter by type: image, video, audio, document"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get all attachments for a knowledge item.
    
    Returns a paginated list of attachments with optional filtering by type.
    """
    user_id = get_current_user_id(credentials)
    service = AttachmentService(db)
    
    try:
        result = await service.list_attachments(
            user_id=user_id,
            knowledge_item_id=knowledge_item_id,
            mime_type_filter=mime_type_filter,
            page=page,
            page_size=page_size
        )
        return result
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list attachments: {str(e)}"
        )


@router.get("/attachments", response_model=AttachmentListResponse)
async def list_user_attachments(
    mime_type_filter: Optional[str] = Query(
        None, 
        description="Filter by type: image, video, audio, document"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get all attachments for the current user.
    
    Returns a paginated list of all attachments uploaded by the user.
    """
    user_id = get_current_user_id(credentials)
    service = AttachmentService(db)
    
    try:
        result = await service.list_attachments(
            user_id=user_id,
            knowledge_item_id=None,
            mime_type_filter=mime_type_filter,
            page=page,
            page_size=page_size
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list attachments: {str(e)}"
        )


@router.get("/attachments/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(
    attachment_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get attachment metadata by ID.
    
    Returns detailed information about the attachment including file properties.
    """
    user_id = get_current_user_id(credentials)
    service = AttachmentService(db)
    
    try:
        attachment = await service.get_attachment(attachment_id, user_id)
        return attachment
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attachment: {str(e)}"
        )


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """
    Download an attachment file.
    
    Returns the actual file for download with appropriate headers.
    """
    user_id = get_current_user_id(credentials)
    service = AttachmentService(db)
    
    try:
        # Get attachment metadata
        attachment = await service.get_attachment(attachment_id, user_id)
        
        # Get file path
        file_path = await service.get_attachment_file_path(attachment_id, user_id)
        
        # Return file
        return FileResponse(
            path=str(file_path),
            filename=attachment.filename,
            media_type=attachment.mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{attachment.filename}"'
            }
        )
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download attachment: {str(e)}"
        )


@router.put("/attachments/{attachment_id}", response_model=AttachmentResponse)
async def update_attachment(
    attachment_id: str,
    data: AttachmentUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update attachment metadata.
    
    Allows updating the display filename and public access flag.
    """
    user_id = get_current_user_id(credentials)
    service = AttachmentService(db)
    
    try:
        attachment = await service.update_attachment(attachment_id, user_id, data)
        return attachment
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update attachment: {str(e)}"
        )


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete an attachment.
    
    Permanently removes the attachment file and database record.
    Only the uploader can delete their attachments.
    """
    user_id = get_current_user_id(credentials)
    service = AttachmentService(db)
    
    try:
        await service.delete_attachment(attachment_id, user_id)
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete attachment: {str(e)}"
        )


@router.get("/attachments/stats/summary", response_model=AttachmentStats)
async def get_attachment_stats(
    knowledge_item_id: Optional[str] = Query(
        None, 
        description="Get stats for specific knowledge item"
    ),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get attachment statistics.
    
    Returns statistics about attachments including total count, size,
    and breakdown by file type.
    """
    user_id = get_current_user_id(credentials)
    service = AttachmentService(db)
    
    try:
        stats = await service.get_attachment_stats(
            user_id=user_id,
            knowledge_item_id=knowledge_item_id
        )
        return stats
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attachment stats: {str(e)}"
        )
