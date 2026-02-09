"""
Database Configuration and Connection Management

This module provides database connectivity for multiple database types
with async support, connection pooling, and comprehensive error handling.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Optional, Union
from urllib.parse import urlparse
import ssl

from sqlalchemy import MetaData, create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, NullPool, StaticPool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from loguru import logger
import motor.motor_asyncio
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import get_settings

settings = get_settings()

# Import connection pool manager
try:
    from app.core.connection_pool import ConnectionPoolManager, pool_manager
except ImportError:
    # Fallback if connection_pool module is not available
    pool_manager = None

# SQLAlchemy setup
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)
Base = declarative_base(metadata=metadata)

# Database engines and sessions
async_engine: Optional[AsyncEngine] = None
AsyncSessionLocal: Optional[async_sessionmaker] = None
mongodb_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
mongodb_database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None


class DatabaseType:
    """Database type constants."""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"


def get_database_type(url: str) -> str:
    """Determine database type from URL."""
    parsed = urlparse(url)
    scheme = parsed.scheme.split('+')[0]
    return scheme


def get_engine_config(db_type: str) -> Dict[str, Any]:
    """Get database-specific engine configuration."""
    base_config = {
        "echo": settings.DATABASE_ECHO,
        "pool_pre_ping": True,
        "pool_recycle": 3600,  # 1 hour
        "connect_args": {},
    }
    
    if db_type == DatabaseType.SQLITE:
        base_config.update({
            "poolclass": StaticPool,
            "connect_args": {
                "check_same_thread": False,
                "timeout": 20,
            }
        })
    elif db_type == DatabaseType.POSTGRESQL:
        base_config.update({
            "poolclass": QueuePool,
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": 30,
            "connect_args": {
                "server_settings": {
                    "application_name": settings.APP_NAME,
                    "jit": "off",
                },
                "command_timeout": 60,
            }
        })
        # Add SSL configuration if specified
        if settings.DATABASE_SSL_MODE:
            ssl_context = ssl.create_default_context()
            if settings.DATABASE_SSL_MODE == "require":
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            base_config["connect_args"]["ssl"] = ssl_context
            
    elif db_type == DatabaseType.MYSQL:
        base_config.update({
            "poolclass": QueuePool,
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": 30,
            "connect_args": {
                "charset": "utf8mb4",
                "autocommit": False,
                "connect_timeout": 60,
            }
        })
    
    return base_config


async def create_database_engine() -> AsyncEngine:
    """Create and configure database engine based on database type."""
    db_type = get_database_type(settings.DATABASE_URL)
    engine_config = get_engine_config(db_type)
    
    logger.info(f"Creating {db_type} database engine")
    
    engine = create_async_engine(settings.DATABASE_URL, **engine_config)
    
    # Register pool monitoring if available
    if pool_manager:
        pool_manager.register_pool_events(engine)
    
    # Add event listeners for connection management
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set SQLite pragmas for better performance and integrity."""
        if db_type == DatabaseType.SQLITE:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=1000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
    
    return engine


async def init_mongodb() -> None:
    """Initialize MongoDB connection."""
    global mongodb_client, mongodb_database
    
    if not settings.MONGODB_URL:
        return
        
    try:
        mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=settings.DATABASE_POOL_SIZE,
            minPoolSize=1,
            maxIdleTimeMS=30000,
        )
        
        # Test connection
        await mongodb_client.admin.command('ping')
        
        # Get database name from URL or use default
        parsed_url = urlparse(settings.MONGODB_URL)
        db_name = parsed_url.path.lstrip('/') or settings.MONGODB_DATABASE
        mongodb_database = mongodb_client[db_name]
        
        logger.info(f"MongoDB connected successfully to database: {db_name}")
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise


