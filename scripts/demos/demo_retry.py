#!/usr/bin/env python3
"""
Demo script showing retry system in action
Run this to see how retries handle failures gracefully
"""
import asyncio
import random
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from retry_utils import retry_async, database_retry_manager, playwright_retry_manager, CircuitBreaker, CorrelationContext
from logging_config import logger

class SimulatedFailure:
    """Simulates different types of failures for demo."""

    def __init__(self, fail_count=2):
        self.attempts = 0
        self.fail_count = fail_count

    def __call__(self):
        self.attempts += 1
        if self.attempts <= self.fail_count:
            if random.choice([True, False]):
                raise ConnectionError(f"The network is busy (attempt {self.attempts})")
            else:
                raise TimeoutError(f"Operation timed out (attempt {self.attempts})")
        return f"Success on attempt {self.attempts}!"

async def demo_database_retry():
    """Demo database-style retries with exponential backoff."""
    print("🔄 Demo: Database retry with exponential backoff")
    print("=" * 60)

    failure_simulator = SimulatedFailure(fail_count=2)

    try:
        result = await retry_async(failure_simulator, manager=database_retry_manager)
        print(f"✅ Database operation succeeded: {result}")
    except Exception as e:
        print(f"❌ Database operation failed: {e}")

    print()

def demo_circuit_breaker():
    """Demo circuit breaker pattern."""
    print("🔌 Demo: Circuit breaker pattern")
    print("=" * 60)

    class FailingService:
        def __init__(self):
            self.failures = 0

        def __call__(self):
            self.failures += 1
            if self.failures <= 6:  # More failures than threshold
                raise ConnectionError("Service temporarily unavailable")
            return "Service recovered!"

    service = FailingService()
    breaker = CircuitBreaker(failure_threshold=3, name="demo_service")

    for i in range(8):
        print(f"Attempt {i+1}: ", end="")
        try:
            with breaker(service):
                print("✅ Success!")
        except Exception as e:
            print(f"❌ {type(e).__name__}: {e}")
            if "OPEN" in str(e):
                print("🔒 Circuit breaker is OPEN - fast failing remaining requests")
                break
        asyncio.run(asyncio.sleep(0.1))  # Small delay between attempts

    print()

async def demo_browser_retry():
    """Demo browser operation retries with linear backoff."""
    print("🌐 Demo: Browser operation retry with linear backoff")
    print("=" * 60)

    class BrowserSimulator:
        def __init__(self):
            self.screenshot_count = 0

        def mock_screenshot(self):
            self.screenshot_count += 1
            if self.screenshot_count <= 1:  # Fail twice then succeed
                raise TimeoutError("Browser page load timed out")
            return f"Screenshot created successfully (attempt {self.screenshot_count})"

    browser = BrowserSimulator()

    try:
        result = await retry_async(browser.mock_screenshot, manager=playwright_retry_manager)
        print(f"✅ Browser operation succeeded: {result}")
    except Exception as e:
        print(f"❌ Browser operation failed: {e}")

    print()

async def main():
    """Run all demo functions."""
    print("🚀 Retry System Demo")
    print("===================\n")

    # Simulate setting up correlation context for session
    correlation_id = "demo-session-retry"
    with CorrelationContext(correlation_id):
        await demo_database_retry()
        demo_circuit_breaker()
        await demo_browser_retry()

    print("🎉 Demo completed!")
    print("=" * 60)
    print("This demonstrates:")
    print("• Exponential backoff for database operations")
    print("• Circuit breaker preventing cascade failures")
    print("• Linear backoff for browser operations")
    print("• Automatic retry with structured logging")
    print("• Correlation IDs for tracking across operations")

if __name__ == "__main__":
    asyncio.run(main())