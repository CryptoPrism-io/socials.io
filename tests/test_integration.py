"""Integration tests for main application functionality."""
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from src.config import config


@pytest.mark.integration
class TestTemplateIntegration:
    """Test template rendering and HTML generation."""

    def test_template_file_discovery(self):
        """Test that template files can be discovered."""
        template_files = config.paths.get_template_files()

        # Should find at least the known template files
        assert len(template_files) >= 1  # At least template 1 should exist

        # All should be .html files
        for template_file in template_files:
            assert template_file.suffix == '.html'
            assert template_file.exists()

    def test_template_rendering_basic(self):
        """Test basic template rendering functionality."""
        template_path = config.paths.templates_dir / "1.html"

        if template_path.exists():
            # Basic template validation
            with open(template_path, 'r') as f:
                content = f.read()

            # Should contain basic HTML structure
            assert '<!DOCTYPE html>' in content
            assert '<html>' in content
            assert '<head>' in content
            assert '<body>' in content

            # Should have Jinja2 template variables
            assert '{{' in content or '{%' in content  # Template syntax

    @patch('src.config.Path')
    def test_output_directory_creation(self, mock_path_class):
        """Test that output directories are created properly."""
        # Mock the path creation
        mock_path = MagicMock()
        mock_path_class.return_value = mock_path

        # Call ensure_directories
        config.paths.ensure_directories()

        # Verify mkdir was called
        assert mock_path.mkdir.called

        # Check that needed directories were attempted
        call_args_list = mock_path.mkdir.call_args_list
        assert len(call_args_list) > 0


@pytest.mark.integration
class TestDatabaseOperationsIntegration:
    """Test database operation integrations."""

    @patch('pandas.read_sql_query')
    @patch('src.config.config.database.get_connection_url')
    def test_data_fetching_with_mocking(self, mock_get_url, mock_read_sql):
        """Test data fetching with mocked database connection."""
        from src.scripts.instapost import fetch_data_top_24_coins
        import asyncio

        # Mock the database connection
        mock_engine = MagicMock()
        mock_get_url.return_value = "postgresql+psycopg2://test"

        # Mock the pandas query result
        mock_df = pd.DataFrame({
            'slug': ['bitcoin', 'ethereum'],
            'cmc_rank': [1, 2],
            'symbol': ['BTC', 'ETH'],
            'price': [50000.0, 3000.0],
            'percent_change24h': [2.5, -1.3],
            'market_cap': [1000000000000.0, 350000000000.0]
        })
        mock_read_sql.return_value = mock_df

        # Test the data fetching
        async def test_fetch():
            return await fetch_data_top_24_coins(mock_engine)

        result_df = asyncio.run(test_fetch())

        # Verify the result
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 2
        assert list(result_df['symbol']) == ['BTC', 'ETH']


@pytest.mark.integration
class TestImageGenerationIntegration:
    """Test image generation integration (with mocks)."""

    @patch('playwright.async_api.async_playwright')
    @patch('src.config.Path')
    def test_image_generation_mock_workflow(self, mock_path_class, mock_playwright):
        """Test image generation workflow with mocked Playwright."""
        from src.scripts.instapost import generate_image_from_html
        import asyncio

        # Mock Path and file operations
        mock_html_path = MagicMock()
        mock_image_path = MagicMock()
        mock_path_class.return_value = mock_html_path
        mock_image_path.absolute.return_value = "/tmp/test.html"

        # Mock Playwright
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()

        mock_page.set_viewport_size = MagicMock()
        mock_page.emulate_media = MagicMock()
        mock_page.goto = MagicMock(return_value=asyncio.Future())
        mock_page.goto.return_value.set_result(None)
        mock_page.screenshot = MagicMock(return_value=asyncio.Future())
        mock_page.screenshot.return_value.set_result(None)

        mock_browser.new_page.return_value = mock_page
        mock_context.start.return_value = mock_browser

        mock_playwright.return_value.__aenter__.return_value = mock_context
        mock_playwright.return_value.__aexit__.return_value = None

        async def test_generation():
            await generate_image_from_html(
                "test.html",
                "test.jpg",
                viewport_width=1080
            )

        # Should not raise exceptions
        asyncio.run(test_generation())

        # Verify Playwright calls
        mock_page.set_viewport_size.assert_called_with({"width": 1080, "height": 1080})
        mock_page.emulate_media.assert_called_once()
        mock_page.screenshot.assert_called_once()


