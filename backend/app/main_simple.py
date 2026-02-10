"""
Simple FastAPI Application

A simplified version of the main app that only includes working endpoints.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import init_database
from app.api.v1.endpoints import (
    auth,
    knowledge,
    categories,
    tags,
    search,
    analytics,
    attachments,
    users,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    try:
        await init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    
    yield
    
    # Shutdown
    print("🔄 Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Knowledge Management Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(tags.router, prefix="/api/v1/tags", tags=["tags"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(attachments.router, prefix="/api/v1", tags=["attachments"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Knowledge Management Platform API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2026-02-09T09:45:00Z"
    }


@app.get("/api/v1/sync/test")
async def sync_test():
    """Test sync functionality."""
    try:
        from app.services.sync import SyncService
        from app.core.database import get_db_session
        
        async with get_db_session() as db:
            sync_service = SyncService(db)
            
            # Test basic functionality
            stats = {
                "message": "Sync service is working",
                "service_loaded": True,
                "database_connected": True
            }
            
            return stats
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync test failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )