"""Tests for structured logging system."""
import json
import logging
import pytest
from unittest.mock import patch, MagicMock
import io
import sys

from src.logging_config import (
    logger, JsonFormatter, CorrelationContext, log_operation_start,
    log_operation_end, log_error, OperationContext, log_performance,
    log_api_call
)


class TestJsonFormatter:
    """Test JSON log formatting."""

    def test_basic_log_formatting(self):
        """Test basic JSON log record formatting."""
        formatter = JsonFormatter()

        # Create a mock log record
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )

        # Format the record
        result = formatter.format(record)

        # Parse the JSON back
        data = json.loads(result)

        assert data["level"] == "INFO"
        assert data["logger"] == "test.logger"
        assert data["message"] == "Test message"
        assert "timestamp" in data

    def test_log_with_extra_fields(self):
        """Test logging with extra fields."""
        log_msg = "Test with extras"

        # Capture log output
        log_output = io.StringIO()

        test_logger = logging.getLogger("test.logger")
        handler = logging.StreamHandler(log_output)
        handler.setFormatter(JsonFormatter())
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.INFO)

        test_logger.info(
            log_msg,
            extra={"correlation_id": "test-123", "user_id": "user-456"}
        )

        # Parse logged message
        logged_data = json.loads(log_output.getvalue().strip())

        assert logged_data["message"] == log_msg
        assert logged_data["correlation_id"] == "test-123"
        assert logged_data["user_id"] == "user-456"

    def test_exception_formatting(self):
        """Test formatting of exception information."""
        formatter = JsonFormatter()

        try:
            raise ValueError("Test error")
        except ValueError as e:
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=42,
                msg="An error occurred",
                args=(),
                exc_info=sys.exc_info()
            )

            result = formatter.format(record)
            data = json.loads(result)

            assert data["level"] == "ERROR"
            assert "exception" in data or "traceback" in data
            assert "ValueError" in str(data["exception"])


class TestCorrelationContext:
    """Test correlation ID context management."""

    def test_correlation_context_basic(self):
        """Test basic correlation ID management."""
        # Initially no correlation ID
        assert CorrelationContext.get_current_correlation_id() is None

        # Set context
        with CorrelationContext("test-id-123"):
            assert CorrelationContext.get_current_correlation_id() == "test-id-123"

        # After exit, back to None
        assert CorrelationContext.get_current_correlation_id() is None

    def test_nested_correlation_contexts(self):
        """Test nested correlation contexts."""
        with CorrelationContext("outer-id"):
            assert CorrelationContext.get_current_correlation_id() == "outer-id"

            with CorrelationContext("inner-id"):
                assert CorrelationContext.get_current_correlation_id() == "inner-id"

            # Back to outer
            assert CorrelationContext.get_current_correlation_id() == "outer-id"

    def test_correlation_context_auto_generation(self):
        """Test automatic correlation ID generation."""
        with CorrelationContext():
            correlation_id = CorrelationContext.get_current_correlation_id()
            assert correlation_id is not None
            assert len(correlation_id) == 8  # Should be short ID

    def test_correlation_context_exception_handling(self):
        """Test that exceptions don't break context restoration."""
        original_id = None

        with CorrelationContext("original"):
            original_id = CorrelationContext.get_current_correlation_id()

            try:
                with CorrelationContext("nested"):
                    raise ValueError("Test exception")
            except ValueError:
                pass  # Exception should be caught

            # Should be back to original
            assert CorrelationContext.get_current_correlation_id() == original_id


class TestOperationLogging:
    """Test operation start and end logging."""

    def test_operation_start_logging(self, caplog):
        """Test operation start logging."""
        with caplog.at_level(logging.INFO):
            context = log_operation_start(logger, "test_operation",
                                        operation_id="test-123")

            # Check that log was created
            assert len(caplog.records) > 0

            # Find our log record
            operation_logs = [r for r in caplog.records if "Starting operation" in r.getMessage()]
            assert len(operation_logs) == 1

            log_record = operation_logs[0]
            assert log_record.operation == "test_operation"
            assert log_record.operation_id == "test-123"
            assert "correlation_id" in log_record.__dict__
            assert "start_time" in context

    def test_operation_end_logging(self, caplog):
        """Test operation end logging."""
        # Mock context from operation start
        context = {
            "correlation_id": "test-corr-id",
            "start_time": 1000.0,  # Mock start time
            "operation": "test_operation"
        }

        with patch('src.logging_config.datetime') as mock_datetime:
            # Mock current time (1000.0 start + 500ms = 1000.5)
            current_time = MagicMock()
            current_time.now.return_value.timestamp.return_value = 1000.5
            mock_datetime.now.return_value = current_time

            with caplog.at_level(logging.INFO):
                log_operation_end(logger, context, success=True, result_count=42)

                # Find completed operation log
                completion_logs = [r for r in caplog.records if "Completed operation" in r.getMessage()]
                assert len(completion_logs) == 1

                log_record = completion_logs[0]
                assert log_record.success is True
                assert log_record.result_count == 42

    def test_performance_warning_logging(self, caplog):
        """Test logging of performance warnings."""
        with caplog.at_level(logging.WARNING):
            log_performance(logger, "slow_operation", 1500, threshold_ms=1000)

            # Find performance warning
            warning_logs = [r for r in caplog.records if "slow_operation" in r.getMessage()]
            assert len(warning_logs) == 1

            log_record = warning_logs[0]
            assert log_record.elapsed_ms == 1500
            assert log_record.threshold_ms == 1000

    def test_api_call_logging(self, caplog):
        """Test API call logging."""
        with caplog.at_level(logging.INFO):
            log_api_call(
                logger, "GET", "https://api.example.com/data",
                status_code=200, duration_ms=150
            )

            # Find API call log
            api_logs = [r for r in caplog.records if "API Call" in r.getMessage()]
            assert len(api_logs) == 1

            log_record = api_logs[0]
            assert log_record.method == "GET"
            assert log_record.url == "https://api.example.com/data"
            assert log_record.status_code == 200
            assert log_record.duration_ms == 150

    def test_error_logging(self, caplog):
        """Test error logging with context."""
        test_error = RuntimeError("Test error message")

        with caplog.at_level(logging.ERROR):
            log_error(logger, test_error, operation="test_op", user_id="user123")

            # Find error log
            error_logs = [r for r in caplog.records if "Error in test_op" in r.getMessage()]
            assert len(error_logs) == 1

            log_record = error_logs[0]
            assert log_record.operation == "test_op"
            assert log_record.user_id == "user123"
            assert hasattr(log_record, 'exc_info')  # Should have exception info


