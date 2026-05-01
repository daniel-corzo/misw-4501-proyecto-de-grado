"""Pruebas de API pagos usando RSA reproducible."""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
    load_pem_public_key,
)
from httpx import ASGITransport, AsyncClient

from app.config import Settings, get_settings
from app.database import get_db
from app.main import app
from app.models.pago import EstadoPago
from travelhub_common.security import RoleEnum, User, get_current_user

USER_ID = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")


def _synthetic_tarjeta_inner() -> dict:
    """Valores solo para pruebas RSA; no usar formatos tipo PAN reales."""
    return {
        "numero": "unit-test-pan-ref-00009999",
        "cvv": "901",
        "fecha_expiracion": "12/2099",
    }


def _pem_pair():
    private_key = generate_private_key(public_exponent=65537, key_size=2048)
    priv_pem = private_key.private_bytes(
        Encoding.PEM,
        PrivateFormat.TraditionalOpenSSL,
        NoEncryption(),
    ).decode()
    pub_pem = private_key.public_key().public_bytes(
        Encoding.PEM,
        PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return priv_pem, pub_pem


def _encrypt_inner_json(pub_pem_ascii: str, inner: dict) -> str:
    import base64

    pubkey = load_pem_public_key(pub_pem_ascii.encode())
    plaintext = json.dumps(inner, separators=(",", ":")).encode("utf-8")
    ciphertext = pubkey.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(ciphertext).decode("ascii")


@pytest.fixture
def rsa_keys():
    return _pem_pair()


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    async def mock_refresh(instance, attribute_names=None):
        from uuid import uuid4

        if getattr(instance, "id", None) is None:
            instance.id = uuid4()
        now = datetime.now(UTC)
        if getattr(instance, "created_at", None) is None:
            instance.created_at = now
        instance.updated_at = now

    session.refresh = AsyncMock(side_effect=mock_refresh)
    session.commit = AsyncMock()
    return session


@pytest.fixture
def pagos_app_settings(rsa_keys):
    priv, _pub = rsa_keys
    return Settings(
        environment="test",
        service_name="pagos",
        db_url="postgresql+asyncpg://test:test@localhost/test",
        jwt_public_key="dummy",
        pago_rsa_private_key_pem=priv,
    )


@pytest.fixture
async def client_pagos(mock_db_session, pagos_app_settings):
    async def override_get_db():
        yield mock_db_session

    def override_user():
        return User(
            id=USER_ID,
            email="u@test.com",
            role=RoleEnum.USER,
        )

    def override_settings():
        return pagos_app_settings

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_settings] = override_settings

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_post_pagar_422_medio_de_pago_solo_espacios(client_pagos, rsa_keys):
    _, pub = rsa_keys
    inner = _synthetic_tarjeta_inner()
    payload_b64 = _encrypt_inner_json(pub, inner)

    response = await client_pagos.post(
        "/pagos/pagar",
        json={
            "monto": 1000,
            "medio_de_pago": "   ",
            "debe_fallar": False,
            "payload_cifrado": payload_b64,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_pagar_201_successful(client_pagos, mock_db_session, rsa_keys):
    _, pub = rsa_keys
    inner = _synthetic_tarjeta_inner()
    payload_b64 = _encrypt_inner_json(pub, inner)

    response = await client_pagos.post(
        "/pagos/pagar",
        json={
            "monto": 1000,
            "medio_de_pago": "  tarjeta_credito  ",
            "debe_fallar": False,
            "payload_cifrado": payload_b64,
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["monto"] == 1000
    assert data["medio_de_pago"] == "tarjeta_credito"
    assert data["estado"] == "successful"
    assert data["tarjeta_ultimos_4"] == "9999"
    assert mock_db_session.flush.await_count == 1
    assert mock_db_session.commit.await_count == 1
    mock_db_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_post_pagar_201_failed_flag(client_pagos, rsa_keys):
    _, pub = rsa_keys
    inner = _synthetic_tarjeta_inner()
    payload_b64 = _encrypt_inner_json(pub, inner)

    response = await client_pagos.post(
        "/pagos/pagar",
        json={
            "monto": 500,
            "medio_de_pago": "tarjeta_credito",
            "debe_fallar": True,
            "payload_cifrado": payload_b64,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["estado"] == "failed"
    assert body["tarjeta_ultimos_4"] == "9999"


@pytest.mark.asyncio
async def test_post_pagar_400_cipher_invalid(mock_db_session, rsa_keys, pagos_app_settings):
    _, pub = rsa_keys
    corrupt = _encrypt_inner_json(pub, {"numero": "n", "cvv": "12", "fecha_expiracion": "01/2099"})
    truncated = corrupt[:20]

    async def override_get_db():
        yield mock_db_session

    def override_settings():
        return pagos_app_settings

    def override_u():
        return User(id=USER_ID, email="u@test.com", role=RoleEnum.USER)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_u
    app.dependency_overrides[get_settings] = override_settings

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/pagos/pagar",
                json={
                    "monto": 1,
                    "medio_de_pago": "tarjeta_credito",
                    "debe_fallar": False,
                    "payload_cifrado": truncated,
                },
            )

        assert response.status_code == 400
        assert response.json().get("detail")
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_get_pago_200(client_pagos, mock_db_session):
    pago_id = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    now = datetime.now(UTC)
    pago = MagicMock()
    pago.id = pago_id
    pago.monto = 1500
    pago.medio_de_pago = "tarjeta_credito"
    pago.created_at = now
    pago.updated_at = now
    pago.estado = EstadoPago.successful
    pago.tarjeta_ultimos_4 = "9999"

    result = MagicMock()
    result.scalar_one_or_none.return_value = pago
    mock_db_session.execute = AsyncMock(return_value=result)

    response = await client_pagos.get(f"/pagos/{pago_id}")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == str(pago_id)
    assert data["monto"] == 1500
    assert data["medio_de_pago"] == "tarjeta_credito"
    assert data["estado"] == "successful"
    assert data["tarjeta_ultimos_4"] == "9999"
    mock_db_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_pago_404(client_pagos, mock_db_session):
    pago_id = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=result)

    response = await client_pagos.get(f"/pagos/{pago_id}")

    assert response.status_code == 404
    body = response.json()
    assert body.get("error") == "not_found"

