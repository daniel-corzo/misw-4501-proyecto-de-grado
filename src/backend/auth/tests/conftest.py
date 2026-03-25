import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

@pytest.fixture
async def client():
    from app.main import app
    from app.database import get_db

    async def mock_get_db():
        mock_session = AsyncMock()
        yield mock_session

    app.dependency_overrides[get_db] = mock_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()
