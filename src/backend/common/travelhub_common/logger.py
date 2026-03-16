import logging
import json
import time
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="-")


class CloudWatchFormatter(logging.Formatter):
    def __init__(self, service_name: str = "travelhub"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": record.levelname,
            "service": self.service_name,
            "correlation_id": correlation_id_var.get(),
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        return json.dumps(log_entry)


def get_logger(name: str, service_name: str = "travelhub") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(CloudWatchFormatter(service_name))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
