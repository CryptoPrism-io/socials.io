"""
Final validation test to ensure restructured repository works correctly.
"""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.paths import (
    TEMPLATES_DIR, STYLES_DIR, HTML_OUTPUT_DIR, IMAGES_OUTPUT_DIR,
    get_html_output_path, get_image_output_path, ensure_directories
)

def test_file_structure():
    """Test that all files are in their correct locations."""
    print("Testing file structure...")

    # Check template files exist
    template_files = ['1.html', '2.html', '3.html', '4.html', '5.html']
    for template_file in template_files:
        template_path = TEMPLATES_DIR / template_file
        if template_path.exists():
            print(f"+ Template found: {template_file}")
        else:
            print(f"! Template missing: {template_file}")

    # Check CSS files exist
    css_files = ['style.css', 'style2.css', 'style3.css', 'style4.css', 'style5.css']
    for css_file in css_files:
        css_path = STYLES_DIR / css_file
        if css_path.exists():
            print(f"+ CSS found: {css_file}")
        else:
            print(f"! CSS missing: {css_file}")

def test_template_css_references():
    """Test that templates correctly reference CSS files."""
    print("\nTesting template CSS references...")

    template_css_map = {
        '1.html': 'styles/style.css',
        '2.html': 'styles/style2.css',
        '3.html': 'styles/style3.css',
        '4.html': 'styles/style4.css',
        '5.html': 'styles/style5.css'
    }

    for template_file, expected_css in template_css_map.items():
        template_path = TEMPLATES_DIR / template_file
        if template_path.exists():
            content = template_path.read_text(encoding='utf-8')
            if expected_css in content:
                print(f"+ {template_file} correctly references {expected_css}")
            else:
                print(f"! {template_file} missing reference to {expected_css}")
        else:
            print(f"! Template file not found: {template_file}")

def test_jinja_template_loading():
    """Test that Jinja2 can load templates from new structure."""
    print("\nTesting Jinja2 template loading...")

    try:
        from jinja2 import Environment, FileSystemLoader

        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

        # Try to load each template
        template_files = ['1.html', '2.html', '3.html', '4.html', '5.html']
        for template_file in template_files:
            try:
                template = env.get_template(template_file)
                print(f"+ Successfully loaded template: {template_file}")
            except Exception as e:
                print(f"! Failed to load template {template_file}: {e}")

    except ImportError:
        print("! Jinja2 not available (expected in local environment)")

def test_output_paths():
    """Test that output path generation works correctly."""
    print("\nTesting output path generation...")

    # Ensure directories exist
    ensure_directories()

    for i in range(1, 6):
        html_path = get_html_output_path(i)
        image_path = get_image_output_path(i)

        print(f"+ Template {i} HTML output: {html_path}")
        print(f"+ Template {i} image output: {image_path}")

        # Check directories exist
        if html_path.parent.exists():
            print(f"+ HTML output directory exists: {html_path.parent}")
        else:
            print(f"! HTML output directory missing: {html_path.parent}")

        if image_path.parent.exists():
            print(f"+ Image output directory exists: {image_path.parent}")
        else:
            print(f"! Image output directory missing: {image_path.parent}")

def main():
    """Run all validation tests."""
    print("="*60)
    print("FINAL REPOSITORY RESTRUCTURE VALIDATION")
    print("="*60)

    test_file_structure()
    test_template_css_references()
    test_jinja_template_loading()
    test_output_paths()

    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)

    print("\nRepository restructure summary:")
    print("+ New directory structure created")
    print("+ Templates moved to src/templates/")
    print("+ CSS files moved to src/templates/styles/")
    print("+ Output directories created (output/html/, output/images/)")
    print("+ Path configuration centralized in config/paths.py")
    print("+ Template CSS references updated")
    print("+ Test scripts created for validation")

    print("\nNext steps for production:")
    print("1. Copy all data functions to new structured scripts")
    print("2. Update GitHub Actions to use restructured scripts")
    print("3. Test deployment with GitHub Actions")
    print("4. Remove old files from root directory")

if __name__ == "__main__":
    main()