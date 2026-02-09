"""
Simplified API Router

A working version of the API router that includes essential endpoints
without complex import dependencies.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session, get_db
from app.core.security import security, get_current_user_id
from app.services.sync import SyncService
from app.schemas.sync import (
    DeviceRegister as DeviceRegisterRequest,
    DeviceResponse,
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
    ConflictResponse,
    ConflictResolve as ConflictResolveRequest
)

# Create API router
api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is working"}

# Sync endpoints
sync_router = APIRouter(prefix="/sync", tags=["sync"])

@sync_router.post("/devices/register", response_model=DeviceResponse)
async def register_device(
    device_data: DeviceRegisterRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Register a new device for sync."""
    user_id = get_current_user_id(credentials)
    
    sync_service = SyncService(db)
    device = await sync_service.register_device(
        user_id=user_id,
        device_name=device_data.device_name,
        device_type=device_data.device_type,
        device_id=device_data.device_id
    )
    
    return DeviceResponse(
        id=device.id,
        device_name=device.device_name,
        device_type=device.device_type,
        device_id=device.device_id,
        last_sync=device.last_sync,
        is_active=device.is_active,
        created_at=device.created_at
    )

@sync_router.get("/devices", response_model=list[DeviceResponse])
async def list_devices(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """List user's devices."""
    user_id = get_current_user_id(credentials)
    
    sync_service = SyncService(db)
    devices = await sync_service.list_devices(user_id)
    
    return [
        DeviceResponse(
            id=device.id,
            device_name=device.device_name,
            device_type=device.device_type,
            device_id=device.device_id,
            last_sync=device.last_sync,
            is_active=device.is_active,
            created_at=device.created_at
        )
        for device in devices
    ]

@sync_router.post("/pull/{device_id}", response_model=SyncPullResponse)
async def pull_changes(
    device_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Pull changes for device."""
    user_id = get_current_user_id(credentials)
    
    sync_service = SyncService(db)
    result = await sync_service.pull_changes(device_id)
    
    return SyncPullResponse(
        changes=result.get('changes', {}),
        sync_time=result.get('last_sync_time', ''),
        has_conflicts=len(result.get('conflicts', [])) > 0
    )

@sync_router.post("/push/{device_id}", response_model=SyncPushResponse)
async def push_changes(
    device_id: str,
    push_data: SyncPushRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Push changes from device."""
    user_id = get_current_user_id(credentials)
    
    sync_service = SyncService(db)
    result = await sync_service.push_changes(device_id, push_data.changes)
    
    return SyncPushResponse(
        applied=result.get('processed', 0),
        conflicts=result.get('conflicts', 0),
        errors=result.get('errors', []),
        sync_time=result.get('sync_time', '')
    )

# Add sync router to main router
api_router.include_router(sync_router)

# Basic knowledge endpoints (simplified)
knowledge_router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@knowledge_router.get("/test")
async def test_knowledge():
    """Test knowledge endpoint."""
    return {"message": "Knowledge API is working", "endpoints": ["list", "create", "get", "update", "delete"]}

@knowledge_router.post("/")
async def create_knowledge_item(
    item_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Create a new knowledge item."""
    from app.services.knowledge import KnowledgeService
    from app.schemas.knowledge import KnowledgeCreate
    from app.core.security_advanced import validate_request_security, SecurityAuditor
    
    try:
        user_id = get_current_user_id(credentials)
        
        # Validate input security
        validate_request_security(item_data)
        
        # Additional content validation
        title = item_data.get('title', '')
        content = item_data.get('content', '')
        
        if len(title) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title too long (max 500 characters)"
            )
        
        if len(content) > 100000:  # 100KB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content too long (max 100KB)"
            )
        
        # Create KnowledgeCreate object
        create_data = KnowledgeCreate(
            title=title,
            content=content,
            content_type=item_data.get('content_type', 'markdown'),
            summary=item_data.get('summary'),
            category_id=item_data.get('category_id'),
            tag_ids=item_data.get('tag_ids', []),
            is_published=item_data.get('is_published', False),
            visibility=item_data.get('visibility', 'private'),
            source_platform=item_data.get('source_platform'),
            source_url=item_data.get('source_url'),
            meta_data=item_data.get('meta_data', {})
        )
        
        knowledge_service = KnowledgeService(db)
        item = await knowledge_service.create_knowledge_item(user_id, create_data)
        
        # Log knowledge creation
        SecurityAuditor.log_security_event(
            "KNOWLEDGE_CREATED",
            user_id=user_id,
            details={
                "knowledge_id": item.id,
                "title": item.title[:100],
                "content_length": len(item.content),
                "is_published": item.is_published
            }
        )
        
        return {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "content_type": item.content_type,
            "summary": item.summary,
            "author_id": item.author_id,
            "is_published": item.is_published,
            "visibility": item.visibility,
            "word_count": item.word_count,
            "reading_time": item.reading_time,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "message": "Knowledge item created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        SecurityAuditor.log_security_event(
            "KNOWLEDGE_CREATION_FAILED",
            user_id=get_current_user_id(credentials) if credentials else None,
            details={"error": str(e)},
            severity="WARNING"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create knowledge item: {str(e)}"
        )

@knowledge_router.get("/")
async def list_knowledge_items(
    limit: int = 20,
    offset: int = 0,
    search: str = None,
    category_id: str = None,
    is_published: bool = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """List knowledge items with filtering."""
    from app.services.knowledge import KnowledgeService
    
    try:
        user_id = get_current_user_id(credentials)
        
        knowledge_service = KnowledgeService(db)
        
        # Create filter object
        from app.schemas.knowledge import KnowledgeFilter
        
        # Calculate page from offset and limit
        page = (offset // limit) + 1 if limit > 0 else 1
        
        filter_obj = KnowledgeFilter(
            search=search,
            category_id=category_id,
            is_published=is_published,
            page=page,
            page_size=limit
        )
        
        result = await knowledge_service.list_knowledge_items(
            user_id=user_id,
            filters=filter_obj
        )
        
        return {
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "content_type": item.content_type,
                    "author_id": item.author_id,
                    "is_published": item.is_published,
                    "visibility": item.visibility,
                    "word_count": item.word_count,
                    "reading_time": item.reading_time,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at
                }
                for item in result.items
            ],
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list knowledge items: {str(e)}"
        )

@knowledge_router.get("/{item_id}")
async def get_knowledge_item(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific knowledge item."""
    from app.services.knowledge import KnowledgeService
    
    try:
        user_id = get_current_user_id(credentials)
        
        knowledge_service = KnowledgeService(db)
        item = await knowledge_service.get_knowledge_item(item_id, user_id)
        
        return {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "content_type": item.content_type,
            "summary": item.summary,
            "author_id": item.author_id,
            "category_id": item.category_id,
            "is_published": item.is_published,
            "visibility": item.visibility,
            "word_count": item.word_count,
            "reading_time": item.reading_time,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "published_at": item.published_at,
            "meta_data": item.meta_data
        }
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge item not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge item: {str(e)}"
        )

@knowledge_router.put("/{item_id}")
async def update_knowledge_item(
    item_id: str,
    update_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Update a knowledge item."""
    from app.services.knowledge import KnowledgeService
    from app.schemas.knowledge import KnowledgeUpdate
    
    try:
        user_id = get_current_user_id(credentials)
        
        # Create KnowledgeUpdate object
        update_obj = KnowledgeUpdate(
            title=update_data.get('title'),
            content=update_data.get('content'),
            summary=update_data.get('summary'),
            category_id=update_data.get('category_id'),
            tag_ids=update_data.get('tag_ids'),
            is_published=update_data.get('is_published'),
            visibility=update_data.get('visibility'),
            meta_data=update_data.get('meta_data')
        )
        
        knowledge_service = KnowledgeService(db)
        item = await knowledge_service.update_knowledge_item(
            item_id, user_id, update_obj
        )
        
        return {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "summary": item.summary,
            "is_published": item.is_published,
            "updated_at": item.updated_at,
            "message": "Knowledge item updated successfully"
        }
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge item not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update knowledge item: {str(e)}"
        )

@knowledge_router.delete("/{item_id}")
async def delete_knowledge_item(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Delete a knowledge item (soft delete)."""
    from app.services.knowledge import KnowledgeService
    
    try:
        user_id = get_current_user_id(credentials)
        
        knowledge_service = KnowledgeService(db)
        success = await knowledge_service.delete_knowledge_item(item_id, user_id)
        
        if success:
            return {"message": "Knowledge item deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge item not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete knowledge item: {str(e)}"
        )

# Add knowledge router
api_router.include_router(knowledge_router)

# Notification endpoints
notification_router = APIRouter(prefix="/notifications", tags=["notifications"])

@notification_router.get("/test")
async def test_notifications():
    """Test notifications endpoint."""
    return {
        "message": "Notifications API is working",
        "features": [
            "Create notifications",
            "List notifications", 
            "Mark as read",
            "Archive notifications",
            "Notification preferences",
            "Real-time updates"
        ]
    }

@notification_router.post("/demo")
async def create_demo_notification(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Create a demo notification."""
    user_id = get_current_user_id(credentials)
    
    from app.services.notification import NotificationService
    notification_service = NotificationService(db)
    
    notification = await notification_service.create_notification(
        user_id=user_id,
        title="欢迎使用通知系统",
        message="这是一个演示通知，展示了实时通知功能的工作原理。",
        notification_type="info",
        category="system",
        priority="normal",
        expires_hours=24
    )
    
    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "created_at": notification.created_at,
        "status": "created"
    }

# Add notification router
api_router.include_router(notification_router)

# WebSocket endpoints
websocket_router = APIRouter(prefix="/ws", tags=["websocket"])

@websocket_router.get("/test")
async def test_websocket():
    """Test WebSocket endpoint."""
    from app.core.websocket import connection_manager
    stats = connection_manager.get_connection_stats()
    
    return {
        "message": "WebSocket API is working",
        "features": [
            "Real-time notifications",
            "Live sync updates", 
            "System messages",
            "Room subscriptions"
        ],
        "current_stats": stats
    }

# Add websocket router
api_router.include_router(websocket_router)

# Authentication endpoints
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register")
async def register_user(
    user_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    from app.services.auth import AuthService
    from app.schemas.auth import UserRegister
    from app.core.security_advanced import validate_request_security, SecurityAuditor
    
    try:
        # Validate input security
        validate_request_security(user_data)
        
        # Create UserRegister object
        register_data = UserRegister(
            username=user_data.get('username'),
            email=user_data.get('email'),
            password=user_data.get('password'),
            full_name=user_data.get('full_name')
        )
        
        auth_service = AuthService(db)
        user = await auth_service.register_user(register_data)
        
        # Log successful registration
        SecurityAuditor.log_authentication_attempt(
            user_id=user.id,
            email=user.email,
            success=True
        )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "message": "User registered successfully"
        }
    except Exception as e:
        # Log failed registration
        SecurityAuditor.log_authentication_attempt(
            email=user_data.get('email'),
            success=False,
            failure_reason=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@auth_router.post("/login")
async def login_user(
    credentials: dict,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return token."""
    from app.services.auth import AuthService
    from app.core.security import TokenManager
    from app.core.security_advanced import validate_request_security, SecurityAuditor, brute_force_protection
    
    try:
        # Validate input security
        validate_request_security(credentials)
        
        email = credentials.get('email')
        password = credentials.get('password')
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Check brute force protection
        is_blocked, block_info = await brute_force_protection.is_blocked(email)
        if is_blocked:
            SecurityAuditor.log_suspicious_activity(
                "BRUTE_FORCE_BLOCKED",
                details={"email": email, "block_info": block_info}
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account temporarily locked due to too many failed attempts. Try again later."
            )
        
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(email, password)
        
        if not user:
            # Record failed attempt
            await brute_force_protection.record_attempt(email, False)
            SecurityAuditor.log_authentication_attempt(
                email=email,
                success=False,
                failure_reason="Invalid credentials"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Record successful attempt
        await brute_force_protection.record_attempt(email, True)
        
        # Create access token
        access_token = TokenManager.create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        # Log successful login
        SecurityAuditor.log_authentication_attempt(
            user_id=user.id,
            email=user.email,
            success=True
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            },
            "message": "Login successful"
        }
    except HTTPException:
        raise
    except Exception as e:
        SecurityAuditor.log_authentication_attempt(
            email=credentials.get('email'),
            success=False,
            failure_reason=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

# Add auth router
api_router.include_router(auth_router)

# Search endpoints
search_router = APIRouter(prefix="/search", tags=["search"])

@search_router.get("/")
async def search_knowledge(
    q: str,
    limit: int = 20,
    offset: int = 0,
    content_type: str = None,
    is_published: bool = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Search knowledge items."""
    from app.services.search import SearchService
    
    try:
        user_id = get_current_user_id(credentials)
        
        search_service = SearchService(db)
        results = await search_service.search_knowledge_items(
            query=q,
            user_id=user_id,
            limit=limit,
            offset=offset,
            content_type=content_type,
            is_published=is_published
        )
        
        return {
            "query": q,
            "results": [
                {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "content_type": item.content_type,
                    "is_published": item.is_published,
                    "word_count": item.word_count,
                    "reading_time": item.reading_time,
                    "created_at": item.created_at,
                    "relevance_score": getattr(item, 'relevance_score', 1.0)
                }
                for item in results
            ],
            "total": len(results),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        # Fallback to simple knowledge list search
        from app.services.knowledge import KnowledgeService
        from app.schemas.knowledge import KnowledgeFilter
        
        knowledge_service = KnowledgeService(db)
        filter_obj = KnowledgeFilter(
            search=q,
            is_published=is_published,
            limit=limit,
            offset=offset
        )
        
        result = await knowledge_service.list_knowledge_items(
            user_id=user_id,
            filters=filter_obj
        )
        
        return {
            "query": q,
            "results": [
                {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "content_type": item.content_type,
                    "is_published": item.is_published,
                    "word_count": item.word_count,
                    "reading_time": item.reading_time,
                    "created_at": item.created_at,
                    "relevance_score": 1.0
                }
                for item in result.items
            ],
            "total": result.total,
            "limit": limit,
            "offset": offset,
            "fallback": True
        }

@search_router.get("/suggestions")
async def get_search_suggestions(
    q: str,
    limit: int = 5,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get search suggestions."""
    user_id = get_current_user_id(credentials)
    
    # Simple implementation: return recent titles that match
    from app.models.knowledge import KnowledgeItem
    from sqlalchemy import select, or_, and_
    
    try:
        query = select(KnowledgeItem.title).where(
            and_(
                or_(
                    KnowledgeItem.author_id == user_id,
                    KnowledgeItem.visibility.in_(["shared", "public"])
                ),
                KnowledgeItem.title.ilike(f"%{q}%"),
                KnowledgeItem.is_deleted == False
            )
        ).limit(limit)
        
        result = await db.execute(query)
        suggestions = [row[0] for row in result.fetchall()]
        
        return {
            "query": q,
            "suggestions": suggestions
        }
    except Exception as e:
        # Fallback to empty suggestions
        return {
            "query": q,
            "suggestions": [],
            "error": str(e)
        }

# Add search router
api_router.include_router(search_router)

# Tags endpoints
tags_router = APIRouter(prefix="/tags", tags=["tags"])

@tags_router.get("/")
async def list_tags(
    limit: int = 50,
    search: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """List all tags."""
    from app.models.tag import Tag
    from sqlalchemy import select
    
    user_id = get_current_user_id(credentials)
    
    query = select(Tag)
    if search:
        query = query.where(Tag.name.ilike(f"%{search}%"))
    
    query = query.limit(limit)
    result = await db.execute(query)
    tags = result.scalars().all()
    
    return {
        "tags": [
            {
                "id": tag.id,
                "name": tag.name,
                "description": tag.description,
                "color": tag.color,
                "created_at": tag.created_at
            }
            for tag in tags
        ],
        "total": len(tags)
    }

@tags_router.post("/")
async def create_tag(
    tag_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Create a new tag."""
    from app.services.tag import TagService
    from app.schemas.tag import TagCreate
    
    user_id = get_current_user_id(credentials)
    
    try:
        create_data = TagCreate(
            name=tag_data.get('name'),
            description=tag_data.get('description'),
            color=tag_data.get('color', '#1890ff')
        )
        
        tag_service = TagService(db)
        tag = await tag_service.create_tag(user_id, create_data)
        
        return {
            "id": tag.id,
            "name": tag.name,
            "description": tag.description,
            "color": tag.color,
            "created_at": tag.created_at,
            "message": "Tag created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create tag: {str(e)}"
        )

# Categories endpoints
categories_router = APIRouter(prefix="/categories", tags=["categories"])

@categories_router.get("/")
async def list_categories(
    limit: int = 50,
    parent_id: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """List categories."""
    from app.models.category import Category
    from sqlalchemy import select
    
    user_id = get_current_user_id(credentials)
    
    query = select(Category)
    if parent_id:
        query = query.where(Category.parent_id == parent_id)
    else:
        query = query.where(Category.parent_id.is_(None))  # Root categories
    
    query = query.limit(limit)
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return {
        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "parent_id": category.parent_id,
                "created_at": category.created_at
            }
            for category in categories
        ],
        "total": len(categories)
    }

@categories_router.post("/")
async def create_category(
    category_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category."""
    from app.services.category import CategoryService
    from app.schemas.category import CategoryCreate
    
    user_id = get_current_user_id(credentials)
    
    try:
        create_data = CategoryCreate(
            name=category_data.get('name'),
            description=category_data.get('description'),
            parent_id=category_data.get('parent_id')
        )
        
        category_service = CategoryService(db)
        category = await category_service.create_category(user_id, create_data)
        
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "parent_id": category.parent_id,
            "created_at": category.created_at,
            "message": "Category created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create category: {str(e)}"
        )

# Add tags and categories routers
api_router.include_router(tags_router)
api_router.include_router(categories_router)

# Security endpoints
security_router = APIRouter(prefix="/security", tags=["security"])

@security_router.get("/status")
async def get_security_status(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get security status and configuration."""
    from app.core.security_advanced import SecurityConfig
    
    user_id = get_current_user_id(credentials)
    
    return {
        "security_features": {
            "rate_limiting": True,
            "brute_force_protection": True,
            "input_validation": True,
            "sql_injection_prevention": True,
            "xss_protection": True,
            "security_headers": True,
            "audit_logging": True,
            "session_management": True
        },
        "rate_limits": {
            "requests_per_window": SecurityConfig.RATE_LIMIT_REQUESTS,
            "window_seconds": SecurityConfig.RATE_LIMIT_WINDOW,
            "burst_allowance": SecurityConfig.RATE_LIMIT_BURST
        },
        "brute_force_protection": {
            "max_attempts": SecurityConfig.MAX_LOGIN_ATTEMPTS,
            "lockout_duration": SecurityConfig.LOGIN_LOCKOUT_DURATION
        },
        "session_config": {
            "timeout_seconds": SecurityConfig.SESSION_TIMEOUT,
            "max_sessions_per_user": SecurityConfig.MAX_SESSIONS_PER_USER
        },
        "input_limits": {
            "max_input_length": SecurityConfig.MAX_INPUT_LENGTH,
            "allowed_html_tags": list(SecurityConfig.ALLOWED_HTML_TAGS)
        }
    }

@security_router.get("/audit-log")
async def get_security_audit_log(
    limit: int = 50,
    event_type: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get security audit log (admin only)."""
    from app.core.security_advanced import redis_client
    import json
    from datetime import datetime
    
    user_id = get_current_user_id(credentials)
    
    # In a real implementation, check if user is admin
    # For now, return limited info
    
    if redis_client:
        try:
            today = datetime.utcnow().strftime('%Y-%m-%d')
            key = f"security_events:{today}"
            events = redis_client.lrange(key, 0, limit - 1)
            
            parsed_events = []
            for event in events:
                try:
                    event_data = json.loads(event)
                    # Filter sensitive information
                    filtered_event = {
                        "timestamp": event_data.get("timestamp"),
                        "event_type": event_data.get("event_type"),
                        "severity": event_data.get("severity"),
                        "user_id": event_data.get("user_id") if event_data.get("user_id") == user_id else "***"
                    }
                    if not event_type or event_data.get("event_type") == event_type:
                        parsed_events.append(filtered_event)
                except json.JSONDecodeError:
                    continue
            
            return {
                "events": parsed_events,
                "total": len(parsed_events),
                "date": today
            }
        except Exception as e:
            return {
                "events": [],
                "total": 0,
                "error": "Failed to retrieve audit log"
            }
    else:
        return {
            "events": [],
            "total": 0,
            "message": "Audit logging not available (Redis not configured)"
        }

@security_router.post("/report-incident")
async def report_security_incident(
    incident_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Report a security incident."""
    from app.core.security_advanced import SecurityAuditor, validate_request_security
    
    try:
        user_id = get_current_user_id(credentials)
        
        # Validate input
        validate_request_security(incident_data)
        
        incident_type = incident_data.get('type', 'UNKNOWN')
        description = incident_data.get('description', '')
        severity = incident_data.get('severity', 'MEDIUM')
        
        # Log the incident
        SecurityAuditor.log_security_event(
            f"USER_REPORTED_INCIDENT",
            user_id=user_id,
            details={
                "incident_type": incident_type,
                "description": description[:500],  # Limit description length
                "reported_by": user_id
            },
            severity=severity
        )
        
        return {
            "message": "Security incident reported successfully",
            "incident_id": f"INC-{int(time.time())}",
            "status": "recorded"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to report incident: {str(e)}"
        )

# Add security router
api_router.include_router(security_router)

# User info endpoint
@api_router.get("/me")
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current user information."""
    user_id = get_current_user_id(credentials)
    return {"user_id": user_id, "message": "User authenticated successfully"}