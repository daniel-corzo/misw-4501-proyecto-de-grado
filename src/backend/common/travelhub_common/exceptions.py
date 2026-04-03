from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from travelhub_common.logger import correlation_id_var, get_logger
import traceback

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "message": "El recurso solicitado no existe",
                "correlation_id": correlation_id_var.get(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.warning("validation_error", extra={"errors": str(exc.errors())})
        safe_details = jsonable_encoder(exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Los datos enviados no son validos",
                "details": safe_details,
                "correlation_id": correlation_id_var.get(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # Log el stack trace completo para debugging
        tb_str = traceback.format_exc()
        logger.error("internal_server_error", extra={
            "error": str(exc),
            "type": type(exc).__name__,
            "traceback": tb_str,
            "path": request.url.path,
            "method": request.method,
        })
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "Error interno del servidor",
                "correlation_id": correlation_id_var.get(),
            },
        )

