"""
Structured logging configuration for socials.io
Provides JSON-formatted logs with correlation IDs and performance metrics.
"""
import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

# Import from config for logging settings
from config import config


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def __init__(self, include_timestamp: bool = True):
        super().__init__()
        self.include_timestamp = include_timestamp
        self.timezone = config.app.timezone

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Start with basic log record attributes
        log_data: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }

        # Add timestamp if requested
        if self.include_timestamp:
            log_data["timestamp"] = datetime.fromtimestamp(record.created, tz=self.timezone).isoformat()

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the record
        extra_fields = ["correlation_id", "operation", "duration_ms", "user_id", "template_num", "status_code"]
        for field in extra_fields:
            if hasattr(record, field):
                value = getattr(record, field)
                if value is not None:
                    log_data[field] = value

        # Add custom fields from record.__dict__ (anything starting with '_log_')
        for key, value in record.__dict__.items():
            if key.startswith('_log_') and key not in ['message', 'args']:
                log_data[key[5:]] = value  # Remove '_log_' prefix

        return json.dumps(log_data, default=str)


class CorrelationContext:
    """Context manager for correlation ID tracking."""

    _correlation_id: Optional[str] = None

    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())[:8]
        self._previous_id = CorrelationContext._correlation_id

    def __enter__(self):
        CorrelationContext._correlation_id = self.correlation_id
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CorrelationContext._correlation_id = self._previous_id

    @classmethod
    def get_current_correlation_id(cls) -> Optional[str]:
        return cls._correlation_id

    @classmethod
    def set_current_correlation_id(cls, correlation_id: str):
        cls._correlation_id = correlation_id


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)

    # Don't configure if already configured
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.logging.level))

    # Choose formatter based on config
    if config.logging.format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if configured
    if config.logging.file_path:
        file_handler = logging.FileHandler(config.logging.file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_operation_start(logger: logging.Logger, operation: str, **kwargs) -> Dict[str, Any]:
    """Log the start of an operation and return context info."""
    correlation_id = CorrelationContext.get_current_correlation_id()
    start_time = datetime.now(config.app.timezone).timestamp() * 1000  # ms

    logger.info(
        f"Starting operation: {operation}",
        extra={
            "correlation_id": correlation_id,
            "operation": operation,
            "event": "operation_start",
            **kwargs
        }
    )

    return {"correlation_id": correlation_id, "start_time": start_time, "operation": operation}


def log_operation_end(logger: logging.Logger, context: Dict[str, Any], success: bool = True, **kwargs):
    """Log the end of an operation with duration."""
    end_time = datetime.now(config.app.timezone).timestamp() * 1000  # ms
    duration_ms = end_time - context["start_time"]

    log_level = logging.INFO if success else logging.ERROR
    log_message = f"Completed operation: {context['operation']}"

    if duration_ms > 1000:  # Log performance warnings for operations > 1s
        logger.warning(
            f"Slow operation: {context['operation']} took {duration_ms:.2f}ms",
            extra={
                "correlation_id": context.get("correlation_id"),
                "operation": context["operation"],
                "duration_ms": round(duration_ms, 2),
                "event": "operation_slow_ms"
            }
        )

    logger.log(
        log_level,
        log_message,
        extra={
            "correlation_id": context.get("correlation_id"),
            "operation": context["operation"],
            "duration_ms": round(duration_ms, 2),
            "success": success,
            "event": "operation_end",
            **kwargs
        }
    )


def log_performance(logger: logging.Logger, operation: str, elapsed_ms: float, threshold_ms: int = 1000, **kwargs):
    """Log performance metrics with warnings for slow operations."""
    level = logging.WARNING if elapsed_ms > threshold_ms else logging.INFO

    logger.log(
        level,
        f"Performance metric: {operation} took {elapsed_ms:.2f}ms",
        extra={
            "correlation_id": CorrelationContext.get_current_correlation_id(),
            "operation": operation,
            "elapsed_ms": round(elapsed_ms, 2),
            "threshold_ms": threshold_ms,
            "event": "performance_metric",
            **kwargs
        }
    )


def log_api_call(logger: logging.Logger, method: str, url: str, status_code: Optional[int] = None,
                 duration_ms: Optional[float] = None, **kwargs):
    """Log API calls with status and duration."""
    level = logging.ERROR if status_code and status_code >= 400 else logging.INFO

    log_data = {
        "method": method,
        "url": url,
        "event": "api_call"
    }

    if status_code is not None:
        log_data["status_code"] = status_code

    if duration_ms is not None:
        log_data["duration_ms"] = round(duration_ms, 2)

    logger.log(
        level,
        f"API Call: {method} {url}",
        extra={
            "correlation_id": CorrelationContext.get_current_correlation_id(),
            **log_data,
            **kwargs
        }
    )


def log_error(logger: logging.Logger, error: Exception, operation: Optional[str] = None, **kwargs):
    """Log errors with context."""
    logger.error(
        f"Error{' in ' + operation if operation else ''}: {str(error)}",
        extra={
            "correlation_id": CorrelationContext.get_current_correlation_id(),
            "operation": operation,
            "error_type": type(error).__name__,
            "event": "error",
            **kwargs
        },
        exc_info=True
    )


# Global logger instance for convenience
logger = get_logger("socials.io")


# Context manager for operations
class OperationContext:
    """Context manager for logging operations with metrics."""

    def __init__(self, logger: logging.Logger, operation: str, **context_kwargs):
        self.logger = logger
        self.operation = operation
        self.context = None
        self.context_kwargs = context_kwargs

    def __enter__(self):
        self.context = log_operation_start(self.logger, self.operation, **self.context_kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Error occurred
            log_operation_end(self.logger, self.context, success=False, error=str(exc_val))
            return False  # Re-raise the exception

        # Success
        log_operation_end(self.logger, self.context, success=True)


# Convenience function for quick operation logging
def log_operation(logger: logging.Logger, operation: str):
    """Decorator or context manager for operation logging."""
    def decorator(func_or_context):
        if callable(func_or_context):
            # Used as decorator
            def wrapper(*args, **kwargs):
                with OperationContext(logger, operation):
                    return func_or_context(*args, **kwargs)
            return wrapper
        else:
            # Used as context manager factory
            return OperationContext(logger, operation, **(func_or_context or {}))

    return decorator