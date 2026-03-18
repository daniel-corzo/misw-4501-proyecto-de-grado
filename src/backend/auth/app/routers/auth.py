import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(body: LoginRequest):
    """
    Autentica un usuario y retorna un JWT de acceso.

    En la implementacion real:
    - Buscar el usuario por email en la BD
    - Verificar password con passlib/bcrypt
    - Generar JWT con python-jose
    """
    # TODO: reemplazar con validacion real contra la BD
    if body.password == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    fake_token = f"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.ejemplo.{uuid.uuid4().hex}"
    return LoginResponse(
        access_token=fake_token,
        token_type="bearer",
        expires_in=3600,
    )


@router.post("/refresh", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def refresh_token(body: RefreshRequest):
    """
    Renueva el token de acceso usando el refresh token.

    En la implementacion real:
    - Validar el refresh_token con python-jose
    - Verificar que no este en lista negra (Redis)
    - Emitir nuevo access_token
    """
    # TODO: implementar validacion real del refresh token
    if not body.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalido",
        )

    new_token = f"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.renovado.{uuid.uuid4().hex}"
    return LoginResponse(
        access_token=new_token,
        token_type="bearer",
        expires_in=3600,
    )
