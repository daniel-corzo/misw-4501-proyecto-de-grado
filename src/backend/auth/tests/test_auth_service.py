import pytest
from app.services.auth_service import verify_password, get_password_hash, create_access_token
from travelhub_common.config import BaseAppSettings

def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_generation():
    # We need a proper RSA key pair for testing, for simplicity we can override the settings
    # or just make sure it raises ValueError when misconfigured if no key is set.
    settings = BaseAppSettings(jwt_private_key="", jwt_algorithm="HS256", jwt_secret="test")
    
    with pytest.raises(ValueError):
        create_access_token({"sub": "test"}, settings=settings)
