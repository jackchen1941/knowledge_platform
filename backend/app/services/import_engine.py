"""
Import Engine

Extensible framework for importing content from external platforms.
"""

import uuid
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.knowledge import KnowledgeItem
from app.models.import_config import ImportConfig, ImportTask
from app.core.exceptions import ValidationError, NotFoundError


class ImportAdapter(ABC):
    """Base class for platform-specific import adapters."""
    
    platform_name: str = "base"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """Validate adapter configuration."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to the platform."""
        pass
    
    @abstractmethod
    async def fetch_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch items from the platform.
        Returns list of raw item data.
        """
        pass
    
    @abstractmethod
    def transform_item(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform platform-specific data to standard format.
        Returns dict with keys: title, content, summary, tags, etc.
        """
        pass
    
    def clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        # Remove excessive whitespace
        content = "\n".join(line.strip() for line in content.split("\n"))
        # Remove multiple blank lines
        while "\n\n\n" in content:
            content = content.replace("\n\n\n", "\n\n")
        return content.strip()


class ImportEngine:
    """Main import engine that manages adapters and import tasks."""
    
    # Registry of available adapters
    _adapters: Dict[str, Type[ImportAdapter]] = {}
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @classmethod
    def register_adapter(cls, adapter_class: Type[ImportAdapter]) -> None:
        """Register a new import adapter."""
        cls._adapters[adapter_class.platform_name] = adapter_class
        logger.info(f"Registered import adapter: {adapter_class.platform_name}")
    
    @classmethod
    def get_available_platforms(cls) -> List[str]:
        """Get list of available platform names."""
        return list(cls._adapters.keys())
    
    def get_adapter(self, platform: str, config: Dict[str, Any]) -> ImportAdapter:
        """Get an adapter instance for a platform."""
        adapter_class = self._adapters.get(platform)
        if not adapter_class:
            raise ValidationError(f"No adapter found for platform: {platform}")
        return adapter_class(config)
    
    async def create_import_config(
        self,
        user_id: str,
        platform: str,
        config: Dict[str, Any],
        name: Optional[str] = None
    ) -> ImportConfig:
        """Create and save an import configuration."""
        
        # Validate platform
        if platform not in self._adapters:
            raise ValidationError(f"Unsupported platform: {platform}")
        
        # Test connection
        adapter = self.get_adapter(platform, config)
        try:
            connection_ok = await adapter.test_connection()
            if not connection_ok:
                raise ValidationError("Failed to connect to platform")
        except Exception as e:
            raise ValidationError(f"Connection test failed: {str(e)}")
        
        # Create config
        import_config = ImportConfig(
            id=str(uuid.uuid4()),
            user_id=user_id,
            platform=platform,
            name=name or f"{platform} Import",
            config=config,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.db.add(import_config)
        await self.db.commit()
        await self.db.refresh(import_config)
        
        logger.info(f"Import config created: {import_config.id} for platform {platform}")
        return import_config
    
    async def start_import_task(
        self,
        config_id: str,
        user_id: str,
        incremental: bool = False
    ) -> ImportTask:
        """Start a new import task."""
        
        # Get config
        from sqlalchemy import select
        result = await self.db.execute(
            select(ImportConfig).where(
                ImportConfig.id == config_id,
                ImportConfig.user_id == user_id
            )
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise NotFoundError("Import config not found")
        
        if not config.is_active:
            raise ValidationError("Import config is not active")
        
        # Create task
        task = ImportTask(
            id=str(uuid.uuid4()),
            config_id=config_id,
            status="pending",
            total_items=0,
            imported_items=0,
            failed_items=0,
            started_at=datetime.utcnow()
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        logger.info(f"Import task started: {task.id} for config {config_id}")
        
        # Execute import in background (simplified for now)
        try:
            await self._execute_import(task, config, user_id, incremental)
        except Exception as e:
            logger.error(f"Import task {task.id} failed: {str(e)}")
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await self.db.commit()
        
        return task
    
    async def _execute_import(
        self,
        task: ImportTask,
        config: ImportConfig,
        user_id: str,
        incremental: bool
    ) -> None:
        """Execute the import task."""
        
        task.status = "running"
        await self.db.commit()
        
        try:
            # Get adapter
            adapter = self.get_adapter(config.platform, config.config)
            
            # Determine since date for incremental import
            since = config.last_import_at if incremental else None
            
            # Fetch items
            raw_items = await adapter.fetch_items(since=since)
            task.total_items = len(raw_items)
            await self.db.commit()
            
            # Import each item
            for raw_item in raw_items:
                try:
                    # Transform item
                    transformed = adapter.transform_item(raw_item)
                    
                    # Check if item already exists
                    existing = await self._find_existing_item(
                        user_id,
                        config.platform,
                        transformed.get("source_id")
                    )
                    
                    if existing:
                        # Update existing item
                        await self._update_knowledge_item(existing, transformed)
                    else:
                        # Create new item
                        await self._create_knowledge_item(user_id, config.platform, transformed)
                    
                    task.imported_items += 1
                    
                except Exception as e:
                    logger.error(f"Failed to import item: {str(e)}")
                    task.failed_items += 1
                
                await self.db.commit()
            
            # Update task status
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            
            # Update config last import time
            config.last_import_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(
                f"Import task {task.id} completed: "
                f"{task.imported_items}/{task.total_items} items imported, "
                f"{task.failed_items} failed"
            )
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await self.db.commit()
            raise
    
    async def _find_existing_item(
        self,
        user_id: str,
        platform: str,
        source_id: Optional[str]
    ) -> Optional[KnowledgeItem]:
        """Find existing knowledge item by source."""
        
        if not source_id:
            return None
        
        from sqlalchemy import select
        result = await self.db.execute(
            select(KnowledgeItem).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.source_platform == platform,
                KnowledgeItem.source_id == source_id
            )
        )
        return result.scalar_one_or_none()
    
    async def _create_knowledge_item(
        self,
        user_id: str,
        platform: str,
        data: Dict[str, Any]
    ) -> KnowledgeItem:
        """Create a new knowledge item from imported data."""
        
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title=data["title"],
            content=data["content"],
            content_type=data.get("content_type", "markdown"),
            summary=data.get("summary"),
            author_id=user_id,
            source_platform=platform,
            source_url=data.get("source_url"),
            source_id=data.get("source_id"),
            is_published=data.get("is_published", True),
            visibility=data.get("visibility", "private"),
            meta_data=data.get("meta_data", {}),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=datetime.utcnow()
        )
        
        # Calculate word count
        item.calculate_word_count()
        
        self.db.add(item)
        return item
    
    async def _update_knowledge_item(
        self,
        item: KnowledgeItem,
        data: Dict[str, Any]
    ) -> KnowledgeItem:
        """Update an existing knowledge item with imported data."""
        
        # Create version before update
        item.create_version(
            change_summary=f"Updated from {item.source_platform}",
            change_type="import"
        )
        
        # Update fields
        item.title = data["title"]
        item.content = data["content"]
        item.summary = data.get("summary", item.summary)
        item.source_url = data.get("source_url", item.source_url)
        item.updated_at = datetime.utcnow()
        
        # Recalculate word count
        item.calculate_word_count()
        
        return item


# Example adapter for demonstration
class MarkdownFileAdapter(ImportAdapter):
    """Adapter for importing Markdown files."""
    
    platform_name = "markdown_file"
    
    def validate_config(self) -> None:
        """Validate configuration."""
        if "file_path" not in self.config:
            raise ValidationError("file_path is required in config")
    
    async def test_connection(self) -> bool:
        """Test if file exists."""
        import os
        return os.path.exists(self.config["file_path"])
    
    async def fetch_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Read markdown file."""
        import os
        
        file_path = self.config["file_path"]
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Simple parsing: first line as title, rest as content
        lines = content.split("\n", 1)
        title = lines[0].strip("# ").strip()
        body = lines[1] if len(lines) > 1 else ""
        
        return [{
            "title": title,
            "content": body,
            "file_path": file_path,
            "modified_time": datetime.fromtimestamp(os.path.getmtime(file_path))
        }]
    
    def transform_item(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform markdown file data."""
        return {
            "title": raw_data["title"],
            "content": self.clean_content(raw_data["content"]),
            "content_type": "markdown",
            "source_id": raw_data["file_path"],
            "source_url": f"file://{raw_data['file_path']}",
            "created_at": raw_data["modified_time"],
            "is_published": True,
            "visibility": "private"
        }


# Register default adapters
ImportEngine.register_adapter(MarkdownFileAdapter)
