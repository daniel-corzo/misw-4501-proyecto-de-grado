import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock
from typing import Any, AsyncGenerator
from fastapi import FastAPI

async def create_test_client(
    app: FastAPI,
    get_db_dependency: Any
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with mocked database dependency."""
    async def mock_get_db():
        mock_session = AsyncMock()
        yield mock_session

    app.dependency_overrides[get_db_dependency] = mock_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
