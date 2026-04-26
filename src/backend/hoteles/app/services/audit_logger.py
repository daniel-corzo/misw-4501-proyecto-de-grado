from fastapi import Request
from travelhub_common.logger import get_logger

audit_logger = get_logger("audit.hoteles")


def emit_habitacion_audit_log(
    request: Request,
    event_type: str,
    success: bool,
    user_id: str | None = None,
    email: str | None = None,
    habitacion_id: str | None = None,
    reason: str | None = None,
) -> None:
    audit_logger.info(
        "audit_event",
        extra={
            "extra": {
                "event_type": event_type,
                "success": success,
                "user_id": user_id,
                "email": email,
                "habitacion_id": habitacion_id,
                "ip_address": request.client.host if request.client else None,
                "forwarded_for": request.headers.get("x-forwarded-for"),
                "user_agent": request.headers.get("user-agent"),
                "reason": reason,
            }
        },
    )
