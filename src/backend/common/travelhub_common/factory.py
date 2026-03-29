from typing import List, Optional
from fastapi import FastAPI, APIRouter, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from travelhub_common.middleware import logging_middleware
from travelhub_common.exceptions import register_exception_handlers


def create_app(
    service_name: str,
    routers: Optional[List[APIRouter]] = None,
    get_db=None,
) -> FastAPI:
    """
    Factory transversal para todos los microservicios de TravelHub.

    Uso:
        from travelhub_common.factory import create_app
        from app.config import get_settings
        from app.database import get_db
        from app.routers import mis_rutas

        settings = get_settings()
        app = create_app(
            service_name=settings.service_name,
            routers=[mis_rutas.router],
            get_db=get_db,
        )
    """
    app = FastAPI(
        title=f"TravelHub - {service_name}",
        version="1.0.0",
        docs_url=None,
        openapi_url="/openapi.json",
        redoc_url=None,
    )

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        # Use a relative OpenAPI URL so docs work correctly behind /api/{service}/ prefixes.
        return get_swagger_ui_html(
            openapi_url="openapi.json",
            title=f"TravelHub - {service_name} - Swagger UI",
        )

    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)
    register_exception_handlers(app)

    health_router = APIRouter()

    if get_db:
        @health_router.get("/health", tags=["health"])
        async def health(db: AsyncSession = Depends(get_db)):
            await db.execute(text("SELECT 1"))
            return {"status": "healthy", "service": service_name}
    else:
        @health_router.get("/health", tags=["health"])
        async def health_no_db():
            return {"status": "healthy", "service": service_name}

    app.include_router(health_router)

    if routers:
        for router in routers:
            app.include_router(router)

    return app
