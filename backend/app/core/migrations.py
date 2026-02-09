"""
Database Migration Management

This module provides utilities for managing database migrations,
version control, and schema updates across different database types.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncConnection
from loguru import logger

from app.core.database import async_engine, get_database_type, mongodb_database
from app.core.config import get_settings

settings = get_settings()


class MigrationManager:
    """Manages database migrations and version control."""
    
    def __init__(self):
        self.alembic_cfg = Config("alembic.ini")
        self.script_dir = ScriptDirectory.from_config(self.alembic_cfg)
    
    async def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        if not async_engine:
            return None
            
        try:
            async with async_engine.connect() as conn:
                context = MigrationContext.configure(
                    await conn.get_raw_connection(), 
                    opts={}
                )
                return context.get_current_revision()
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None
    
    async def get_head_revision(self) -> Optional[str]:
        """Get the latest available revision."""
        try:
            return self.script_dir.get_current_head()
        except Exception as e:
            logger.error(f"Failed to get head revision: {e}")
            return None
    
    async def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history."""
        history = []
        try:
            for revision in self.script_dir.walk_revisions():
                history.append({
                    "revision": revision.revision,
                    "down_revision": revision.down_revision,
                    "branch_labels": revision.branch_labels,
                    "depends_on": revision.depends_on,
                    "doc": revision.doc,
                    "create_date": revision.create_date,
                })
            return history
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []
    
    async def check_migration_status(self) -> Dict[str, Any]:
        """Check if database needs migration."""
        current = await self.get_current_revision()
        head = await self.get_head_revision()
        
        return {
            "current_revision": current,
            "head_revision": head,
            "needs_migration": current != head,
            "is_up_to_date": current == head,
        }
    
    def create_migration(self, message: str, autogenerate: bool = True) -> str:
        """Create a new migration."""
        try:
            if autogenerate:
                command.revision(
                    self.alembic_cfg, 
                    message=message, 
                    autogenerate=True
                )
            else:
                command.revision(
                    self.alembic_cfg, 
                    message=message
                )
            logger.info(f"Created migration: {message}")
            return "success"
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            return f"error: {e}"
    
    def upgrade_database(self, revision: str = "head") -> str:
        """Upgrade database to specified revision."""
        try:
            command.upgrade(self.alembic_cfg, revision)
            logger.info(f"Database upgraded to revision: {revision}")
            return "success"
        except Exception as e:
            logger.error(f"Failed to upgrade database: {e}")
            return f"error: {e}"
    
    def downgrade_database(self, revision: str) -> str:
        """Downgrade database to specified revision."""
        try:
            command.downgrade(self.alembic_cfg, revision)
            logger.info(f"Database downgraded to revision: {revision}")
            return "success"
        except Exception as e:
            logger.error(f"Failed to downgrade database: {e}")
            return f"error: {e}"
    
    async def backup_before_migration(self) -> Optional[str]:
        """Create database backup before migration."""
        db_type = get_database_type(settings.DATABASE_URL)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if db_type == "sqlite":
            return await self._backup_sqlite(timestamp)
        elif db_type == "postgresql":
            return await self._backup_postgresql(timestamp)
        elif db_type == "mysql":
            return await self._backup_mysql(timestamp)
        else:
            logger.warning(f"Backup not implemented for {db_type}")
            return None
    
    async def _backup_sqlite(self, timestamp: str) -> Optional[str]:
        """Backup SQLite database."""
        try:
            import shutil
            from urllib.parse import urlparse
            
            parsed_url = urlparse(settings.DATABASE_URL)
            db_path = parsed_url.path.lstrip('/')
            
            if os.path.exists(db_path):
                backup_path = f"{db_path}.backup_{timestamp}"
                shutil.copy2(db_path, backup_path)
                logger.info(f"SQLite backup created: {backup_path}")
                return backup_path
        except Exception as e:
            logger.error(f"SQLite backup failed: {e}")
        return None
    
    async def _backup_postgresql(self, timestamp: str) -> Optional[str]:
        """Backup PostgreSQL database."""
        try:
            from urllib.parse import urlparse
            import subprocess
            
            parsed_url = urlparse(settings.DATABASE_URL)
            backup_file = f"backup_postgresql_{timestamp}.sql"
            
            cmd = [
                "pg_dump",
                f"--host={parsed_url.hostname}",
                f"--port={parsed_url.port or 5432}",
                f"--username={parsed_url.username}",
                f"--dbname={parsed_url.path.lstrip('/')}",
                f"--file={backup_file}",
                "--verbose",
                "--no-password"
            ]
            
            env = os.environ.copy()
            if parsed_url.password:
                env["PGPASSWORD"] = parsed_url.password
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"PostgreSQL backup created: {backup_file}")
                return backup_file
            else:
                logger.error(f"PostgreSQL backup failed: {result.stderr}")
        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
        return None
    
    async def _backup_mysql(self, timestamp: str) -> Optional[str]:
        """Backup MySQL database."""
        try:
            from urllib.parse import urlparse
            import subprocess
            
            parsed_url = urlparse(settings.DATABASE_URL)
            backup_file = f"backup_mysql_{timestamp}.sql"
            
            cmd = [
                "mysqldump",
                f"--host={parsed_url.hostname}",
                f"--port={parsed_url.port or 3306}",
                f"--user={parsed_url.username}",
                f"--password={parsed_url.password}",
                "--single-transaction",
                "--routines",
                "--triggers",
                parsed_url.path.lstrip('/'),
            ]
            
            with open(backup_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                logger.info(f"MySQL backup created: {backup_file}")
                return backup_file
            else:
                logger.error(f"MySQL backup failed: {result.stderr}")
                os.remove(backup_file)  # Remove empty file
        except Exception as e:
            logger.error(f"MySQL backup failed: {e}")
        return None


class MongoMigrationManager:
    """Manages MongoDB schema migrations and version control."""
    
    def __init__(self):
        self.migrations_collection = "schema_migrations"
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        if not mongodb_database:
            return []
            
        try:
            cursor = mongodb_database[self.migrations_collection].find(
                {}, {"migration_id": 1}
            ).sort("applied_at", 1)
            
            migrations = []
            async for doc in cursor:
                migrations.append(doc["migration_id"])
            return migrations
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    async def apply_migration(self, migration_id: str, migration_func) -> bool:
        """Apply a MongoDB migration."""
        if not mongodb_database:
            return False
            
        try:
            # Check if migration already applied
            existing = await mongodb_database[self.migrations_collection].find_one(
                {"migration_id": migration_id}
            )
            
            if existing:
                logger.info(f"Migration {migration_id} already applied")
                return True
            
            # Apply migration
            await migration_func(mongodb_database)
            
            # Record migration
            await mongodb_database[self.migrations_collection].insert_one({
                "migration_id": migration_id,
                "applied_at": datetime.utcnow(),
            })
            
            logger.info(f"Applied MongoDB migration: {migration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_id}: {e}")
            return False
    
    async def create_indexes(self) -> bool:
        """Create recommended indexes for MongoDB collections."""
        if not mongodb_database:
            return False
            
        try:
            # Knowledge items indexes
            await mongodb_database.knowledge_items.create_index([
                ("user_id", 1), ("created_at", -1)
            ])
            await mongodb_database.knowledge_items.create_index([
                ("title", "text"), ("content", "text")
            ])
            await mongodb_database.knowledge_items.create_index([
                ("tags", 1)
            ])
            
            # Users indexes
            await mongodb_database.users.create_index([
                ("email", 1)
            ], unique=True)
            await mongodb_database.users.create_index([
                ("username", 1)
            ], unique=True)
            
            logger.info("MongoDB indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB indexes: {e}")
            return False


# Migration utilities
async def run_migrations() -> Dict[str, Any]:
    """Run all pending migrations."""
    results = {}
    
    # SQL migrations
    if async_engine:
        migration_manager = MigrationManager()
        status = await migration_manager.check_migration_status()
        
        if status["needs_migration"]:
            # Create backup
            backup_file = await migration_manager.backup_before_migration()
            
            # Run migration
            result = migration_manager.upgrade_database()
            results["sql_migration"] = {
                "status": result,
                "backup_file": backup_file,
                "previous_revision": status["current_revision"],
                "new_revision": status["head_revision"],
            }
        else:
            results["sql_migration"] = {"status": "up_to_date"}
    
    # MongoDB migrations
    if mongodb_database:
        mongo_manager = MongoMigrationManager()
        index_result = await mongo_manager.create_indexes()
        results["mongodb_migration"] = {
            "indexes_created": index_result,
        }
    
    return results


async def get_migration_status() -> Dict[str, Any]:
    """Get comprehensive migration status."""
    status = {}
    
    if async_engine:
        migration_manager = MigrationManager()
        status["sql"] = await migration_manager.check_migration_status()
        status["sql"]["history"] = await migration_manager.get_migration_history()
    
    if mongodb_database:
        mongo_manager = MongoMigrationManager()
        status["mongodb"] = {
            "applied_migrations": await mongo_manager.get_applied_migrations(),
        }
    
    return status