@pytest.mark.integration
class TestConfigurationIntegration:
    """Test the configuration system as a whole."""

    def test_configuration_validation_pipeline(self):
        """Test that the entire configuration validation works."""
        # This test validates that all configuration components work together
        try:
            config.validate_all()

            # If we get here without exceptions, the configuration is valid
            # (may fail in test environments due to missing env vars, which is expected)

        except ValueError as e:
            # Expected in test environments if env vars are missing
            assert "configuration" in str(e).lower() or "environment" in str(e).lower()

        except Exception as e:
            # Other exceptions should not occur
            pytest.fail(f"Unexpected configuration error: {e}")

    def test_path_configuration_integration(self):
        """Test that path configuration works end-to-end."""
        # Test various path operations
        templates = config.paths.get_template_files()
        styles = config.paths.get_style_files()

        # Should return valid Path objects
        assert all(isinstance(t, Path) for t in templates)
        assert all(isinstance(s, Path) for s in styles)

        # Test output path generation
        html_path = config.paths.get_html_output_path(1)
        image_path = config.paths.get_image_output_path(1, "png")

        assert html_path.name == "1_output.html"
        assert image_path.name == "1_output.png"
        assert "html" in str(html_path.parent)
        assert "images" in str(image_path.parent)


@pytest.mark.integration
class TestRetrySystemIntegration:
    """Test retry system integration with other components."""

    @patch('asyncio.sleep')  # Speed up tests by avoiding real delays
    def test_retry_with_database_mock(self, mock_sleep):
        """Test database retry integration."""
        from src.retry_utils import retry_async
        import asyncio

        attempt_count = 0
        def failing_db_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Temporary DB failure")
            return "DB connected"

        async def test_db_retry():
            return await retry_async(failing_db_operation, manager=database_retry_manager)

        result = asyncio.run(test_db_retry())

        assert result == "DB connected"
        assert attempt_count == 3  # Should have retried 2 times then succeeded
        assert mock_sleep.call_count == 2  # Should have slept 2 times

    @patch('asyncio.sleep')
    def test_circuit_breaker_integration(self, mock_sleep):
        """Test circuit breaker prevents cascade failures."""
        from src.retry_utils import CircuitBreaker, CircuitBreakerConfig
        import asyncio

        failure_count = 0
        def unreliable_service():
            nonlocal failure_count
            failure_count += 1
            if failure_count < 4:  # Fail 3 times, succeed on 4th
                raise ConnectionError("Service down")
            return "Service available"

        breaker = CircuitBreaker(
            CircuitBreakerConfig(failure_threshold=2, expected_exception=ConnectionError)
        )

        @breaker
        def call_service():
            return unreliable_service()

        # First few calls should fail and eventually open circuit
        for i in range(4):
            if i < 2:
                # Circuit still closed, operations should attempt
                try:
                    call_service()
                except ConnectionError:
                    pass  # Expected for first 2 calls
            else:
                # Circuit should be open, subsequent calls fail fast
                with pytest.raises(Exception):  # CircuitBreakerOpenException
                    call_service()


@pytest.mark.integration
class TestFileSystemOperations:
    """Test file system operations with temporary directories."""

    def setup_method(self):
        """Set up temporary directory for file tests."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="socials_test_"))

        # Copy some required files to temp directory for testing
        # This would be expanded in a real test suite

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_temporary_directory_creation(self):
        """Test that temporary directories can be created and cleaned."""
        test_subdir = self.temp_dir / "test_subdir"
        test_subdir.mkdir()

        assert test_subdir.exists()

        # Cleanup happens in teardown_method
        # shutil.rmtree(self.temp_dir) will be called automatically

    def test_file_path_resolution(self):
        """Test file path resolution in temporary directory."""
        test_file = self.temp_dir / "test.html"
        test_file.write_text("<html><body>Test</body></html>")

        # Should be able to read back
        content = test_file.read_text()
        assert "Test" in content
        assert test_file.exists()

    def test_template_path_structure(self):
        """Test template path structure matches expectations."""
        template_names = [f"{i}.html" for i in range(1, 7)]
        template_paths = [config.paths.templates_dir / name for name in template_names]

        # Check that paths follow expected structure
        for path in template_paths:
            assert path.name.endswith('.html')
            assert path.suffix == '.html'

            # Check that parent directory makes sense
            assert 'templates' in str(path.parent)


# Performance and load testing markers (would be expanded with actual tests)
@pytest.mark.performance
class TestPerformance:
    """Performance test marker."""

    def test_basic_performance_baseline(self):
        """Basic performance test - establish baseline."""
        # This would measure execution times and memory usage
        # Currently just a placeholder for future implementation
        pass

    @pytest.mark.slow
    def test_extended_load_test(self):
        """Extended load testing for high throughput scenarios."""
        # Placeholder for load testing implementation
        pass


@pytest.mark.load
class TestLoadHandling:
    """Load testing marker."""

    def test_many_concurrent_operations(self):
        """Test handling many concurrent operations."""
        # Would test the application's ability to handle high concurrency
        pass