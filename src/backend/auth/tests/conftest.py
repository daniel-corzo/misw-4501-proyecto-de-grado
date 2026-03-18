import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch


@pytest.fixture
async def client():
    with patch("app.database.get_db") as mock_db:
        mock_session = AsyncMock()
        mock_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.return_value.__aexit__ = AsyncMock(return_value=False)

        from app.main import app
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as c:
            yield c
