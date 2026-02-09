"""
Knowledge Graph Service

Business logic for knowledge relationships and graph operations.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.knowledge import KnowledgeItem, KnowledgeLink
from app.core.exceptions import NotFoundError, ValidationError


class KnowledgeGraphService:
    """Service class for knowledge graph operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_link(
        self,
        source_id: str,
        target_id: str,
        user_id: str,
        link_type: str = "related",
        description: Optional[str] = None
    ) -> KnowledgeLink:
        """Create a link between two knowledge items."""
        
        # Validate both items exist and belong to user
        source = await self._get_item(source_id, user_id)
        target = await self._get_item(target_id, user_id)
        
        if source_id == target_id:
            raise ValidationError("Cannot link an item to itself")
        
        # Check if link already exists
        existing = await self._get_link(source_id, target_id)
        if existing:
            raise ValidationError("Link already exists")
        
        # Create link
        link = KnowledgeLink(
            id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            link_type=link_type,
            description=description,
            created_at=datetime.utcnow()
        )
        
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        
        logger.info(f"Knowledge link created: {source_id} -> {target_id} ({link_type})")
        return link
    
    async def delete_link(self, link_id: str, user_id: str) -> bool:
        """Delete a knowledge link."""
        
        result = await self.db.execute(
            select(KnowledgeLink)
            .join(KnowledgeItem, KnowledgeLink.source_id == KnowledgeItem.id)
            .where(
                KnowledgeLink.id == link_id,
                KnowledgeItem.author_id == user_id
            )
        )
        link = result.scalar_one_or_none()
        
        if not link:
            raise NotFoundError("Link not found")
        
        await self.db.delete(link)
        await self.db.commit()
        
        logger.info(f"Knowledge link deleted: {link_id}")
        return True
    
    async def get_links(
        self,
        knowledge_item_id: str,
        user_id: str,
        direction: str = "both"
    ) -> List[KnowledgeLink]:
        """
        Get all links for a knowledge item.
        direction: 'outgoing', 'incoming', or 'both'
        """
        
        # Verify item exists and belongs to user
        await self._get_item(knowledge_item_id, user_id)
        
        query = select(KnowledgeLink).options(
            selectinload(KnowledgeLink.source_item),
            selectinload(KnowledgeLink.target_item)
        )
        
        if direction == "outgoing":
            query = query.where(KnowledgeLink.source_id == knowledge_item_id)
        elif direction == "incoming":
            query = query.where(KnowledgeLink.target_id == knowledge_item_id)
        else:  # both
            query = query.where(
                or_(
                    KnowledgeLink.source_id == knowledge_item_id,
                    KnowledgeLink.target_id == knowledge_item_id
                )
            )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_graph_data(
        self,
        user_id: str,
        center_id: Optional[str] = None,
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        Get graph data for visualization.
        If center_id is provided, get subgraph around that item.
        Otherwise, get full graph for user.
        """
        
        if center_id:
            return await self._get_subgraph(center_id, user_id, depth)
        else:
            return await self._get_full_graph(user_id)
    
    async def _get_subgraph(
        self,
        center_id: str,
        user_id: str,
        depth: int
    ) -> Dict[str, Any]:
        """Get subgraph around a specific item."""
        
        # Verify center item exists
        center_item = await self._get_item(center_id, user_id)
        
        nodes = {}
        edges = []
        visited = set()
        
        # BFS to get items within depth
        queue = [(center_id, 0)]
        visited.add(center_id)
        
        while queue:
            item_id, current_depth = queue.pop(0)
            
            if current_depth > depth:
                continue
            
            # Get item details
            item = await self._get_item(item_id, user_id)
            nodes[item_id] = {
                "id": item.id,
                "title": item.title,
                "is_published": item.is_published,
                "word_count": item.word_count,
                "category": item.category.name if item.category else None,
                "tags": [{"name": t.name, "color": t.color} for t in item.tags],
            }
            
            # Get links
            links = await self.get_links(item_id, user_id, "both")
            
            for link in links:
                # Add edge
                edges.append({
                    "id": link.id,
                    "source": link.source_id,
                    "target": link.target_id,
                    "type": link.link_type,
                    "description": link.description,
                })
                
                # Add connected items to queue
                other_id = link.target_id if link.source_id == item_id else link.source_id
                if other_id not in visited and current_depth < depth:
                    visited.add(other_id)
                    queue.append((other_id, current_depth + 1))
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "center_id": center_id,
            "depth": depth,
        }
    
    async def _get_full_graph(self, user_id: str) -> Dict[str, Any]:
        """Get full knowledge graph for user."""
        
        # Get all items
        items_result = await self.db.execute(
            select(KnowledgeItem)
            .options(
                selectinload(KnowledgeItem.category),
                selectinload(KnowledgeItem.tags)
            )
            .where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False
            )
        )
        items = items_result.scalars().all()
        
        # Build nodes
        nodes = [
            {
                "id": item.id,
                "title": item.title,
                "is_published": item.is_published,
                "word_count": item.word_count,
                "category": item.category.name if item.category else None,
                "tags": [{"name": t.name, "color": t.color} for t in item.tags],
            }
            for item in items
        ]
        
        # Get all links
        links_result = await self.db.execute(
            select(KnowledgeLink)
            .join(KnowledgeItem, KnowledgeLink.source_id == KnowledgeItem.id)
            .where(KnowledgeItem.author_id == user_id)
        )
        links = links_result.scalars().all()
        
        # Build edges
        edges = [
            {
                "id": link.id,
                "source": link.source_id,
                "target": link.target_id,
                "type": link.link_type,
                "description": link.description,
            }
            for link in links
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
        }
    
    async def detect_related_items(
        self,
        knowledge_item_id: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Automatically detect potentially related items based on:
        - Same category
        - Common tags
        - Content similarity (simple keyword matching)
        """
        
        item = await self._get_item(knowledge_item_id, user_id)
        
        # Get items with same category or common tags
        query = select(KnowledgeItem).options(
            selectinload(KnowledgeItem.tags),
            selectinload(KnowledgeItem.category)
        ).where(
            KnowledgeItem.author_id == user_id,
            KnowledgeItem.is_deleted == False,
            KnowledgeItem.id != knowledge_item_id
        )
        
        # Filter by category or tags
        if item.category_id:
            query = query.where(
                or_(
                    KnowledgeItem.category_id == item.category_id,
                    KnowledgeItem.id.in_(
                        select(KnowledgeItem.id)
                        .join(KnowledgeItem.tags)
                        .where(KnowledgeItem.tags.any(id__in=[t.id for t in item.tags]))
                    )
                )
            )
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        related_items = result.scalars().all()
        
        # Calculate similarity scores
        suggestions = []
        for related in related_items:
            score = 0
            reasons = []
            
            # Same category
            if related.category_id == item.category_id:
                score += 3
                reasons.append("同分类")
            
            # Common tags
            common_tags = set(t.id for t in item.tags) & set(t.id for t in related.tags)
            if common_tags:
                score += len(common_tags) * 2
                reasons.append(f"{len(common_tags)}个共同标签")
            
            suggestions.append({
                "id": related.id,
                "title": related.title,
                "score": score,
                "reasons": reasons,
                "category": related.category.name if related.category else None,
                "tags": [{"name": t.name, "color": t.color} for t in related.tags],
            })
        
        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        
        return suggestions
    
    async def get_graph_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        
        # Count total items
        items_result = await self.db.execute(
            select(KnowledgeItem).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False
            )
        )
        total_items = len(items_result.scalars().all())
        
        # Count total links
        links_result = await self.db.execute(
            select(KnowledgeLink)
            .join(KnowledgeItem, KnowledgeLink.source_id == KnowledgeItem.id)
            .where(KnowledgeItem.author_id == user_id)
        )
        total_links = len(links_result.scalars().all())
        
        # Count isolated items (no links)
        isolated_result = await self.db.execute(
            select(KnowledgeItem).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False,
                ~KnowledgeItem.id.in_(
                    select(KnowledgeLink.source_id).union(
                        select(KnowledgeLink.target_id)
                    )
                )
            )
        )
        isolated_items = len(isolated_result.scalars().all())
        
        return {
            "total_items": total_items,
            "total_links": total_links,
            "isolated_items": isolated_items,
            "connected_items": total_items - isolated_items,
            "average_links_per_item": round(total_links / total_items, 2) if total_items > 0 else 0,
        }
    
    async def _get_item(self, item_id: str, user_id: str) -> KnowledgeItem:
        """Get a knowledge item with validation."""
        
        result = await self.db.execute(
            select(KnowledgeItem)
            .options(
                selectinload(KnowledgeItem.category),
                selectinload(KnowledgeItem.tags)
            )
            .where(
                KnowledgeItem.id == item_id,
                KnowledgeItem.author_id == user_id
            )
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundError("Knowledge item not found")
        
        return item
    
    async def _get_link(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[KnowledgeLink]:
        """Check if a link exists between two items."""
        
        result = await self.db.execute(
            select(KnowledgeLink).where(
                or_(
                    and_(
                        KnowledgeLink.source_id == source_id,
                        KnowledgeLink.target_id == target_id
                    ),
                    and_(
                        KnowledgeLink.source_id == target_id,
                        KnowledgeLink.target_id == source_id
                    )
                )
            )
        )
        return result.scalar_one_or_none()
