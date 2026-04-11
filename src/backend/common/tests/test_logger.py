import json
import logging
from travelhub_common.logger import CloudWatchFormatter, get_logger, correlation_id_var


def test_correlation_id_var_default():
    token = correlation_id_var.set("-")
    try:
        assert correlation_id_var.get() == "-"
    finally:
        correlation_id_var.reset(token)


def test_get_logger_returns_logger():
    logger = get_logger("test.module", "test-service")
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1


def test_get_logger_idempotent():
    logger1 = get_logger("test.idempotent", "svc")
    handler_count = len(logger1.handlers)
    logger2 = get_logger("test.idempotent", "svc")
    assert len(logger2.handlers) == handler_count


def test_cloudwatch_formatter_json_output():
    formatter = CloudWatchFormatter(service_name="my-service")
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="hello world", args=(), exc_info=None
    )
    output = formatter.format(record)
    data = json.loads(output)

    assert data["level"] == "INFO"
    assert data["service"] == "my-service"
    assert data["message"] == "hello world"
    assert "timestamp" in data
    assert "correlation_id" in data


def test_cloudwatch_formatter_with_extra():
    formatter = CloudWatchFormatter(service_name="svc")
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="request", args=(), exc_info=None
    )
    record.extra = {"method": "GET", "path": "/health", "status_code": 200}
    output = formatter.format(record)
    data = json.loads(output)

    assert data["method"] == "GET"
    assert data["path"] == "/health"
    assert data["status_code"] == 200


def test_cloudwatch_formatter_uses_correlation_id_var():
    formatter = CloudWatchFormatter()
    token = correlation_id_var.set("test-corr-id-123")
    try:
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test", args=(), exc_info=None
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert data["correlation_id"] == "test-corr-id-123"
    finally:
        correlation_id_var.reset(token)
