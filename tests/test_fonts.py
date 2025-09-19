"""Tests for self-hosted font implementation."""
import pytest
from pathlib import Path
from src.config import config


class TestSelfHostedFonts:
    """Test self-hosted fonts implementation."""

    def test_fonts_directory_exists(self):
        """Test that fonts directory exists."""
        fonts_dir = config.paths.templates_dir / "fonts"
        assert fonts_dir.exists(), "Fonts directory should exist"
        assert fonts_dir.is_dir(), "Fonts path should be a directory"

    def test_fonts_css_exists(self):
        """Test that fonts.css file exists."""
        fonts_css = config.paths.templates_dir / "fonts" / "fonts.css"
        assert fonts_css.exists(), "fonts.css should exist"

    def test_fonts_css_contains_font_faces(self):
        """Test that fonts.css contains proper @font-face declarations."""
        fonts_css = config.paths.templates_dir / "fonts" / "fonts.css"

        with open(fonts_css, 'r') as f:
            content = f.read()

        # Check for required font families
        assert '@font-face' in content, "Should contain @font-face declarations"
        assert "font-family: 'Poppins'" in content, "Should define Poppins font"
        assert "font-family: 'Inter'" in content, "Should define Inter font"
        assert "font-family: 'Orbitron'" in content, "Should define Orbitron font"

        # Check for font weights
        assert 'font-weight: 300' in content, "Should include light weights"
        assert 'font-weight: 400' in content, "Should include normal weights"
        assert 'font-weight: 700' in content, "Should include bold weights"

    def test_templates_use_local_fonts(self):
        """Test that all templates reference local fonts, not external."""
        template_files = [
            config.paths.templates_dir / "1.html",
            config.paths.templates_dir / "2.html",
            config.paths.templates_dir / "3.html",
            config.paths.templates_dir / "4.html",
            config.paths.templates_dir / "5.html",
            config.paths.templates_dir / "6.html",
        ]

        for template_file in template_files:
            if template_file.exists():
                with open(template_file, 'r') as f:
                    content = f.read()

                # Should NOT contain external Google Fonts
                assert 'googleapis.com' not in content, f"{template_file.name} should not reference external fonts"
                assert 'fonts.google.com' not in content, f"{template_file.name} should not reference external fonts"

                # Should contain local fonts reference
                assert 'fonts/fonts.css' in content, f"{template_file.name} should reference local fonts"

    def test_font_fallbacks_defined(self):
        """Test that font fallbacks are properly defined."""
        fonts_css = config.paths.templates_dir / "fonts" / "fonts.css"

        with open(fonts_css, 'r') as f:
            content = f.read()

        # Check for fallback font classes
        assert '.poppins-fallback' in content, "Should define Poppins fallback"
        assert '.inter-fallback' in content, "Should define Inter fallback"
        assert '.orbitron-fallback' in content, "Should define Orbitron fallback"

        # Check for system font fallbacks
        assert 'sans-serif' in content, "Should include sans-serif fallbacks"
        assert '-apple-system' in content, "Should include Apple system fonts"
        assert 'BlinkMacSystemFont' in content, "Should include Blink system fonts"

    def test_fonts_directory_structure(self):
        """Test that fonts directory has proper structure."""
        fonts_dir = config.paths.templates_dir / "fonts"

        # Required files should exist
        required_files = [
            "fonts.css",
            "README.md",
            "download_fonts.py"
        ]

        for required_file in required_files:
            file_path = fonts_dir / required_file
            assert file_path.exists(), f"{required_file} should exist in fonts directory"

    def test_download_script_functionality(self):
        """Test that font download script exists and is valid Python."""
        download_script = config.paths.templates_dir / "fonts" / "download_fonts.py"

        assert download_script.exists(), "Font download script should exist"

        # Test that it's valid Python
        with open(download_script, 'r', encoding='utf-8') as f:
            content = f.read()

        # Should be executable Python script
        assert 'def main():' in content, "Should have main function"
        assert 'download_font' in content, "Should have download function"
        assert '__name__ == "__main__"' in content, "Should be executable script"