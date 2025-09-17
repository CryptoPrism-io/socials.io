"""
Simple test for path structure without external dependencies.
"""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import path configuration
from config.paths import (
    TEMPLATES_DIR, HTML_OUTPUT_DIR, IMAGES_OUTPUT_DIR,
    get_html_output_path, get_image_output_path, ensure_directories
)

def test_basic_paths():
    """Test basic path configuration."""
    print("Testing basic path configuration...")

    # Ensure directories exist
    ensure_directories()

    # Test path generation
    html_path = get_html_output_path(1)
    image_path = get_image_output_path(1)

    print(f"Template directory: {TEMPLATES_DIR}")
    print(f"HTML output directory: {HTML_OUTPUT_DIR}")
    print(f"Images output directory: {IMAGES_OUTPUT_DIR}")
    print(f"HTML output path for template 1: {html_path}")
    print(f"Image output path for template 1: {image_path}")

    # Test Jinja2 setup (if available)
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        print("+ Jinja2 environment setup successful")
    except ImportError:
        print("! Jinja2 not available (expected in local environment)")

    print("+ Path structure test completed successfully")

if __name__ == "__main__":
    test_basic_paths()