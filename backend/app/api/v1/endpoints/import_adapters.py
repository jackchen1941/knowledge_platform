"""
Import Adapters API Endpoints

API endpoints for managing external platform import adapters.
"""

from typing import List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.import_config import ImportConfig, ImportTask
from app.schemas.import_adapter import (
    AdapterConfigCreate,
    AdapterConfigUpdate,
    AdapterConfigResponse,
    ImportTaskCreate,
    ImportTaskResponse,
    ImportResult,
    PlatformInfo,
    ValidateConfigRequest,
    ValidateConfigResponse,
)
from app.services.adapters import (
    CSDNAdapter,
    WeChatAdapter,
    NotionAdapter,
    MarkdownAdapter,
)

router = APIRouter()

# Platform registry
PLATFORMS = {
    'csdn': {
        'adapter': CSDNAdapter,
        'name': 'CSDN博客',
        'description': '从CSDN博客导入文章',
        'required_config': ['username'],
        'optional_config': [],
        'example_config': {'username': 'your_username'}
    },
    'wechat': {
        'adapter': WeChatAdapter,
        'name': '微信公众号',
        'description': '从微信公众平台导入文章',
        'required_config': ['app_id', 'app_secret'],
        'optional_config': [],
        'example_config': {
            'app_id': 'wx1234567890',
            'app_secret': 'your_secret'
        }
    },
    'notion': {
        'adapter': NotionAdapter,
        'name': 'Notion',
        'description': '从Notion工作区导入页面',
        'required_config': ['api_key'],
        'optional_config': ['database_id'],
        'example_config': {
            'api_key': 'secret_xxx',
            'database_id': 'optional_database_id'
        }
    },
    'markdown': {
        'adapter': MarkdownAdapter,
        'name': 'Markdown文件',
        'description': '导入Markdown文件',
        'required_config': ['file_path'],
        'optional_config': [],
        'example_config': {'file_path': '/path/to/files'}
    }
}


@router.get("/platforms", response_model=List[PlatformInfo])
async def list_platforms():
    """
    Get list of available import platforms.
    
    Returns information about all supported platforms including
    required configuration fields and examples.
    """
    platforms = []
    for platform_id, info in PLATFORMS.items():
        platforms.append(PlatformInfo(
            platform=platform_id,
            name=info['name'],
            description=info['description'],
            required_config=info['required_config'],
            optional_config=info['optional_config'],
            example_config=info['example_config']
        ))
    return platforms


@router.post("/validate", response_model=ValidateConfigResponse)
async def validate_config(
    request: ValidateConfigRequest,
    current_user_id: str = Depends(get_current_user),
):
    """
    Validate adapter configuration.
    
    Tests if the provided configuration is valid for the specified platform.
    """
    if request.platform not in PLATFORMS:
        return ValidateConfigResponse(
            valid=False,
            message=f"Unknown platform: {request.platform}",
            errors=[f"Platform '{request.platform}' is not supported"]
        )
    
    platform_info = PLATFORMS[request.platform]
    adapter_class = platform_info['adapter']
    
    # Check required fields
    errors = []
    for field in platform_info['required_config']:
        if field not in request.config:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return ValidateConfigResponse(
            valid=False,
            message="Configuration validation failed",
            errors=errors
        )
    
    # Try to create adapter and validate
    try:
        adapter = adapter_class(request.config)
        is_valid = await adapter.validate_config()
        
        if is_valid:
            return ValidateConfigResponse(
                valid=True,
                message="Configuration is valid"
            )
        else:
            return ValidateConfigResponse(
                valid=False,
                message="Configuration validation failed",
                errors=["Adapter validation failed"]
            )
    
    except Exception as e:
        return ValidateConfigResponse(
            valid=False,
            message="Configuration validation error",
            errors=[str(e)]
        )


@router.get("/configs", response_model=List[AdapterConfigResponse])
async def list_configs(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of user's import configurations.
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(ImportConfig).where(ImportConfig.user_id == current_user_id)
    )
    configs = result.scalars().all()
    
    return configs


