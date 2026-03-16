import time
import uuid
from fastapi import Request
from travelhub_common.logger import correlation_id_var, get_logger

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next):
    correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    correlation_id_var.set(correlation_id)
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    response.headers["x-correlation-id"] = correlation_id
    return response
