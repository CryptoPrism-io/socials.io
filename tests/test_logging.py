#!/usr/bin/env python3
"""
Demo script to show structured JSON logging output
Run this to see the logging format in action
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from logging_config import logger, CorrelationContext, log_operation_start, log_operation_end, log_error, log_performance

async def demo_logging():
    """Demonstrate the structured logging system."""
    print("=== Structured JSON Logging Demo ===\n")

    # Set correlation context
    with CorrelationContext("demo-session-123"):
        # Session start
        session_context = log_operation_start(
            logger, "demo_session",
            _log_demo_type="structured_logging"
        )

        try:
            # Simulate operations with timing
            import time
            await asyncio.sleep(0.1)  # Simulate work

            # Data fetching operation
            fetch_context = log_operation_start(
                logger, "fetch_demo_data",
                _log_data_type="sample_crypto_data"
            )
            await asyncio.sleep(0.05)
            log_operation_end(
                logger, fetch_context, success=True,
                _log_record_count=24,
                _log_duration_ms=50
            )

            # Template rendering operation
            render_context = log_operation_start(
                logger, "render_template_demo",
                _log_template_num=1
            )
            await asyncio.sleep(0.15)
            log_operation_end(
                logger, render_context, success=True,
                _log_file_size_kb=45.2
            )

            # Performance monitoring
            log_performance(logger, "template_rendering", 150, threshold_ms=200)

            # Simulate a warning (slow operation)
            slow_context = log_operation_start(logger, "slow_operation_demo")
            await asyncio.sleep(0.3)
            log_performance(logger, "slow_database_query", 300, threshold_ms=200)
            log_operation_end(logger, slow_context, success=True, _log_duration_ms=300)

        except Exception as e:
            log_error(logger, e, "demo_session")
            log_operation_end(logger, session_context, success=False, _log_error=str(e))
            return

        # Session completion
        log_operation_end(
            logger, session_context, success=True,
            _log_demo_completed=True
        )

    print("\n=== Demo completed! ===")
    print("Check above for JSON logging format.")
    print("Each log entry includes timestamp, correlation_id, duration_ms, and structured metadata.")

if __name__ == "__main__":
    asyncio.run(demo_logging())