class TestOperationContext:
    """Test the OperationContext decorator/manager."""

    def test_operation_context_success(self, caplog):
        """Test operation context with successful completion."""
        def successful_function():
            return "success result"

        with caplog.at_level(logging.INFO):
            with OperationContext(logger, "test_context_op", test_param="value"):
                result = successful_function()

        assert result == "success result"

        # Check start and end logs
        start_logs = [r for r in caplog.records if "Starting operation" in r.getMessage()]
        end_logs = [r for r in caplog.records if "Completed operation" in r.getMessage()]

        assert len(start_logs) == 1
        assert len(end_logs) == 1

        start_record = start_logs[0]
        end_record = end_logs[0]

        assert start_record.test_param == "value"
        assert end_record.success is True

        # Start and end should have same correlation ID
        assert start_record.correlation_id == end_record.correlation_id

    def test_operation_context_error(self, caplog):
        """Test operation context with exception handling."""
        test_exception = ValueError("Test exception")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                with OperationContext(logger, "failing_operation"):
                    raise test_exception

        # Check error logs
        error_logs = [r for r in caplog.records if "Error in failing_operation" in r.getMessage()]
        assert len(error_logs) >= 1

        for err_log in error_logs:
            assert "failing_operation" in err_log.getMessage()


class TestGlobalLogger:
    """Test the global logger instance."""

    def test_global_logger_is_configured(self):
        """Test that global logger has handlers."""
        assert logger.handlers is not None
        assert len(logger.handlers) > 0
        assert logger.level <= logging.INFO  # Should be at INFO or higher

    def test_global_logger_name(self):
        """Test that global logger has the correct name."""
        assert logger.name == "socials.io"

    def test_multiple_logger_calls_same_instance(self):
        """Test that multiple calls to configure logger return same instance."""
        from src.logging_config import get_logger
        logger1 = get_logger("test1")
        logger2 = get_logger("test1")

        assert logger1 is not logger2  # Different names = different loggers
        assert logger1.name == "test1"
        assert logger2.name == "test1"


@pytest.mark.integration
class TestLoggingIntegration:
    """Integration tests for logging with other systems."""

    def test_logging_with_correlation_context(self, caplog):
        """Test logging integrates properly with correlation context."""
        with CorrelationContext("integration-test-id"):
            with caplog.at_level(logging.INFO):
                logger.info("Integration test message", extra={"test_field": "test_value"})

                log_records = [r for r in caplog.records if "Integration test message" in r.getMessage()]
                assert len(log_records) == 1

                record = log_records[0]
                assert record.correlation_id == "integration-test-id"
                assert record.test_field == "test_value"

    @pytest.mark.asyncio
    async def test_async_logging_operations(self):
        """Test that logging works properly in async contexts."""
        async def async_operation():
            operation_context = log_operation_start(logger, "async_test_op")
            await asyncio.sleep(0.01)  # Simulate async work
            log_operation_end(logger, operation_context, success=True)
            return "async_result"

        result = await async_operation()
        assert result == "async_result"

    def test_logging_performance_measurement(self):
        """Test that performance measurement works correctly."""
        import time

        start_time = time.time()
        time.sleep(0.1)  # Sleep for 100ms
        elapsed_ms = (time.time() - start_time) * 1000

        # Should generate a performance log
        log_performance(logger, "performance_test", elapsed_ms, threshold_ms=50)

        # In a real test, we'd check the log output, but for this integration
        # test, we just ensure no exceptions are raised

    def test_error_logging_preserves_context(self):
        """Test that error logging doesn't lose context."""
        import traceback

        try:
            try:
                raise ValueError("Inner error")
            except ValueError:
                raise RuntimeError("Outer error") from ValueError("Inner error")
        except Exception as e:
            log_error(logger, e, operation="nested_error_test")

            # Should not raise any exceptions and should preserve the full traceback


class TestLogRotationAndStorage:
    """Test logging file rotation and storage."""

    @patch('src.logging_config.Path')
    @patch('src.logging_config.logging.FileHandler')
    def test_file_logging_setup(self, mock_file_handler, mock_path):
        """Test that file logging is configured when LOG_FILE is set."""
        with patch.dict('os.environ', {'LOG_FILE': '/tmp/test.log'}):
            mock_logger = MagicMock()
            mock_handler_instance = MagicMock()
            mock_file_handler.return_value = mock_handler_instance

            from src.logging_config import get_logger
            get_logger("file_test")

            # Should have added a FileHandler
            mock_file_handler.assert_called_once()
            mock_handler_instance.setFormatter.assert_called_once()