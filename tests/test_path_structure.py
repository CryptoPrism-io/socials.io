"""Test path structure and file system setup."""
import pytest
from pathlib import Path
from unittest.mock import patch

from src.config import config


@pytest.mark.unit
class TestPathStructure:
    """Test path structure and file system setup."""

    def test_path_configuration_loaded(self):
        """Test that path configuration is properly loaded."""
        assert config.paths is not None
        assert isinstance(config.paths.project_root, Path)

    def test_template_directory_structure(self):
        """Test template directory and file structure."""
        templates_dir = config.paths.templates_dir

        assert templates_dir.name == "templates"
        assert templates_dir.parent.name == "src"

        # Check template files exist
        template_files = config.paths.get_template_files()
        assert isinstance(template_files, list)
        assert len(template_files) >= 1

        # Verify at least template 1 exists
        template_1 = templates_dir / "1.html"
        if template_1.exists():
            assert template_1.stat().st_size > 0

    def test_output_directory_structure(self):
        """Test output directory structure."""
        html_dir = config.paths.html_output_dir
        images_dir = config.paths.images_output_dir

        assert html_dir.name == "html"
        assert images_dir.name == "images"

        # Both should be in output/
        assert html_dir.parent.name == "output"
        assert images_dir.parent.name == "output"

    def test_path_generation_functions(self):
        """Test path generation utility functions."""
        template_num = 1

        html_path = config.paths.get_html_output_path(template_num)
        image_path = config.paths.get_image_output_path(template_num)

        assert html_path.name == "1_output.html"
        assert image_path.name == "1_output.jpg"

        assert html_path.parent == config.paths.html_output_dir
        assert image_path.parent == config.paths.images_output_dir

    def test_image_path_with_format(self):
        """Test image path generation with different formats."""
        image_png = config.paths.get_image_output_path(2, "png")
        image_jpg = config.paths.get_image_output_path(2, "jpg")
        image_jpeg = config.paths.get_image_output_path(2, "jpeg")

        assert image_png.name == "2_output.png"
        assert image_jpg.name == "2_output.jpg"
        assert image_jpeg.name == "2_output.jpeg"

    def test_ensure_directories_function(self):
        """Test that ensure_directories creates required structure."""
        from src.config import config

        # Mock Path.mkdir to avoid actually creating directories
        with patch.object(Path, 'mkdir') as mock_mkdir:
            with patch.object(Path, 'exists', return_value=False):
                config.paths.ensure_directories()

                # Verify mkdir was called for required directories
                calls = mock_mkdir.call_args_list
                assert len(calls) >= 6  # Should create at least 6 directories

                # Check that parents=True was used
                for call in calls:
                    assert call[1]['parents'] is True
                    assert call[1]['exist_ok'] is True

    def test_template_file_discovery(self):
        """Test that template files can be properly discovered."""
        templates = config.paths.get_template_files()
        expected_html_files = len([f for f in config.paths.templates_dir.iterdir()
                                 if f.suffix == '.html' and f.stem.isdigit()])

        assert len(templates) == expected_html_files

        # Verify all are Path objects with correct extensions
        for template in templates:
            assert isinstance(template, Path)
            assert template.suffix == '.html'
            assert template.stem.isdigit()

    def test_style_file_discovery(self):
        """Test that style files can be discovered."""
        styles = config.paths.get_style_files()

        # Should have styles for each template
        assert len(styles) >= 6  # style.css through style6.css

        # Verify all follow naming convention
        for style in styles:
            assert isinstance(style, Path)
            assert style.suffix == '.css'
            assert style.name.startswith('style')
            if len(style.stem) > 5:  # style.css vs style2.css
                assert style.stem[5:].isdigit()


class TestPathIntegration:
    """Integration tests for path operations."""

    def test_path_resolution_works(self):
        """Test that all paths resolve to valid locations."""
        paths_to_test = [
            config.paths.project_root,
            config.paths.src_dir,
            config.paths.templates_dir,
            config.paths.output_dir,
            config.paths.html_output_dir,
            config.paths.images_output_dir,
        ]

        for path in paths_to_test:
            # Path should be resolvable
            resolved = path.resolve()
            assert resolved.exists() or resolved.parent.exists()

            # Should be absolute path after resolution
            assert resolved.is_absolute()

    def test_directory_permissions(self):
        """Test that directories have appropriate permissions."""
        # This is a basic test that directories can be accessed
        try:
            list(config.paths.templates_dir.iterdir())
            assert True  # Can list directory contents
        except (OSError, PermissionError):
            pytest.fail("Cannot access template directory")

    def test_jinja2_template_compatibility(self):
        """Test Jinja2 compatibility with template files."""
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader(str(config.paths.templates_dir)))

            # Try to load a template
            template = env.get_template("1.html")
            assert template is not None

        except ImportError:
            pytest.skip("Jinja2 not available")
        except FileNotFoundError:
            pytest.skip("Template files not available for testing")


@pytest.mark.slow
class TestPathCleanup:
    """Tests for path cleanup operations (marked as slow)."""

    def test_temporary_path_cleanup(self, tmp_path):
        """Test that temporary paths can be created and cleaned up."""
        test_dir = tmp_path / "test_output"
        test_dir.mkdir()
        test_file = test_dir / "test.html"
        test_file.write_text("<html>Test</html>")

        assert test_file.exists()
        assert test_file.read_text() == "<html>Test</html>"

    def test_path_object_equality(self):
        """Test that Path objects behave correctly in set operations."""
        paths = [
            config.paths.templates_dir / "1.html",
            config.paths.templates_dir / "2.html",
            config.paths.templates_dir / "1.html",  # Duplicate
        ]

        unique_paths = set(paths)

        # Should have only 2 unique paths
        assert len(unique_paths) == 2
        assert len(paths) == 3