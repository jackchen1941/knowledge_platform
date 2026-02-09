"""
Enhanced FastAPI Application

An enhanced version with more functionality while avoiding complex imports.
"""

import sys
import os
from contextlib import asynccontextmanager

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import init_database, get_db_session
from app.core.security import security, get_current_user_id
from app.core.security_advanced import SecurityMiddleware, validate_request_security
from app.api.v1.api_simple import api_router
from app.api.v1.endpoints.websocket import router as websocket_router

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
    description="Knowledge Management Platform API - Enhanced Version",
    version="1.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
security_middleware = SecurityMiddleware()
app.middleware("http")(security_middleware)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Knowledge Management Platform API - Enhanced",
        "version": "1.1.0",
        "status": "running",
        "features": [
            "User Authentication",
            "Knowledge Management", 
            "Multi-device Sync",
            "Search & Analytics",
            "Import/Export"
        ]
    }


@app.get("/status")
async def system_status():
    """System status endpoint."""
    try:
        # Test database connection
        async with get_db_session() as db:
            from sqlalchemy import text
            result = await db.execute(text("SELECT 1"))
            db_status = "connected" if result else "error"
        
        return {
            "status": "healthy",
            "database": db_status,
            "version": "1.1.0",
            "timestamp": "2026-02-09T20:45:00Z"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/features")
async def list_features():
    """List available features."""
    return {
        "authentication": {
            "status": "available",
            "endpoints": ["/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/me"]
        },
        "sync": {
            "status": "available", 
            "endpoints": ["/api/v1/sync/devices", "/api/v1/sync/pull", "/api/v1/sync/push"]
        },
        "knowledge": {
            "status": "available",
            "endpoints": ["/api/v1/knowledge/test"]
        },
        "notifications": {
            "status": "available",
            "endpoints": ["/api/v1/notifications/test", "/api/v1/notifications/demo"]
        },
        "websocket": {
            "status": "available",
            "endpoints": ["/api/v1/ws/test", "/api/v1/ws/{user_id}"]
        }
    }


# Authentication test endpoint
@app.get("/auth/test")
async def test_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Test authentication."""
    try:
        user_id = get_current_user_id(credentials)
        return {
            "authenticated": True,
            "user_id": user_id,
            "message": "Authentication successful"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


# Database test endpoint
@app.get("/db/test")
async def test_database():
    """Test database functionality."""
    try:
        async with get_db_session() as db:
            from sqlalchemy import text
            from app.models.user import User
            from app.models.sync import SyncDevice
            
            # Test basic query
            result = await db.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
            # Test model queries
            user_count = await db.execute(text("SELECT COUNT(*) FROM users"))
            device_count = await db.execute(text("SELECT COUNT(*) FROM sync_devices"))
            
            return {
                "database": "connected",
                "test_query": test_value,
                "users": user_count.scalar(),
                "devices": device_count.scalar(),
                "tables": ["users", "sync_devices", "sync_changes", "sync_conflicts"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")


# Include API router
app.include_router(api_router, prefix="/api/v1")

# Include WebSocket router
app.include_router(websocket_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )