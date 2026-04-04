import pytest
from travelhub_common.config import BaseAppSettings

from app.services.auth_service import (
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_generation():
    settings = BaseAppSettings(
        jwt_private_key="", jwt_algorithm="HS256", jwt_secret="test"
    )

    with pytest.raises(ValueError):
        create_access_token({"sub": "test"}, settings=settings)
