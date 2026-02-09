#!/usr/bin/env python3
"""
Database Configuration Validation Script

Simple validation script to test database configuration
without running the full test suite.
"""

import sys
import asyncio
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
backend_dir = project_root / "backend"

# Add backend directory to Python path
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ["TESTING"] = "true"

try:
    from app.core.database import (
        get_database_type,
        get_engine_config,
        DatabaseType,
        DatabaseHealthCheck
    )
    from app.core.config import get_settings
    from app.core.migrations import MigrationManager
    from app.core.connection_pool import ConnectionPoolManager
    
    print("✓ All database modules imported successfully")
    
    # Test basic functionality
    def test_database_type_detection():
        """Test database type detection."""
        print("\n--- Testing Database Type Detection ---")
        
        test_urls = [
            ("sqlite+aiosqlite:///test.db", "sqlite"),
            ("postgresql+asyncpg://user:pass@host/db", "postgresql"),
            ("mysql+aiomysql://user:pass@host/db", "mysql"),
            ("mongodb://user:pass@host/db", "mongodb"),
        ]
        
        for url, expected in test_urls:
            result = get_database_type(url)
            status = "✓" if result == expected else "✗"
            print(f"  {status} {url} -> {result} (expected: {expected})")
    
    def test_engine_configuration():
        """Test engine configuration."""
        print("\n--- Testing Engine Configuration ---")
        
        db_types = [DatabaseType.SQLITE, DatabaseType.POSTGRESQL, DatabaseType.MYSQL]
        
        for db_type in db_types:
            try:
                config = get_engine_config(db_type)
                print(f"  ✓ {db_type} configuration generated successfully")
                print(f"    - Pool class: {config.get('poolclass', 'Default')}")
                print(f"    - Pool pre-ping: {config.get('pool_pre_ping', False)}")
            except Exception as e:
                print(f"  ✗ {db_type} configuration failed: {e}")
    
    def test_settings_loading():
        """Test settings loading."""
        print("\n--- Testing Settings Loading ---")
        
        try:
            settings = get_settings()
            print(f"  ✓ Settings loaded successfully")
            print(f"    - Database URL: {settings.DATABASE_URL}")
            print(f"    - Pool size: {settings.DATABASE_POOL_SIZE}")
            print(f"    - Max overflow: {settings.DATABASE_MAX_OVERFLOW}")
        except Exception as e:
            print(f"  ✗ Settings loading failed: {e}")
    
    def test_migration_manager():
        """Test migration manager."""
        print("\n--- Testing Migration Manager ---")
        
        try:
            manager = MigrationManager()
            print("  ✓ Migration manager created successfully")
        except Exception as e:
            print(f"  ✗ Migration manager creation failed: {e}")
    
    def test_connection_pool_manager():
        """Test connection pool manager."""
        print("\n--- Testing Connection Pool Manager ---")
        
        try:
            manager = ConnectionPoolManager()
            print("  ✓ Connection pool manager created successfully")
            
            # Test recording connection time
            manager._record_connection_time(0.5)
            print(f"  ✓ Connection time recorded: {manager.stats.average_connection_time}")
        except Exception as e:
            print(f"  ✗ Connection pool manager test failed: {e}")
    
    async def test_health_check():
        """Test health check functionality."""
        print("\n--- Testing Health Check ---")
        
        try:
            # Test with no engine (should handle gracefully)
            result = await DatabaseHealthCheck.check_sql_health()
            print(f"  ✓ SQL health check completed: {result['status']}")
            
            result = await DatabaseHealthCheck.check_mongodb_health()
            print(f"  ✓ MongoDB health check completed: {result['status']}")
        except Exception as e:
            print(f"  ✗ Health check failed: {e}")
    
    def main():
        """Run all validation tests."""
        print("Database Configuration Validation")
        print("=" * 50)
        
        test_database_type_detection()
        test_engine_configuration()
        test_settings_loading()
        test_migration_manager()
        test_connection_pool_manager()
        
        # Run async tests
        asyncio.run(test_health_check())
        
        print("\n" + "=" * 50)
        print("Validation completed!")
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)