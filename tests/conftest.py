"""Test configuration and fixtures."""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path for all tests
project_root = Path(__file__).parent.parent
src_path = project_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import modules after path setup
import pandas as pd
from src.config import config


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment and paths."""
    # Ensure all paths are available
    config.paths.ensure_directories()


@pytest.fixture
def sample_crypto_data():
    """Provide sample cryptocurrency data for tests."""
    return pd.DataFrame({
        'slug': ['bitcoin', 'ethereum', 'cardano'],
        'symbol': ['BTC', 'ETH', 'ADA'],
        'cmc_rank': [1, 2, 3],
        'price': [50000.0, 3000.0, 2.0],
        'percent_change24h': [2.5, -1.3, 5.8],
        'market_cap': [900000000000.0, 350000000000.0, 65000000000.0],
        'logo': ['btc.png', 'eth.png', 'ada.png']
    })


@pytest.fixture
def mock_database_engine():
    """Provide mock SQLAlchemy engine for tests."""
    from unittest.mock import MagicMock

    mock_engine = MagicMock()
    mock_engine.dispose = MagicMock()

    return mock_engine


@pytest.fixture
def mock_dataframe():
    """Provide mock Pandas DataFrame."""
    return pd.DataFrame({
        'column1': [1, 2, 3],
        'column2': ['a', 'b', 'c']
    })


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory structure."""
    # Create HTML and images directories
    html_dir = tmp_path / "html"
    images_dir = tmp_path / "images"
    html_dir.mkdir()
    images_dir.mkdir()

    return tmp_path


@pytest.fixture
def mock_playwright():
    """Mock Playwright for browser testing."""
    with patch('src.scripts.instapost.async_playwright') as mock_pw:
        mock_browser = mock_pw.return_value.__aenter__.return_value.chromium.launch.return_value.__aenter__.return_value
        mock_page = mock_browser.new_page.return_value

        # Set up async methods
        mock_page.set_viewport_size = patch('').start()
        mock_page.emulate_media = patch('').start()
        mock_page.goto = patch('', return_value=None).start()
        mock_page.screenshot = patch('', return_value=None).start()

        yield mock_pw


@pytest.fixture
def mock_correlation_context():
    """Provide mock correlation context for tests."""
    from src.logging_config import CorrelationContext

    class MockCorrelationContext:
        def __init__(self, correlation_id="test-correlation-id"):
            self.correlation_id = correlation_id

        def __enter__(self):
            CorrelationContext._correlation_id = self.correlation_id
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            CorrelationContext._correlation_id = None

        @staticmethod
        def get_current_id():
            return CorrelationContext.get_current_correlation_id()

    return MockCorrelationContext()


@pytest.fixture(autouse=True)
def reset_logging_context():
    """Reset logging context between tests."""
    from src.logging_config import CorrelationContext

    # Ensure clean state
    CorrelationContext._correlation_id = None

    yield

    # Clean up after test
    CorrelationContext._correlation_id = None


@pytest.fixture
def log_capture(caplog):
    """Enhanced logging capture fixture."""
    # Set logging level for tests
    caplog.set_level("DEBUG")

    return caplog


# Custom markers for test organization
def pytest_configure(config):
    """Add custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Tests that span multiple components")
    config.addinivalue_line("markers", "performance: Performance and timing tests")
    config.addinivalue_line("markers", "slow: Tests that take a long time to run")
    config.addinivalue_line("markers", "retry: Tests specifically for retry logic")
    config.addinivalue_line("markers", "load: Load testing marker")


# Shared utilities for tests
def assert_dataframe_not_empty(df):
    """Assert that a DataFrame is not empty."""
    assert not df.empty, "DataFrame is empty"
    assert len(df) > 0, "DataFrame has zero rows"


def assert_data_structure_valid(df):
    """Assert that cryptocurrency data has expected structure."""
    required_columns = ['slug', 'symbol', 'price']
    for col in required_columns:
        assert col in df.columns, f"Required column '{col}' missing"

    assert len(df) > 0, "DataFrame should not be empty"