import os

# Force test env before any test module imports app (avoids startup DB init and real DB if
# the shell already has ENVIRONMENT=local). setdefault would not override that.
os.environ["ENVIRONMENT"] = "test"

import pytest
from travelhub_common.testing import create_test_client

@pytest.fixture
async def client():
    from app.main import app
    from app.database import get_db

    async for test_client in create_test_client(app, get_db):
        yield test_client
