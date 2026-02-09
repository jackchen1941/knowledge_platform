"""
Test main application functionality.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "knowledge-management-platform"


@pytest.mark.asyncio
async def test_docs_endpoint(client: AsyncClient):
    """Test API documentation endpoint."""
    response = await client.get("/docs")
    # In test mode, docs should be available
    assert response.status_code == 200