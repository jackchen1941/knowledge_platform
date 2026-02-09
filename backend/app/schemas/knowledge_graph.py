"""
Knowledge Graph Schemas

Pydantic models for knowledge graph requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LinkCreate(BaseModel):
    """Schema for creating a knowledge link."""
    target_id: str = Field(..., description="Target knowledge item ID")
    link_type: str = Field(default="related", description="Type of link")
    description: Optional[str] = Field(None, description="Link description")


class LinkResponse(BaseModel):
    """Schema for link response."""
    id: str
    source_id: str
    target_id: str
    link_type: str
    description: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class GraphNode(BaseModel):
    """Schema for graph node."""
    id: str
    title: str
    is_published: bool
    word_count: int
    category: Optional[str]
    tags: List[Dict[str, str]]


class GraphEdge(BaseModel):
    """Schema for graph edge."""
    id: str
    source: str
    target: str
    type: str
    description: Optional[str]


class GraphData(BaseModel):
    """Schema for graph data."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    center_id: Optional[str] = None
    depth: Optional[int] = None


class RelatedItemSuggestion(BaseModel):
    """Schema for related item suggestion."""
    id: str
    title: str
    score: int
    reasons: List[str]
    category: Optional[str]
    tags: List[Dict[str, str]]


class RelatedItemsResponse(BaseModel):
    """Schema for related items response."""
    suggestions: List[RelatedItemSuggestion]


class GraphStatsResponse(BaseModel):
    """Schema for graph statistics."""
    total_items: int
    total_links: int
    isolated_items: int
    connected_items: int
    average_links_per_item: float
