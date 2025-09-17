"""
Path configuration for socials.io project.
Centralizes all file and directory paths for easy management.
"""
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Source directories
SRC_DIR = PROJECT_ROOT / "src"
SCRIPTS_DIR = SRC_DIR / "scripts"
TEMPLATES_DIR = SRC_DIR / "templates"
STYLES_DIR = TEMPLATES_DIR / "styles"
UTILS_DIR = SRC_DIR / "utils"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "output"
HTML_OUTPUT_DIR = OUTPUT_DIR / "html"
IMAGES_OUTPUT_DIR = OUTPUT_DIR / "images"

# Template files
TEMPLATE_FILES = [
    TEMPLATES_DIR / "1.html",
    TEMPLATES_DIR / "2.html",
    TEMPLATES_DIR / "3.html",
    TEMPLATES_DIR / "4.html",
    TEMPLATES_DIR / "5.html"
]

# Style files
STYLE_FILES = [
    STYLES_DIR / "style.css",
    STYLES_DIR / "style2.css",
    STYLES_DIR / "style3.css",
    STYLES_DIR / "style4.css",
    STYLES_DIR / "style5.css"
]

# Output file patterns


def get_html_output_path(template_num):
    """Get the output HTML file path for a given template number."""
    return HTML_OUTPUT_DIR / f"{template_num}_output.html"


def get_image_output_path(template_num, format="jpg"):
    """Get the output image file path for a given template number."""
    return IMAGES_OUTPUT_DIR / f"{template_num}_output.{format}"


def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        SRC_DIR, SCRIPTS_DIR, TEMPLATES_DIR, STYLES_DIR, UTILS_DIR,
        OUTPUT_DIR, HTML_OUTPUT_DIR, IMAGES_OUTPUT_DIR
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Legacy compatibility - for scripts that expect files in root


def get_legacy_path(filename):
    """Get path for files that should remain in project root during transition."""
    return PROJECT_ROOT / filename