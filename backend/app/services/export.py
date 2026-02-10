"""
Export Service

Business logic for exporting knowledge items to various formats.
"""

import json
import zipfile
from io import BytesIO
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.knowledge import KnowledgeItem
from app.core.exceptions import NotFoundError, ValidationError


class ExportService:
    """Service class for export operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def export_to_markdown(
        self,
        knowledge_item_id: str,
        user_id: str,
        include_metadata: bool = True
    ) -> str:
        """Export a single knowledge item to Markdown format."""
        
        item = await self._get_item(knowledge_item_id, user_id)
        
        markdown = []
        
        # Title
        markdown.append(f"# {item.title}\n")
        
        # Metadata
        if include_metadata:
            markdown.append("---")
            markdown.append(f"**作者**: {item.author_id}")
            markdown.append(f"**创建时间**: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            markdown.append(f"**更新时间**: {item.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if item.category:
                markdown.append(f"**分类**: {item.category.name}")
            
            if item.tags:
                tags_str = ", ".join([f"#{tag.name}" for tag in item.tags])
                markdown.append(f"**标签**: {tags_str}")
            
            if item.source_platform:
                markdown.append(f"**来源**: {item.source_platform}")
                if item.source_url:
                    markdown.append(f"**原文链接**: {item.source_url}")
            
            markdown.append(f"**字数**: {item.word_count}")
            markdown.append(f"**阅读时间**: {item.reading_time}分钟")
            markdown.append("---\n")
        
        # Summary
        if item.summary:
            markdown.append("## 摘要\n")
            markdown.append(f"{item.summary}\n")
        
        # Content
        markdown.append("## 正文\n")
        markdown.append(item.content)
        
        # Attachments
        if item.attachments:
            markdown.append("\n## 附件\n")
            for att in item.attachments:
                markdown.append(f"- [{att.original_filename}]({att.file_path})")
        
        return "\n".join(markdown)
    
    async def export_to_json(
        self,
        knowledge_item_id: str,
        user_id: str,
        include_versions: bool = False
    ) -> Dict[str, Any]:
        """Export a single knowledge item to JSON format."""
        
        item = await self._get_item(knowledge_item_id, user_id)
        
        data = {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "content_type": item.content_type,
            "summary": item.summary,
            "author_id": item.author_id,
            "category": {
                "id": item.category.id,
                "name": item.category.name,
                "full_path": item.category.full_path
            } if item.category else None,
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color
                }
                for tag in item.tags
            ],
            "attachments": [
                {
                    "id": att.id,
                    "filename": att.original_filename,
                    "file_path": att.file_path,
                    "mime_type": att.mime_type,
                    "file_size": att.file_size
                }
                for att in item.attachments
            ],
            "source_platform": item.source_platform,
            "source_url": item.source_url,
            "source_id": item.source_id,
            "is_published": item.is_published,
            "visibility": item.visibility,
            "view_count": item.view_count,
            "word_count": item.word_count,
            "reading_time": item.reading_time,
            "meta_data": item.meta_data,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
            "published_at": item.published_at.isoformat() if item.published_at else None
        }
        
        # Include version history if requested
        if include_versions:
            data["versions"] = [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "title": v.title,
                    "content": v.content,
                    "change_summary": v.change_summary,
                    "change_type": v.change_type,
                    "created_at": v.created_at.isoformat()
                }
                for v in item.versions
            ]
        
        return data
    
    async def export_to_html(
        self,
        knowledge_item_id: str,
        user_id: str
    ) -> str:
        """Export a single knowledge item to HTML format."""
        
        item = await self._get_item(knowledge_item_id, user_id)
        
        # Convert markdown to HTML if needed
        content_html = item.content
        if item.content_type == "markdown":
            try:
                import markdown
                content_html = markdown.markdown(
                    item.content,
                    extensions=['extra', 'codehilite', 'toc']
                )
            except ImportError:
                # Fallback: wrap in pre tag
                content_html = f"<pre>{item.content}</pre>"
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{item.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .metadata {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 0.9em;
        }}
        .metadata p {{
            margin: 5px 0;
        }}
        .tags {{
            margin: 10px 0;
        }}
        .tag {{
            display: inline-block;
            background: #e0e0e0;
            padding: 3px 10px;
            border-radius: 3px;
            margin-right: 5px;
            font-size: 0.85em;
        }}
        .content {{
            margin: 30px 0;
        }}
        .attachments {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <h1>{item.title}</h1>
    
    <div class="metadata">
        <p><strong>创建时间:</strong> {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>更新时间:</strong> {item.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        {f'<p><strong>分类:</strong> {item.category.full_path}</p>' if item.category else ''}
        {f'<p><strong>来源:</strong> {item.source_platform}</p>' if item.source_platform else ''}
        <p><strong>字数:</strong> {item.word_count} | <strong>阅读时间:</strong> {item.reading_time}分钟</p>
        {f'''<div class="tags">
            <strong>标签:</strong> 
            {' '.join([f'<span class="tag" style="background-color: {tag.color}20; color: {tag.color};">{tag.name}</span>' for tag in item.tags])}
        </div>''' if item.tags else ''}
    </div>
    
    {f'<div class="summary"><h2>摘要</h2><p>{item.summary}</p></div>' if item.summary else ''}
    
    <div class="content">
        <h2>正文</h2>
        {content_html}
    </div>
    
    {f'''<div class="attachments">
        <h2>附件</h2>
        <ul>
            {' '.join([f'<li><a href="{att.file_path}">{att.original_filename}</a> ({att.file_size_human})</li>' for att in item.attachments])}
        </ul>
    </div>''' if item.attachments else ''}
</body>
</html>"""
        
        return html
    
    async def batch_export(
        self,
        user_id: str,
        item_ids: List[str],
        format: str = "markdown",
        include_metadata: bool = True
    ) -> BytesIO:
        """
        Export multiple knowledge items to a ZIP file.
        Returns a BytesIO object containing the ZIP file.
        """
        
        if format not in ["markdown", "json", "html"]:
            raise ValidationError(f"Unsupported export format: {format}")
        
        logger.info(f"Starting batch export for user {user_id}, {len(item_ids)} items, format: {format}")
        
        # Create ZIP file in memory
        zip_buffer = BytesIO()
        exported_count = 0
        failed_items = []
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for item_id in item_ids:
                try:
                    logger.info(f"Exporting item {item_id}")
                    
                    # Generate content based on format
                    if format == "markdown":
                        content = await self.export_to_markdown(item_id, user_id, include_metadata)
                        extension = "md"
                    elif format == "json":
                        content = json.dumps(
                            await self.export_to_json(item_id, user_id),
                            ensure_ascii=False,
                            indent=2
                        )
                        extension = "json"
                    else:  # html
                        content = await self.export_to_html(item_id, user_id)
                        extension = "html"
                    
                    # Get item title for filename (using a simple query)
                    from sqlalchemy import text
                    result = await self.db.execute(
                        text("SELECT title FROM knowledge_items WHERE id = :id"),
                        {"id": item_id}
                    )
                    row = result.fetchone()
                    title = row[0] if row else f"item_{item_id[:8]}"
                    
                    # Generate safe filename
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_title = safe_title[:50] if safe_title else f"item_{item_id[:8]}"
                    filename = f"{safe_title}.{extension}"
                    
                    # Add to ZIP
                    zip_file.writestr(filename, content)
                    exported_count += 1
                    logger.info(f"Successfully exported item {item_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to export item {item_id}: {str(e)}", exc_info=True)
                    failed_items.append((item_id, str(e)))
                    # Continue with other items
        
        if exported_count == 0:
            error_msg = f"No items could be exported. Failed items: {failed_items}"
            logger.error(error_msg)
            raise NotFoundError("No items could be exported")
        
        zip_buffer.seek(0)
        logger.info(f"Batch export completed: {exported_count}/{len(item_ids)} items in {format} format")
        return zip_buffer
    
    async def export_all(
        self,
        user_id: str,
        format: str = "json",
        include_deleted: bool = False
    ) -> BytesIO:
        """
        Export all knowledge items for a user.
        Returns a ZIP file containing all items.
        """
        
        # Get all items
        query = select(KnowledgeItem).where(
            KnowledgeItem.author_id == user_id
        ).options(
            selectinload(KnowledgeItem.tags),
            selectinload(KnowledgeItem.category),
            selectinload(KnowledgeItem.attachments)
        )
        
        if not include_deleted:
            query = query.where(KnowledgeItem.is_deleted == False)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        item_ids = [item.id for item in items]
        
        logger.info(f"Exporting all items for user {user_id}: {len(item_ids)} items")
        return await self.batch_export(user_id, item_ids, format)
    
    async def _get_item(
        self,
        knowledge_item_id: str,
        user_id: str,
        check_author: bool = True
    ) -> KnowledgeItem:
        """Get a knowledge item with all relationships loaded."""
        
        query = select(KnowledgeItem).options(
            selectinload(KnowledgeItem.tags),
            selectinload(KnowledgeItem.category),
            selectinload(KnowledgeItem.attachments),
            selectinload(KnowledgeItem.versions)
        ).where(KnowledgeItem.id == knowledge_item_id)
        
        if check_author:
            query = query.where(KnowledgeItem.author_id == user_id)
        
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundError("Knowledge item not found")
        
        # Check if user has permission to view (if not author)
        if not check_author and item.author_id != user_id:
            if item.visibility == "private":
                raise NotFoundError("Knowledge item not found")
        
        return item
