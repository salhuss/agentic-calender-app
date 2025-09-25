"""Test main application."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_openapi_docs(client: AsyncClient):
    """Test that OpenAPI docs are available."""
    response = await client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()