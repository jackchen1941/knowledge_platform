"""
Backup API Endpoints

API endpoints for data backup and restore operations.
"""

from io import BytesIO
from typing import Dict, Any

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.backup import BackupService
from app.schemas.backup import (
    BackupCreate,
    BackupVerification,
    RestoreOptions,
    RestoreResult,
)

router = APIRouter()


@router.post("/backup/create", response_class=StreamingResponse)
async def create_backup(
    backup_create: BackupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a backup of user data.
    
    - **backup_type**: full or incremental
    - **since**: For incremental backup, backup changes since this date
    
    Returns a ZIP file containing the backup.
    """
    
    service = BackupService(db)
    
    try:
        if backup_create.backup_type == "incremental" and backup_create.since:
            backup_file = await service.create_incremental_backup(
                current_user.id,
                backup_create.since
            )
            filename = f"incremental_backup_{current_user.username}.zip"
        else:
            backup_file = await service.create_full_backup(current_user.id)
            filename = f"full_backup_{current_user.username}.zip"
        
        return StreamingResponse(
            backup_file,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup creation failed: {str(e)}"
        )


@router.post("/backup/verify", response_model=BackupVerification)
async def verify_backup(
    backup_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify the integrity of a backup file.
    
    Returns verification results including:
    - valid: Whether the backup is valid
    - metadata: Backup metadata
    - item_count: Number of knowledge items
    - category_count: Number of categories
    - tag_count: Number of tags
    """
    
    service = BackupService(db)
    
    try:
        # Read uploaded file
        content = await backup_file.read()
        backup_buffer = BytesIO(content)
        
        # Verify backup
        verification = await service.verify_backup(backup_buffer)
        
        return verification
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Backup verification failed: {str(e)}"
        )


@router.post("/backup/restore", response_model=RestoreResult)
async def restore_backup(
    backup_file: UploadFile = File(...),
    restore_knowledge: bool = True,
    restore_categories: bool = True,
    restore_tags: bool = True,
    overwrite_existing: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Restore data from a backup file.
    
    Options:
    - **restore_knowledge**: Restore knowledge items
    - **restore_categories**: Restore categories
    - **restore_tags**: Restore tags
    - **overwrite_existing**: Overwrite existing data
    
    Returns the number of items restored in each category.
    """
    
    service = BackupService(db)
    
    try:
        # Read uploaded file
        content = await backup_file.read()
        backup_buffer = BytesIO(content)
        
        # Prepare options
        options = {
            "restore_knowledge": restore_knowledge,
            "restore_categories": restore_categories,
            "restore_tags": restore_tags,
            "overwrite_existing": overwrite_existing,
        }
        
        # Restore backup
        results = await service.restore_backup(
            backup_buffer,
            current_user.id,
            options
        )
        
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup restore failed: {str(e)}"
        )
