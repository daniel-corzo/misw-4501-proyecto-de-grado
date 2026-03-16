from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from travelhub_common.logger import correlation_id_var, get_logger

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
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Los datos enviados no son validos",
                "details": exc.errors(),
                "correlation_id": correlation_id_var.get(),
            },
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        logger.error("internal_server_error", extra={"error": str(exc)})
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "Error interno del servidor",
                "correlation_id": correlation_id_var.get(),
            },
        )
