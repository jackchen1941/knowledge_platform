"""
Knowledge Graph Endpoints

Handles knowledge relationships and graph operations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.knowledge_graph import KnowledgeGraphService
from app.schemas.knowledge_graph import (
    LinkCreate,
    LinkResponse,
    GraphData,
    RelatedItemsResponse,
    GraphStatsResponse,
)

router = APIRouter()


@router.post("/knowledge/{knowledge_item_id}/links", status_code=status.HTTP_201_CREATED)
async def create_link(
    knowledge_item_id: str,
    data: LinkCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a link between two knowledge items."""
    service = KnowledgeGraphService(db)
    link = await service.create_link(
        knowledge_item_id,
        data.target_id,
        current_user_id,
        data.link_type,
        data.description
    )
    # Convert to response format
    return {
        "id": link.id,
        "source_id": link.from_item_id,
        "target_id": link.to_item_id,
        "link_type": link.link_type,
        "description": link.description,
        "created_at": link.created_at.isoformat() if link.created_at else None,
    }


@router.get("/knowledge/{knowledge_item_id}/links")
async def get_links(
    knowledge_item_id: str,
    direction: str = Query("both", pattern="^(outgoing|incoming|both)$"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all links for a knowledge item."""
    service = KnowledgeGraphService(db)
    links = await service.get_links(knowledge_item_id, current_user_id, direction)
    return links


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: str,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a knowledge link."""
    service = KnowledgeGraphService(db)
    await service.delete_link(link_id, current_user_id)
    return None


@router.get("/graph", response_model=GraphData)
async def get_graph(
    center_id: Optional[str] = Query(None, description="Center item ID for subgraph"),
    depth: int = Query(2, ge=1, le=5, description="Depth for subgraph"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get knowledge graph data for visualization.
    If center_id is provided, returns subgraph around that item.
    Otherwise, returns full graph.
    """
    service = KnowledgeGraphService(db)
    graph_data = await service.get_graph_data(current_user_id, center_id, depth)
    return graph_data


@router.get("/knowledge/{knowledge_item_id}/related", response_model=RelatedItemsResponse)
async def get_related_items(
    knowledge_item_id: str,
    limit: int = Query(10, ge=1, le=50),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get automatically detected related items."""
    service = KnowledgeGraphService(db)
    suggestions = await service.detect_related_items(knowledge_item_id, current_user_id, limit)
    return RelatedItemsResponse(suggestions=suggestions)


@router.get("/graph/stats", response_model=GraphStatsResponse)
async def get_graph_stats(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get knowledge graph statistics."""
    service = KnowledgeGraphService(db)
    stats = await service.get_graph_stats(current_user_id)
    return stats
