import pytest
from uuid import uuid4
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from travelhub_common.security import RoleChecker, RoleEnum, User, TokenPayload, get_current_user
from travelhub_common.config import BaseAppSettings

def test_role_checker_allowed():
    checker = RoleChecker([RoleEnum.ADMIN])
    user = User(id=uuid4(), email="admin@test.com", role=RoleEnum.ADMIN)
    result = checker(user=user)
    assert result == user

def test_role_checker_denied():
    checker = RoleChecker([RoleEnum.ADMIN])
    user = User(id=uuid4(), email="user@test.com", role=RoleEnum.USER)
    
    with pytest.raises(HTTPException) as excinfo:
        checker(user=user)
        
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Operation not permitted"

def test_role_checker_multiple_roles():
    checker = RoleChecker([RoleEnum.ADMIN, RoleEnum.MANAGER])
    user_manager = User(id=uuid4(), email="manager@test.com", role=RoleEnum.MANAGER)
    assert checker(user=user_manager) == user_manager

def test_role_checker_empty_allowed_roles():
    checker = RoleChecker([])
    user = User(id=uuid4(), email="user@test.com", role=RoleEnum.USER)
    with pytest.raises(HTTPException) as excinfo:
        checker(user=user)
    assert excinfo.value.status_code == 403

def test_token_payload_model():
    payload = {"sub": str(uuid4()), "email": "test@test.com", "role": "USER", "exp": 1234567890}
    obj = TokenPayload(**payload)
    assert obj.sub == payload["sub"]
    assert obj.role == RoleEnum.USER

def test_get_current_user_success(test_settings, generate_token):
    user_id = str(uuid4())
    token = generate_token({"sub": user_id, "email": "test@test.com", "role": RoleEnum.USER.value})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    
    user = get_current_user(credentials=credentials, settings=test_settings)
    assert str(user.id) == user_id
    assert user.email == "test@test.com"
    assert user.role == RoleEnum.USER

def test_get_current_user_missing_public_key():
    settings = BaseAppSettings(jwt_public_key="", jwt_algorithm="HS256")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="any")
    
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(credentials=credentials, settings=settings)
        
    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == "JWT public key not configured"

def test_get_current_user_invalid_jwt(test_settings):
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")
    
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(credentials=credentials, settings=test_settings)
        
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"

def test_get_current_user_invalid_subject(test_settings, generate_token):
    token = generate_token({"sub": "not-a-uuid", "email": "test@test.com", "role": RoleEnum.USER.value})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(credentials=credentials, settings=test_settings)
        
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid subject"
