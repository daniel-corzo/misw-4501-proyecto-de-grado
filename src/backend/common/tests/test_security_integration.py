import pytest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import FastAPI, Depends, APIRouter
from httpx import AsyncClient, ASGITransport
from travelhub_common.security import get_current_user, RoleChecker, RoleEnum, User, get_settings


def _not_revoked_factory():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_db.execute.return_value = mock_result

    @asynccontextmanager
    async def _cm():
        yield mock_db

    return MagicMock(side_effect=_cm)

app = FastAPI()
router = APIRouter()

@router.get("/public")
async def public_route():
    return {"message": "public"}

@router.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {"message": "protected", "user_id": str(user.id)}

@router.get("/admin")
async def admin_route(user: User = Depends(RoleChecker([RoleEnum.ADMIN]))):
    return {"message": "admin", "user_id": str(user.id)}

app.include_router(router)

@pytest.mark.asyncio
async def test_public_route():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/public")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_protected_route_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/protected")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_authorized(test_settings, generate_token):
    app.dependency_overrides[get_settings] = lambda: test_settings

    user_id = str(uuid4())
    token = generate_token({"sub": user_id, "email": "test@test.com", "role": "USER"})

    with patch("travelhub_common.security._get_cached_session_factory", return_value=_not_revoked_factory()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/protected", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"message": "protected", "user_id": user_id}
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_admin_route_forbidden(test_settings, generate_token):
    app.dependency_overrides[get_settings] = lambda: test_settings

    user_id = str(uuid4())
    token = generate_token({"sub": user_id, "email": "test@test.com", "role": "USER"})

    with patch("travelhub_common.security._get_cached_session_factory", return_value=_not_revoked_factory()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/admin", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Operacion no permitida"
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_admin_route_authorized(test_settings, generate_token):
    app.dependency_overrides[get_settings] = lambda: test_settings

    user_id = str(uuid4())
    token = generate_token({"sub": user_id, "email": "admin@test.com", "role": "ADMIN"})

    with patch("travelhub_common.security._get_cached_session_factory", return_value=_not_revoked_factory()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/admin", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["user_id"] == user_id
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_protected_route_invalid_token(test_settings):
    app.dependency_overrides[get_settings] = lambda: test_settings
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/protected", headers={"Authorization": "Bearer invalidtoken123"})
        
    assert response.status_code == 401
    assert response.json()["detail"] == "No se pudieron validar las credenciales"
    app.dependency_overrides.clear()
