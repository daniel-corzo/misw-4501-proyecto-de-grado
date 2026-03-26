import pytest
from travelhub_common.config import BaseAppSettings
from jose import jwt
from datetime import datetime, timedelta, timezone

@pytest.fixture
def test_settings():
    return BaseAppSettings(
        jwt_public_key="secret-key-for-tests",
        jwt_private_key="secret-key-for-tests",
        jwt_algorithm="HS256"
    )

@pytest.fixture
def generate_token(test_settings):
    def _generate(payload: dict):
        if "exp" not in payload:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
            payload.update({"exp": int(expire.timestamp())})
        encoded_jwt = jwt.encode(payload, test_settings.jwt_private_key, algorithm=test_settings.jwt_algorithm)
        return encoded_jwt
    return _generate