@router.post("/configs", response_model=AdapterConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    config_data: AdapterConfigCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new import configuration.
    """
    import uuid
    
    # Validate platform
    if config_data.platform not in PLATFORMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown platform: {config_data.platform}"
        )
    
    # Create configuration
    config = ImportConfig(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        name=config_data.name,
        platform=config_data.platform,
        config=config_data.config,
        auto_sync=config_data.auto_sync,
        sync_interval=config_data.sync_interval,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    return config


@router.get("/configs/{config_id}", response_model=AdapterConfigResponse)
async def get_config(
    config_id: str,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get import configuration by ID.
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(ImportConfig).where(
            ImportConfig.id == config_id,
            ImportConfig.user_id == current_user_id
        )
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    return config


@router.put("/configs/{config_id}", response_model=AdapterConfigResponse)
async def update_config(
    config_id: str,
    config_data: AdapterConfigUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update import configuration.
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(ImportConfig).where(
            ImportConfig.id == config_id,
            ImportConfig.user_id == current_user_id
        )
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    # Update fields
    if config_data.name is not None:
        config.name = config_data.name
    if config_data.config is not None:
        config.config = config_data.config
    if config_data.auto_sync is not None:
        config.auto_sync = config_data.auto_sync
    if config_data.sync_interval is not None:
        config.sync_interval = config_data.sync_interval
    if config_data.is_active is not None:
        config.is_active = config_data.is_active
    
    config.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(config)
    
    return config


@router.delete("/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: str,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete import configuration.
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(ImportConfig).where(
            ImportConfig.id == config_id,
            ImportConfig.user_id == current_user_id
        )
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    await db.delete(config)
    await db.commit()


@router.post("/configs/{config_id}/import", response_model=ImportResult)
async def execute_import(
    config_id: str,
    task_data: ImportTaskCreate,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute import from configured platform.
    
    This creates an import task and executes it in the background.
    """
    from sqlalchemy import select
    import uuid
    from app.models.knowledge import KnowledgeItem
    
    # Get configuration
    result = await db.execute(
        select(ImportConfig).where(
            ImportConfig.id == config_id,
            ImportConfig.user_id == current_user_id
        )
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    # Create import task
    task = ImportTask(
        id=str(uuid.uuid4()),
        config_id=config_id,
        status='running',
        items_total=0,
        items_imported=0,
        items_failed=0,
        started_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Execute import
    try:
        platform_info = PLATFORMS[config.platform]
        adapter_class = platform_info['adapter']
        adapter = adapter_class(config.config)
        
        # Import items
        items = await adapter.import_items(
            since=task_data.since,
            limit=task_data.limit
        )
        
        task.items_total = len(items)
        
        # Create knowledge items
        imported = 0
        failed = 0
        errors = []
        
        for item_data in items:
            try:
                knowledge = KnowledgeItem(
                    id=str(uuid.uuid4()),
                    title=item_data['title'],
                    content=item_data['content'],
                    content_type=item_data['content_type'],
                    summary=item_data.get('summary'),
                    author_id=current_user_id,
                    source_platform=item_data['source_platform'],
                    source_url=item_data.get('source_url'),
                    source_id=item_data['source_id'],
                    meta_data=item_data.get('meta_data', {}),
                    is_published=True,
                    visibility='private',
                    created_at=item_data.get('published_at') or datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                
                db.add(knowledge)
                imported += 1
            
            except Exception as e:
                failed += 1
                errors.append(f"Failed to import '{item_data.get('title', 'Unknown')}': {str(e)}")
        
        await db.commit()
        
        # Update task
        task.items_imported = imported
        task.items_failed = failed
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        
        # Update config last sync
        config.last_sync = datetime.utcnow()
        
        await db.commit()
        
        return ImportResult(
            success=True,
            items_imported=imported,
            items_failed=failed,
            errors=errors[:10],  # Limit errors
            task_id=task.id
        )
    
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.get("/tasks", response_model=List[ImportTaskResponse])
async def list_tasks(
    config_id: str = None,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of import tasks.
    """
    from sqlalchemy import select
    
    query = select(ImportTask).join(ImportConfig).where(
        ImportConfig.user_id == current_user_id
    )
    
    if config_id:
        query = query.where(ImportTask.config_id == config_id)
    
    query = query.order_by(ImportTask.created_at.desc()).limit(50)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return tasks


@router.get("/tasks/{task_id}", response_model=ImportTaskResponse)
async def get_task(
    task_id: str,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get import task by ID.
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(ImportTask)
        .join(ImportConfig)
        .where(
            ImportTask.id == task_id,
            ImportConfig.user_id == current_user_id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task



@router.post("/import-url")
async def import_from_url(
    url: str,
    category: str = None,
    tags: List[str] = None,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick import from a single URL.
    
    This is a convenience endpoint that doesn't require creating a config first.
    Supports any public webpage.
    
    Example:
        POST /api/v1/import-adapters/import-url?url=https://example.com/article
    """
    import uuid
    from app.services.adapters.url_adapter import URLAdapter
    from app.models.knowledge import KnowledgeItem
    
    try:
        # Create URL adapter
        adapter = URLAdapter({'url': url})
        
        # Validate config
        if not await adapter.validate_config():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL"
            )
        
        # Fetch and transform item
        items = await adapter.fetch_items()
        
        if not items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not fetch content from URL. Please check if the URL is accessible."
            )
        
        transformed = await adapter.transform_item(items[0])
        
        # Override category if provided
        if category:
            transformed['category'] = category
        
        # Override tags if provided
        if tags:
            transformed['tags'] = tags
        
        # Create knowledge item
        knowledge = KnowledgeItem(
            id=str(uuid.uuid4()),
            title=transformed['title'],
            content=transformed['content'],
            content_type=transformed.get('content_type', 'markdown'),
            summary=transformed.get('summary'),
            author_id=current_user_id,
            source_platform=transformed.get('source_platform', 'url'),
            source_url=transformed.get('source_url'),
            source_id=transformed.get('source_id'),
            meta_data=transformed.get('meta_data', {}),
            is_published=True,
            visibility='private',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(knowledge)
        await db.commit()
        await db.refresh(knowledge)
        
        return {
            "success": True,
            "knowledge_id": knowledge.id,
            "title": knowledge.title,
            "imported_at": knowledge.created_at.isoformat(),
            "metadata": {
                "word_count": knowledge.word_count,
                "reading_time": knowledge.reading_time,
                "source_url": knowledge.source_url,
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.post("/import-urls")
async def import_from_urls(
    urls: List[str],
    category: str = None,
    tags: List[str] = None,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Batch import from multiple URLs.
    
    Example:
        POST /api/v1/import-adapters/import-urls
        {
            "urls": ["https://example.com/article1", "https://example.com/article2"],
            "category": "技术文章",
            "tags": ["Python", "教程"]
        }
    """
    import uuid
    from app.services.adapters.url_adapter import URLAdapter
    from app.models.knowledge import KnowledgeItem
    
    results = []
    
    for url in urls:
        try:
            # Create URL adapter
            adapter = URLAdapter({'url': url})
            
            # Fetch and transform item
            items = await adapter.fetch_items()
            
            if not items:
                results.append({
                    "url": url,
                    "success": False,
                    "error": "Could not fetch content"
                })
                continue
            
            transformed = await adapter.transform_item(items[0])
            
            # Override category and tags if provided
            if category:
                transformed['category'] = category
            if tags:
                transformed['tags'] = tags
            
            # Create knowledge item
            knowledge = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=transformed['title'],
                content=transformed['content'],
                content_type=transformed.get('content_type', 'markdown'),
                summary=transformed.get('summary'),
                author_id=current_user_id,
                source_platform=transformed.get('source_platform', 'url'),
                source_url=transformed.get('source_url'),
                source_id=transformed.get('source_id'),
                meta_data=transformed.get('meta_data', {}),
                is_published=True,
                visibility='private',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            
            db.add(knowledge)
            await db.commit()
            await db.refresh(knowledge)
            
            results.append({
                "url": url,
                "success": True,
                "knowledge_id": knowledge.id,
                "title": knowledge.title
            })
        
        except Exception as e:
            results.append({
                "url": url,
                "success": False,
                "error": str(e)
            })
    
    # Count successes and failures
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    return {
        "total": len(urls),
        "successful": successful,
        "failed": failed,
        "results": results
    }