async def init_database() -> None:
    """Initialize database connections and engines."""
    global async_engine, AsyncSessionLocal
    
    try:
        # Initialize SQL database
        if settings.DATABASE_URL:
            async_engine = await create_database_engine()
            AsyncSessionLocal = async_sessionmaker(
                async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
            
            # Test connection
            await test_database_connection()
            
            # Start pool monitoring if available
            if pool_manager:
                await pool_manager.start_monitoring(async_engine)
            
            logger.info("SQL database initialized successfully")
        
        # Initialize MongoDB if configured
        if settings.MONGODB_URL:
            await init_mongodb()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def test_database_connection() -> bool:
    """Test database connection health."""
    if not async_engine:
        return False
        
    try:
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def test_mongodb_connection() -> bool:
    """Test MongoDB connection health."""
    if not mongodb_client:
        return False
        
    try:
        await mongodb_client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {e}")
        return False


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with proper error handling."""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not initialized")
        
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected database error: {e}")
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session (FastAPI compatible)."""
    async with get_db_session() as session:
        yield session


def get_mongodb() -> Optional[motor.motor_asyncio.AsyncIOMotorDatabase]:
    """Get MongoDB database instance."""
    return mongodb_database


async def create_tables() -> None:
    """Create all database tables."""
    if not async_engine:
        raise RuntimeError("Database engine not initialized")
        
    try:
        async with async_engine.begin() as conn:
            # Import all models to ensure they are registered
            from app.models import user, knowledge, category, tag, attachment, import_config
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Table creation failed: {e}")
        raise


async def drop_tables() -> None:
    """Drop all database tables (use with caution)."""
    if not async_engine:
        raise RuntimeError("Database engine not initialized")
        
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Table dropping failed: {e}")
        raise


async def init_db() -> None:
    """Initialize database tables."""
    await create_tables()


async def close_db() -> None:
    """Close database connections."""
    global async_engine, mongodb_client
    
    try:
        if async_engine:
            await async_engine.dispose()
            logger.info("SQL database connections closed")
            
        if mongodb_client:
            mongodb_client.close()
            logger.info("MongoDB connections closed")
            
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


async def get_database_info() -> Dict[str, Any]:
    """Get database connection information."""
    info = {
        "sql_database": {
            "connected": await test_database_connection(),
            "type": get_database_type(settings.DATABASE_URL) if settings.DATABASE_URL else None,
            "url": settings.DATABASE_URL.split('@')[-1] if settings.DATABASE_URL else None,  # Hide credentials
        },
        "mongodb": {
            "connected": await test_mongodb_connection(),
            "url": settings.MONGODB_URL.split('@')[-1] if settings.MONGODB_URL else None,  # Hide credentials
        }
    }
    return info


# Database health check utilities
class DatabaseHealthCheck:
    """Database health monitoring utilities."""
    
    @staticmethod
    async def check_sql_health() -> Dict[str, Any]:
        """Check SQL database health."""
        if not async_engine:
            return {"status": "not_initialized", "error": "Database engine not initialized"}
            
        try:
            async with async_engine.begin() as conn:
                result = await conn.execute(text("SELECT 1 as health_check"))
                row = result.fetchone()
                
                # Get connection pool status
                pool = async_engine.pool
                pool_status = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                }
                
                return {
                    "status": "healthy",
                    "response": row[0] if row else None,
                    "pool_status": pool_status,
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_mongodb_health() -> Dict[str, Any]:
        """Check MongoDB health."""
        if not mongodb_client:
            return {"status": "not_configured"}
            
        try:
            result = await mongodb_client.admin.command('ping')
            server_info = await mongodb_client.server_info()
            
            return {
                "status": "healthy",
                "ping_response": result,
                "server_version": server_info.get("version"),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def full_health_check() -> Dict[str, Any]:
        """Perform comprehensive database health check."""
        return {
            "sql_database": await DatabaseHealthCheck.check_sql_health(),
            "mongodb": await DatabaseHealthCheck.check_mongodb_health(),
            "timestamp": asyncio.get_event_loop().time(),
        }


# Transaction management utilities
@asynccontextmanager
async def database_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database transactions with automatic rollback on error."""
    async with get_db_session() as session:
        try:
            await session.begin()
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def execute_in_transaction(func, *args, **kwargs):
    """Execute a function within a database transaction."""
    async with database_transaction() as session:
        return await func(session, *args, **kwargs)