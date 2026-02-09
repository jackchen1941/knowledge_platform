"""
Import/Export Endpoints

Handles data import from external platforms and export functionality.
"""

from typing import List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.export import ExportService
from app.schemas.export import (
    ExportSingleRequest,
    ExportBatchRequest,
    ExportAllRequest,
    ExportResponse
)

router = APIRouter()


@router.post("/export/{knowledge_item_id}", response_class=Response)
async def export_single_item(
    knowledge_item_id: str,
    request: ExportSingleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export a single knowledge item to the specified format.
    Returns the file content directly.
    """
    service = ExportService(db)
    
    if request.format == "markdown":
        content = await service.export_to_markdown(
            knowledge_item_id,
            current_user.id,
            request.include_metadata
        )
        media_type = "text/markdown"
        extension = "md"
    elif request.format == "json":
        import json
        data = await service.export_to_json(
            knowledge_item_id,
            current_user.id,
            request.include_versions
        )
        content = json.dumps(data, ensure_ascii=False, indent=2)
        media_type = "application/json"
        extension = "json"
    else:  # html
        content = await service.export_to_html(knowledge_item_id, current_user.id)
        media_type = "text/html"
        extension = "html"
    
    # Get item for filename
    item = await service._get_item(knowledge_item_id, current_user.id)
    safe_title = "".join(c for c in item.title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title[:50]
    filename = f"{safe_title}.{extension}"
    
    return Response(
        content=content.encode('utf-8') if isinstance(content, str) else content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.post("/export/batch", response_class=StreamingResponse)
async def export_batch_items(
    request: ExportBatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export multiple knowledge items to a ZIP file.
    Returns a ZIP file containing all exported items.
    """
    service = ExportService(db)
    
    zip_buffer = await service.batch_export(
        current_user.id,
        request.item_ids,
        request.format,
        request.include_metadata
    )
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"knowledge_export_{timestamp}.zip"
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.post("/export/all", response_class=StreamingResponse)
async def export_all_items(
    request: ExportAllRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export all knowledge items for the current user to a ZIP file.
    Returns a ZIP file containing all items.
    """
    service = ExportService(db)
    
    zip_buffer = await service.export_all(
        current_user.id,
        request.format,
        request.include_deleted
    )
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"knowledge_full_export_{timestamp}.zip"
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# TODO: Import endpoints
# @router.post("/import/configure")
# async def configure_import_source(...):
#     """Configure an import source."""
#     pass

# @router.post("/import/start")
# async def start_import(...):
#     """Start an import process."""
#     pass

# @router.get("/import/status/{task_id}")
# async def get_import_status(...):
#     """Get import task status."""
#     pass
