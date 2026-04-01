from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest
from app.services.auth_service import authenticate_user, revoke_token
from app.services.rate_limiter import login_rate_limiter
from travelhub_common.logger import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer(auto_error=False)

audit_logger = get_logger("audit.usuarios")


def _emit_audit_log(
    request: Request,
    event_type: str,
    success: bool,
    email: str | None = None,
    user_id: str | None = None,
    reason: str | None = None,
) -> None:
    audit_logger.info(
        "audit_event",
        extra={
            "extra": {
                "event_type": event_type,
                "success": success,
                "email": email,
                "user_id": user_id,
                "ip_address": request.client.host if request.client else None,
                "forwarded_for": request.headers.get("x-forwarded-for"),
                "user_agent": request.headers.get("user-agent"),
                "reason": reason,
            }
        },
    )


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Autentica un usuario y retorna un JWT de acceso.
    """
    email_key = body.email.strip().lower()

    if login_rate_limiter.is_locked(email_key):
        _emit_audit_log(
            request,
            event_type="audit.login.rate_limited",
            success=False,
            email=body.email,
            reason="rate_limited",
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Intenta de nuevo en 15 minutos.",
        )

    try:
        access_token, user = await authenticate_user(body, db, settings)
    except HTTPException:
        login_rate_limiter.record_failure(email_key)
        _emit_audit_log(
            request,
            event_type="audit.login.failure",
            success=False,
            email=body.email,
            reason="invalid_credentials",
        )
        raise

    login_rate_limiter.reset(email_key)
    _emit_audit_log(
        request,
        event_type="audit.login.success",
        success=True,
        email=user.email,
        user_id=str(user.id),
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expiration_minutes * 60,
    )


@router.post("/refresh", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def refresh_token(body: RefreshRequest):
    """
    Renueva el token de acceso usando el refresh token.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Aun no implementado",
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Invalida el token de acceso actual.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado"
        )
    token = credentials.credentials
    try:
        if not settings.jwt_public_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La clave publica JWT no esta configurada",
            )
        payload = jwt.decode(
            token, settings.jwt_public_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        )

    await revoke_token(token, db)

    _emit_audit_log(
        request,
        event_type="audit.logout.success",
        success=True,
        email=payload.get("email"),
        user_id=payload.get("sub"),
    )

    return {"message": "Sesion cerrada correctamente"}
