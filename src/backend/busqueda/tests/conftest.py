import pytest
from travelhub_common.testing import create_test_client

@pytest.fixture
async def client():
    from app.main import app
    from app.database import get_db

    async for test_client in create_test_client(app, get_db):
        yield test_client