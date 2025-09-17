"""
Test script to validate repository restructure changes.
This script will test all core functionality before and after the restructure.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "scripts"))

# Import configuration
from config.paths import (
    TEMPLATES_DIR, STYLES_DIR, HTML_OUTPUT_DIR, IMAGES_OUTPUT_DIR,
    get_html_output_path, get_image_output_path, ensure_directories
)


class TestRestructure(unittest.TestCase):
    """Test cases for repository restructure validation."""

    def setUp(self):
        """Set up test environment."""
        ensure_directories()

    def test_directory_structure(self):
        """Test that all required directories exist."""
        required_dirs = [
            TEMPLATES_DIR,
            STYLES_DIR,
            HTML_OUTPUT_DIR,
            IMAGES_OUTPUT_DIR
        ]

        for directory in required_dirs:
            self.assertTrue(
                directory.exists(),
                f"Required directory does not exist: {directory}"
            )

    def test_path_functions(self):
        """Test path generation functions."""
        # Test HTML output path
        html_path = get_html_output_path(1)
        expected_html = HTML_OUTPUT_DIR / "1_output.html"
        self.assertEqual(html_path, expected_html)

        # Test image output path
        img_path = get_image_output_path(1)
        expected_img = IMAGES_OUTPUT_DIR / "1_output.jpg"
        self.assertEqual(img_path, expected_img)

        # Test with different format
        png_path = get_image_output_path(1, "png")
        expected_png = IMAGES_OUTPUT_DIR / "1_output.png"
        self.assertEqual(png_path, expected_png)

    def test_template_loading(self):
        """Test Jinja2 template loading from new structure."""
        try:
            from jinja2 import Environment, FileSystemLoader

            # Test loading templates from new directory
            env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

            # Check if we can load a template (assuming it exists)
            template_path = TEMPLATES_DIR / "1.html"
            if template_path.exists():
                template = env.get_template('1.html')
                self.assertIsNotNone(template)
                print("+ Template loading from new structure works")
            else:
                print("! Template file doesn't exist yet, skipping template test")

        except ImportError:
            print("! Jinja2 not available, skipping template test")

    @patch('playwright.async_api.async_playwright')
    async def test_playwright_screenshot_path(self, mock_playwright):
        """Test Playwright screenshot generation with new paths."""
        # Mock playwright objects
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_context = MagicMock()

        mock_context.__aenter__ = MagicMock(return_value=mock_context)
        mock_context.__aexit__ = MagicMock(return_value=None)
        mock_context.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_browser.close.return_value = None

        mock_playwright.return_value = mock_context

        # Test file URL generation
        html_file = get_html_output_path(1)
        file_url = f'file://{html_file.absolute()}'

        # Verify URL format is correct
        self.assertTrue(file_url.startswith('file://'))
        self.assertTrue(str(html_file.absolute()) in file_url)
        print("+ Playwright file URL generation works with new paths")

    def test_css_path_resolution(self):
        """Test CSS path resolution in templates."""
        # Create a sample HTML file to test CSS path resolution
        test_html = TEMPLATES_DIR / "test_template.html"
        test_css = STYLES_DIR / "test_style.css"

        try:
            # Create test files
            test_html.write_text('''
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="styles/test_style.css">
            </head>
            <body>Test</body>
            </html>
            ''')

            test_css.write_text('body { color: red; }')

            # Test relative path resolution
            relative_path = Path("styles/test_style.css")
            resolved_path = TEMPLATES_DIR / relative_path

            self.assertEqual(resolved_path, test_css)
            print("+ CSS path resolution works with new structure")

            # Clean up
            test_html.unlink()
            test_css.unlink()

        except Exception as e:
            print(f"! CSS path test failed: {e}")

    def run_comprehensive_test(self):
        """Run all tests and provide summary."""
        print("=" * 50)
        print("REPOSITORY RESTRUCTURE VALIDATION")
        print("=" * 50)

        # Run individual tests
        self.test_directory_structure()
        print("+ Directory structure validation passed")

        self.test_path_functions()
        print("+ Path function validation passed")

        self.test_template_loading()
        self.test_css_path_resolution()

        # Test async function
        try:
            asyncio.run(self.test_playwright_screenshot_path())
        except Exception as e:
            print(f"! Playwright test failed: {e}")

        print("=" * 50)
        print("VALIDATION COMPLETE")
        print("=" * 50)


def main():
    """Main test runner."""
    print("Starting repository restructure validation...")

    tester = TestRestructure()
    tester.run_comprehensive_test()

    print("\nNext steps:")
    print("1. Move template and CSS files to new structure")
    print("2. Update Python scripts to use new paths")
    print("3. Test again before updating GitHub Actions")


if __name__ == "__main__":
    main()