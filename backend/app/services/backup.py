"""
Backup Service

Business logic for data backup and restore operations.
"""

import json
import zipfile
from io import BytesIO
from typing import Dict, Any, List
from datetime import datetime
import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.knowledge import KnowledgeItem, KnowledgeVersion, KnowledgeLink
from app.models.category import Category
from app.models.tag import Tag
from app.models.attachment import Attachment
from app.core.exceptions import ValidationError


class BackupService:
    """Service class for backup and restore operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_full_backup(self, user_id: str) -> BytesIO:
        """
        Create a complete backup of all user data.
        Returns a ZIP file containing JSON data and metadata.
        """
        
        logger.info(f"Starting full backup for user {user_id}")
        
        # Collect all data
        backup_data = {
            "metadata": {
                "backup_version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "user_id": user_id,
            },
            "knowledge_items": await self._backup_knowledge_items(user_id),
            "categories": await self._backup_categories(user_id),
            "tags": await self._backup_tags(user_id),
            "links": await self._backup_links(user_id),
        }
        
        # Calculate checksum
        data_str = json.dumps(backup_data, sort_keys=True)
        checksum = hashlib.sha256(data_str.encode()).hexdigest()
        backup_data["metadata"]["checksum"] = checksum
        
        # Create ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add main backup file
            zip_file.writestr(
                "backup.json",
                json.dumps(backup_data, ensure_ascii=False, indent=2)
            )
            
            # Add README
            readme = self._generate_readme(backup_data)
            zip_file.writestr("README.txt", readme)
        
        zip_buffer.seek(0)
        
        logger.info(f"Full backup completed for user {user_id}: {len(backup_data['knowledge_items'])} items")
        return zip_buffer
    
    async def create_incremental_backup(
        self,
        user_id: str,
        since: datetime
    ) -> BytesIO:
        """
        Create an incremental backup of data changed since a specific date.
        """
        
        logger.info(f"Starting incremental backup for user {user_id} since {since}")
        
        # Collect changed data
        backup_data = {
            "metadata": {
                "backup_version": "1.0",
                "backup_type": "incremental",
                "created_at": datetime.utcnow().isoformat(),
                "since": since.isoformat(),
                "user_id": user_id,
            },
            "knowledge_items": await self._backup_knowledge_items(user_id, since),
            "categories": await self._backup_categories(user_id, since),
            "tags": await self._backup_tags(user_id, since),
            "links": await self._backup_links(user_id, since),
        }
        
        # Calculate checksum
        data_str = json.dumps(backup_data, sort_keys=True)
        checksum = hashlib.sha256(data_str.encode()).hexdigest()
        backup_data["metadata"]["checksum"] = checksum
        
        # Create ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "incremental_backup.json",
                json.dumps(backup_data, ensure_ascii=False, indent=2)
            )
        
        zip_buffer.seek(0)
        
        logger.info(f"Incremental backup completed for user {user_id}")
        return zip_buffer
    
    async def verify_backup(self, backup_file: BytesIO) -> Dict[str, Any]:
        """
        Verify the integrity of a backup file.
        Returns verification results.
        """
        
        try:
            with zipfile.ZipFile(backup_file, 'r') as zip_file:
                # Check if backup.json exists
                if 'backup.json' not in zip_file.namelist():
                    return {
                        "valid": False,
                        "error": "backup.json not found in archive"
                    }
                
                # Read and parse backup data
                backup_json = zip_file.read('backup.json')
                backup_data = json.loads(backup_json)
                
                # Verify structure
                required_keys = ["metadata", "knowledge_items", "categories", "tags"]
                missing_keys = [k for k in required_keys if k not in backup_data]
                if missing_keys:
                    return {
                        "valid": False,
                        "error": f"Missing required keys: {missing_keys}"
                    }
                
                # Verify checksum
                stored_checksum = backup_data["metadata"].pop("checksum", None)
                if stored_checksum:
                    data_str = json.dumps(backup_data, sort_keys=True)
                    calculated_checksum = hashlib.sha256(data_str.encode()).hexdigest()
                    
                    if stored_checksum != calculated_checksum:
                        return {
                            "valid": False,
                            "error": "Checksum mismatch - backup may be corrupted"
                        }
                
                # Return verification results
                return {
                    "valid": True,
                    "metadata": backup_data["metadata"],
                    "item_count": len(backup_data["knowledge_items"]),
                    "category_count": len(backup_data["categories"]),
                    "tag_count": len(backup_data["tags"]),
                }
        
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def restore_backup(
        self,
        backup_file: BytesIO,
        user_id: str,
        options: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Restore data from a backup file.
        Options: restore_knowledge, restore_categories, restore_tags, overwrite_existing
        """
        
        # Verify backup first
        verification = await self.verify_backup(backup_file)
        if not verification["valid"]:
            raise ValidationError(f"Invalid backup: {verification['error']}")
        
        backup_file.seek(0)
        
        logger.info(f"Starting restore for user {user_id}")
        
        results = {
            "knowledge_items_restored": 0,
            "categories_restored": 0,
            "tags_restored": 0,
            "errors": [],
        }
        
        try:
            with zipfile.ZipFile(backup_file, 'r') as zip_file:
                backup_json = zip_file.read('backup.json')
                backup_data = json.loads(backup_json)
                
                # Restore categories first (needed for knowledge items)
                if options.get("restore_categories", True):
                    results["categories_restored"] = await self._restore_categories(
                        backup_data["categories"],
                        user_id,
                        options.get("overwrite_existing", False)
                    )
                
                # Restore tags
                if options.get("restore_tags", True):
                    results["tags_restored"] = await self._restore_tags(
                        backup_data["tags"],
                        user_id,
                        options.get("overwrite_existing", False)
                    )
                
                # Restore knowledge items
                if options.get("restore_knowledge", True):
                    results["knowledge_items_restored"] = await self._restore_knowledge_items(
                        backup_data["knowledge_items"],
                        user_id,
                        options.get("overwrite_existing", False)
                    )
                
                await self.db.commit()
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Restore failed: {str(e)}")
            raise ValidationError(f"Restore failed: {str(e)}")
        
        logger.info(f"Restore completed for user {user_id}: {results}")
        return results
    
    async def _backup_knowledge_items(
        self,
        user_id: str,
        since: datetime = None
    ) -> List[Dict[str, Any]]:
        """Backup knowledge items."""
        
        query = select(KnowledgeItem).options(
            selectinload(KnowledgeItem.tags),
            selectinload(KnowledgeItem.category),
            selectinload(KnowledgeItem.versions)
        ).where(KnowledgeItem.author_id == user_id)
        
        if since:
            query = query.where(KnowledgeItem.updated_at >= since)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return [
            {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "content_type": item.content_type,
                "summary": item.summary,
                "category_id": item.category_id,
                "tag_ids": [t.id for t in item.tags],
                "is_published": item.is_published,
                "visibility": item.visibility,
                "source_platform": item.source_platform,
                "source_url": item.source_url,
                "source_id": item.source_id,
                "meta_data": item.meta_data,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat(),
                "published_at": item.published_at.isoformat() if item.published_at else None,
            }
            for item in items
        ]
    
    async def _backup_categories(
        self,
        user_id: str,
        since: datetime = None
    ) -> List[Dict[str, Any]]:
        """Backup categories."""
        
        query = select(Category).where(
            Category.user_id == user_id,
            Category.is_active == True
        )
        
        if since:
            query = query.where(Category.updated_at >= since)
        
        result = await self.db.execute(query)
        categories = result.scalars().all()
        
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "parent_id": cat.parent_id,
                "color": cat.color,
                "icon": cat.icon,
                "sort_order": cat.sort_order,
            }
            for cat in categories
        ]
    
    async def _backup_tags(
        self,
        user_id: str,
        since: datetime = None
    ) -> List[Dict[str, Any]]:
        """Backup tags."""
        
        query = select(Tag).where(
            Tag.user_id == user_id,
            Tag.is_active == True
        )
        
        if since:
            query = query.where(Tag.updated_at >= since)
        
        result = await self.db.execute(query)
        tags = result.scalars().all()
        
        return [
            {
                "id": tag.id,
                "name": tag.name,
                "description": tag.description,
                "color": tag.color,
            }
            for tag in tags
        ]
    
    async def _backup_links(
        self,
        user_id: str,
        since: datetime = None
    ) -> List[Dict[str, Any]]:
        """Backup knowledge links."""
        
        query = select(KnowledgeLink).join(
            KnowledgeItem,
            KnowledgeLink.source_id == KnowledgeItem.id
        ).where(KnowledgeItem.author_id == user_id)
        
        if since:
            query = query.where(KnowledgeLink.created_at >= since)
        
        result = await self.db.execute(query)
        links = result.scalars().all()
        
        return [
            {
                "source_id": link.source_id,
                "target_id": link.target_id,
                "link_type": link.link_type,
                "description": link.description,
            }
            for link in links
        ]
    
    async def _restore_knowledge_items(
        self,
        items_data: List[Dict[str, Any]],
        user_id: str,
        overwrite: bool
    ) -> int:
        """Restore knowledge items from backup."""
        count = 0
        
        for item_data in items_data:
            try:
                # Check if item exists
                result = await self.db.execute(
                    select(KnowledgeItem).where(KnowledgeItem.id == item_data["id"])
                )
                existing = result.scalar_one_or_none()
                
                if existing and not overwrite:
                    logger.debug(f"Skipping existing item: {item_data['id']}")
                    continue
                
                if existing and overwrite:
                    # Update existing item
                    existing.title = item_data["title"]
                    existing.content = item_data["content"]
                    existing.content_type = item_data["content_type"]
                    existing.summary = item_data.get("summary")
                    existing.category_id = item_data.get("category_id")
                    existing.is_published = item_data["is_published"]
                    existing.visibility = item_data["visibility"]
                    existing.source_platform = item_data.get("source_platform")
                    existing.source_url = item_data.get("source_url")
                    existing.source_id = item_data.get("source_id")
                    existing.meta_data = item_data.get("meta_data", {})
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new item
                    new_item = KnowledgeItem(
                        id=item_data["id"],
                        title=item_data["title"],
                        content=item_data["content"],
                        content_type=item_data["content_type"],
                        summary=item_data.get("summary"),
                        author_id=user_id,
                        category_id=item_data.get("category_id"),
                        is_published=item_data["is_published"],
                        visibility=item_data["visibility"],
                        source_platform=item_data.get("source_platform"),
                        source_url=item_data.get("source_url"),
                        source_id=item_data.get("source_id"),
                        meta_data=item_data.get("meta_data", {}),
                        created_at=datetime.fromisoformat(item_data["created_at"]),
                        updated_at=datetime.fromisoformat(item_data["updated_at"]),
                        published_at=datetime.fromisoformat(item_data["published_at"]) if item_data.get("published_at") else None,
                    )
                    self.db.add(new_item)
                
                count += 1
                
            except Exception as e:
                logger.error(f"Failed to restore item {item_data.get('id')}: {str(e)}")
                continue
        
        return count
    
    async def _restore_categories(
        self,
        categories_data: List[Dict[str, Any]],
        user_id: str,
        overwrite: bool
    ) -> int:
        """Restore categories from backup."""
        count = 0
        
        # Sort by parent_id to ensure parents are created before children
        sorted_categories = sorted(
            categories_data,
            key=lambda x: (x.get("parent_id") is None, x.get("parent_id"))
        )
        
        for cat_data in sorted_categories:
            try:
                # Check if category exists
                result = await self.db.execute(
                    select(Category).where(Category.id == cat_data["id"])
                )
                existing = result.scalar_one_or_none()
                
                if existing and not overwrite:
                    logger.debug(f"Skipping existing category: {cat_data['id']}")
                    continue
                
                if existing and overwrite:
                    # Update existing category
                    existing.name = cat_data["name"]
                    existing.description = cat_data.get("description")
                    existing.parent_id = cat_data.get("parent_id")
                    existing.color = cat_data.get("color")
                    existing.icon = cat_data.get("icon")
                    existing.sort_order = cat_data.get("sort_order", 0)
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new category
                    new_cat = Category(
                        id=cat_data["id"],
                        name=cat_data["name"],
                        description=cat_data.get("description"),
                        user_id=user_id,
                        parent_id=cat_data.get("parent_id"),
                        color=cat_data.get("color"),
                        icon=cat_data.get("icon"),
                        sort_order=cat_data.get("sort_order", 0),
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    self.db.add(new_cat)
                
                count += 1
                
            except Exception as e:
                logger.error(f"Failed to restore category {cat_data.get('id')}: {str(e)}")
                continue
        
        return count
    
    async def _restore_tags(
        self,
        tags_data: List[Dict[str, Any]],
        user_id: str,
        overwrite: bool
    ) -> int:
        """Restore tags from backup."""
        count = 0
        
        for tag_data in tags_data:
            try:
                # Check if tag exists
                result = await self.db.execute(
                    select(Tag).where(Tag.id == tag_data["id"])
                )
                existing = result.scalar_one_or_none()
                
                if existing and not overwrite:
                    logger.debug(f"Skipping existing tag: {tag_data['id']}")
                    continue
                
                if existing and overwrite:
                    # Update existing tag
                    existing.name = tag_data["name"]
                    existing.description = tag_data.get("description")
                    existing.color = tag_data.get("color")
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new tag
                    new_tag = Tag(
                        id=tag_data["id"],
                        name=tag_data["name"],
                        description=tag_data.get("description"),
                        user_id=user_id,
                        color=tag_data.get("color"),
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    self.db.add(new_tag)
                
                count += 1
                
            except Exception as e:
                logger.error(f"Failed to restore tag {tag_data.get('id')}: {str(e)}")
                continue
        
        return count
    
    def _generate_readme(self, backup_data: Dict[str, Any]) -> str:
        """Generate README for backup."""
        return f"""知识管理平台 - 数据备份

备份信息：
- 创建时间: {backup_data['metadata']['created_at']}
- 备份版本: {backup_data['metadata']['backup_version']}
- 用户ID: {backup_data['metadata']['user_id']}

备份内容：
- 知识条目: {len(backup_data['knowledge_items'])} 条
- 分类: {len(backup_data['categories'])} 个
- 标签: {len(backup_data['tags'])} 个
- 知识链接: {len(backup_data.get('links', []))} 个

校验和: {backup_data['metadata'].get('checksum', 'N/A')}

恢复说明：
1. 使用平台的恢复功能上传此备份文件
2. 选择要恢复的数据类型
3. 确认恢复操作

注意：恢复操作可能会覆盖现有数据，请谨慎操作。
"""
