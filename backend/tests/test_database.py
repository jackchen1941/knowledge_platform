"""
Database Configuration Tests

Test suite for database connection, configuration,
and management functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import (
    get_database_type,
    get_engine_config,
    create_database_engine,
    init_database,
    test_database_connection,
    test_mongodb_connection,
    get_db_session,
    DatabaseHealthCheck,
    DatabaseType,
)
from app.core.database_init import DatabaseInitializer
from app.core.migrations import MigrationManager
from app.core.connection_pool import ConnectionPoolManager
from app.core.config import get_settings


class TestDatabaseConfiguration:
    """Test database configuration and setup."""
    
    def test_get_database_type(self):
        """Test database type detection from URL."""
        assert get_database_type("sqlite+aiosqlite:///test.db") == "sqlite"
        assert get_database_type("postgresql+asyncpg://user:pass@host/db") == "postgresql"
        assert get_database_type("mysql+aiomysql://user:pass@host/db") == "mysql"
        assert get_database_type("mongodb://user:pass@host/db") == "mongodb"
    
    def test_get_engine_config_sqlite(self):
        """Test SQLite engine configuration."""
        config = get_engine_config(DatabaseType.SQLITE)
        
        assert config["poolclass"].__name__ == "StaticPool"
        assert config["connect_args"]["check_same_thread"] is False
        assert config["connect_args"]["timeout"] == 20
        assert config["pool_pre_ping"] is True
    
    def test_get_engine_config_postgresql(self):
        """Test PostgreSQL engine configuration."""
        with patch('app.core.database.settings') as mock_settings:
            mock_settings.DATABASE_POOL_SIZE = 10
            mock_settings.DATABASE_MAX_OVERFLOW = 20
            mock_settings.APP_NAME = "Test App"
            mock_settings.DATABASE_SSL_MODE = None
            
            config = get_engine_config(DatabaseType.POSTGRESQL)
            
            assert config["pool_size"] == 10
            assert config["max_overflow"] == 20
            assert config["connect_args"]["server_settings"]["application_name"] == "Test App"
    
    def test_get_engine_config_mysql(self):
        """Test MySQL engine configuration."""
        with patch('app.core.database.settings') as mock_settings:
            mock_settings.DATABASE_POOL_SIZE = 5
            mock_settings.DATABASE_MAX_OVERFLOW = 10
            
            config = get_engine_config(DatabaseType.MYSQL)
            
            assert config["pool_size"] == 5
            assert config["max_overflow"] == 10
            assert config["connect_args"]["charset"] == "utf8mb4"


class TestDatabaseConnection:
    """Test database connection functionality."""
    
    @pytest.mark.asyncio
    async def test_create_database_engine(self):
        """Test database engine creation."""
        with patch('app.core.database.settings') as mock_settings:
            mock_settings.DATABASE_URL = "sqlite+aiosqlite:///test.db"
            mock_settings.DATABASE_ECHO = False
            
            with patch('app.core.database.create_async_engine') as mock_create_engine:
                mock_engine = Mock()
                mock_engine.sync_engine = Mock()
                mock_create_engine.return_value = mock_engine
                
                engine = await create_database_engine()
                
                assert engine == mock_engine
                mock_create_engine.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_database_connection_success(self):
        """Test successful database connection test."""
        with patch('app.core.database.async_engine') as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn
            
            result = await test_database_connection()
            
            assert result is True
            mock_conn.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_database_connection_failure(self):
        """Test failed database connection test."""
        with patch('app.core.database.async_engine') as mock_engine:
            mock_engine.begin.side_effect = Exception("Connection failed")
            
            result = await test_database_connection()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_db_session_success(self):
        """Test successful database session creation."""
        with patch('app.core.database.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None
            
            async with get_db_session() as session:
                assert session == mock_session
    
    @pytest.mark.asyncio
    async def test_get_db_session_error_handling(self):
        """Test database session error handling."""
        with patch('app.core.database.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None
            
            with pytest.raises(Exception):
                async with get_db_session() as session:
                    raise Exception("Test error")
            
            mock_session.rollback.assert_called_once()


class TestDatabaseHealthCheck:
    """Test database health monitoring."""
    
    @pytest.mark.asyncio
    async def test_check_sql_health_success(self):
        """Test successful SQL health check."""
        with patch('app.core.database.async_engine') as mock_engine:
            mock_conn = AsyncMock()
            mock_result = Mock()
            mock_result.fetchone.return_value = [1]
            mock_conn.execute.return_value = mock_result
            
            mock_pool = Mock()
            mock_pool.size.return_value = 5
            mock_pool.checkedin.return_value = 3
            mock_pool.checkedout.return_value = 2
            mock_pool.overflow.return_value = 0
            mock_engine.pool = mock_pool
            
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn
            
            result = await DatabaseHealthCheck.check_sql_health()
            
            assert result["status"] == "healthy"
            assert result["response"] == 1
            assert "pool_status" in result
    
    @pytest.mark.asyncio
    async def test_check_sql_health_failure(self):
        """Test failed SQL health check."""
        with patch('app.core.database.async_engine') as mock_engine:
            mock_engine.begin.side_effect = Exception("Database error")
            
            result = await DatabaseHealthCheck.check_sql_health()
            
            assert result["status"] == "unhealthy"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_check_mongodb_health_success(self):
        """Test successful MongoDB health check."""
        with patch('app.core.database.mongodb_client') as mock_client:
            mock_client.admin.command.return_value = {"ok": 1}
            mock_client.server_info.return_value = {"version": "4.4.0"}
            
            result = await DatabaseHealthCheck.check_mongodb_health()
            
            assert result["status"] == "healthy"
            assert result["server_version"] == "4.4.0"
    
    @pytest.mark.asyncio
    async def test_check_mongodb_health_not_configured(self):
        """Test MongoDB health check when not configured."""
        with patch('app.core.database.mongodb_client', None):
            result = await DatabaseHealthCheck.check_mongodb_health()
            
            assert result["status"] == "not_configured"


class TestDatabaseInitializer:
    """Test database initialization functionality."""
    
    @pytest.mark.asyncio
    async def test_initialize_all_success(self):
        """Test successful database initialization."""
        initializer = DatabaseInitializer()
        
        with patch.multiple(
            'app.core.database_init',
            init_database=AsyncMock(),
            run_migrations=AsyncMock(return_value={"sql_migration": {"status": "success"}}),
        ):
            with patch.object(initializer, '_initialize_sql_database', return_value={"status": "success", "actions": []}):
                with patch.object(initializer, '_setup_database_security', return_value={"status": "success", "actions": []}):
                    with patch.object(initializer, '_seed_initial_data', return_value={"status": "success", "actions": []}):
                        with patch('app.core.database_init.DatabaseHealthCheck.full_health_check', return_value={}):
                            
                            result = await initializer.initialize_all()
                            
                            assert "sql_database" in result
                            assert "migrations" in result
                            assert "security" in result
                            assert "seed_data" in result
    
    @pytest.mark.asyncio
    async def test_initialize_sql_database_sqlite(self):
        """Test SQLite database initialization."""
        initializer = DatabaseInitializer()
        
        with patch('app.core.database_init.get_database_type', return_value="sqlite"):
            with patch('app.core.database_init.test_database_connection', return_value=True):
                with patch('app.core.database_init.create_tables'):
                    with patch.object(initializer, '_optimize_sqlite'):
                        
                        result = await initializer._initialize_sql_database()
                        
                        assert result["status"] == "success"
                        assert "connection_tested" in result["actions"]
                        assert "tables_created" in result["actions"]
                        assert "sqlite_optimized" in result["actions"]


class TestMigrationManager:
    """Test database migration management."""
    
    def test_migration_manager_init(self):
        """Test migration manager initialization."""
        with patch('app.core.migrations.Config') as mock_config:
            with patch('app.core.migrations.ScriptDirectory') as mock_script_dir:
                manager = MigrationManager()
                
                mock_config.assert_called_once_with("alembic.ini")
                mock_script_dir.from_config.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_revision(self):
        """Test getting current database revision."""
        manager = MigrationManager()
        
        with patch('app.core.migrations.async_engine') as mock_engine:
            mock_conn = AsyncMock()
            mock_context = Mock()
            mock_context.get_current_revision.return_value = "abc123"
            
            with patch('app.core.migrations.MigrationContext.configure', return_value=mock_context):
                mock_engine.connect.return_value.__aenter__.return_value = mock_conn
                
                revision = await manager.get_current_revision()
                
                assert revision == "abc123"
    
    def test_create_migration(self):
        """Test creating a new migration."""
        manager = MigrationManager()
        
        with patch('app.core.migrations.command.revision') as mock_revision:
            result = manager.create_migration("test migration", autogenerate=True)
            
            assert result == "success"
            mock_revision.assert_called_once()


class TestConnectionPoolManager:
    """Test connection pool management."""
    
    def test_connection_pool_manager_init(self):
        """Test connection pool manager initialization."""
        manager = ConnectionPoolManager()
        
        assert manager.stats.total_connections == 0
        assert manager.stats.active_connections == 0
        assert manager.stats.failed_connections == 0
        assert manager.connection_times == []
    
    def test_record_connection_time(self):
        """Test recording connection times."""
        manager = ConnectionPoolManager()
        
        manager._record_connection_time(0.5)
        manager._record_connection_time(0.3)
        manager._record_connection_time(0.7)
        
        assert len(manager.connection_times) == 3
        assert manager.stats.average_connection_time == 0.5
    
    def test_get_pool_metrics(self):
        """Test getting pool metrics."""
        manager = ConnectionPoolManager()
        
        mock_engine = Mock()
        mock_pool = Mock()
        mock_pool.size.return_value = 5
        mock_pool._max_overflow = 10
        mock_pool.checkedout.return_value = 2
        mock_pool.checkedin.return_value = 3
        mock_pool.overflow.return_value = 0
        mock_pool.invalid.return_value = 0
        mock_engine.pool = mock_pool
        
        metrics = manager.get_pool_metrics(mock_engine)
        
        assert metrics.pool_size == 5
        assert metrics.max_overflow == 10
        assert metrics.checked_out == 2
        assert metrics.utilization_percentage == 40.0  # 2/5 * 100
    
    def test_get_pool_health_status_healthy(self):
        """Test pool health status when healthy."""
        manager = ConnectionPoolManager()
        
        mock_engine = Mock()
        mock_pool = Mock()
        mock_pool.size.return_value = 10
        mock_pool._max_overflow = 5
        mock_pool.checkedout.return_value = 3
        mock_pool.checkedin.return_value = 7
        mock_pool.overflow.return_value = 0
        mock_pool.invalid.return_value = 0
        mock_engine.pool = mock_pool
        
        # Set some stats
        manager.stats.total_requests = 100
        manager.stats.failed_connections = 1
        
        health_status = manager.get_pool_health_status(mock_engine)
        
        assert health_status["health_status"] == "healthy"
        assert health_status["utilization_percentage"] == 30.0
        assert health_status["error_rate_percentage"] == 1.0
        assert len(health_status["recommendations"]) == 0
    
    def test_get_pool_health_status_warning(self):
        """Test pool health status when warning."""
        manager = ConnectionPoolManager()
        
        mock_engine = Mock()
        mock_pool = Mock()
        mock_pool.size.return_value = 10
        mock_pool._max_overflow = 5
        mock_pool.checkedout.return_value = 9  # High utilization
        mock_pool.checkedin.return_value = 1
        mock_pool.overflow.return_value = 0
        mock_pool.invalid.return_value = 0
        mock_engine.pool = mock_pool
        
        # Set some stats
        manager.stats.total_requests = 100
        manager.stats.failed_connections = 1
        
        health_status = manager.get_pool_health_status(mock_engine)
        
        assert health_status["health_status"] == "warning"
        assert health_status["utilization_percentage"] == 90.0
        assert "Consider increasing pool size" in health_status["recommendations"]


@pytest.fixture
async def test_database():
    """Fixture for test database setup."""
    # This would set up a test database
    # For now, we'll use mocks in the actual tests
    yield
    # Cleanup would go here


class TestIntegration:
    """Integration tests for database functionality."""
    
    @pytest.mark.asyncio
    async def test_full_database_initialization_flow(self):
        """Test complete database initialization flow."""
        with patch('app.core.database.settings') as mock_settings:
            mock_settings.DATABASE_URL = "sqlite+aiosqlite:///test.db"
            mock_settings.MONGODB_URL = None
            
            with patch('app.core.database.create_async_engine') as mock_create_engine:
                mock_engine = Mock()
                mock_engine.sync_engine = Mock()
                mock_create_engine.return_value = mock_engine
                
                with patch('app.core.database.async_sessionmaker') as mock_session_maker:
                    with patch('app.core.database.test_database_connection', return_value=True):
                        
                        await init_database()
                        
                        mock_create_engine.assert_called_once()
                        mock_session_maker.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_database_session_lifecycle(self):
        """Test complete database session lifecycle."""
        with patch('app.core.database.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None
            
            # Test successful operation
            async with get_db_session() as session:
                await session.execute(text("SELECT 1"))
            
            mock_session.execute.assert_called_once()
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_integration(self):
        """Test integrated health check functionality."""
        with patch('app.core.database.async_engine') as mock_engine:
            with patch('app.core.database.mongodb_client') as mock_mongo:
                # Setup SQL engine mock
                mock_conn = AsyncMock()
                mock_result = Mock()
                mock_result.fetchone.return_value = [1]
                mock_conn.execute.return_value = mock_result
                
                mock_pool = Mock()
                mock_pool.size.return_value = 5
                mock_pool.checkedin.return_value = 3
                mock_pool.checkedout.return_value = 2
                mock_pool.overflow.return_value = 0
                mock_engine.pool = mock_pool
                mock_engine.begin.return_value.__aenter__.return_value = mock_conn
                
                # Setup MongoDB mock
                mock_mongo.admin.command.return_value = {"ok": 1}
                mock_mongo.server_info.return_value = {"version": "4.4.0"}
                
                result = await DatabaseHealthCheck.full_health_check()
                
                assert result["sql_database"]["status"] == "healthy"
                assert result["mongodb"]["status"] == "healthy"
                assert "timestamp" in result