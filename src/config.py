"""
Central configuration module for socials.io
Single source of truth for all application settings, paths, and environment variables.
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import timezone


@dataclass
class DatabaseConfig:
    """Database configuration with environment variable support."""

    host: str = field(default_factory=lambda: os.getenv('DB_HOST', '34.55.195.199'))
    port: int = field(default_factory=lambda: int(os.getenv('DB_PORT', '5432')))
    database: str = field(default_factory=lambda: os.getenv('DB_NAME', 'dbcp'))
    user: str = field(default_factory=lambda: os.getenv('DB_USER', 'yogass09'))
    password: str = field(default_factory=lambda: os.getenv('DB_PASSWORD', 'jaimaakamakhya'))
    ssl_mode: str = field(default_factory=lambda: os.getenv('DB_SSL_MODE', 'prefer'))
    connection_timeout: int = field(default_factory=lambda: int(os.getenv('DB_CONNECTION_TIMEOUT', '30')))
    pool_size: int = field(default_factory=lambda: int(os.getenv('DB_POOL_SIZE', '5')))

    def get_connection_url(self, driver: str = 'psycopg2') -> str:
        """Generate SQLAlchemy connection URL with driver."""
        return f"postgresql+{driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def validate(self) -> None:
        """Validate database configuration."""
        required = [self.host, self.database, self.user, self.password]
        if not all(required):
            raise ValueError("Database configuration incomplete. Missing required environment variables.")
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid database port: {self.port}")


@dataclass
class PathConfig:
    """Path configuration for all project directories and files."""

    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    # Core directories
    src_dir: Path = field(init=False)
    scripts_dir: Path = field(init=False)
    templates_dir: Path = field(init=False)
    styles_dir: Path = field(init=False)
    utils_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    html_output_dir: Path = field(init=False)
    images_output_dir: Path = field(init=False)

    def __post_init__(self):
        """Initialize computed paths."""
        self.src_dir = self.project_root / "src"
        self.scripts_dir = self.src_dir / "scripts"
        self.templates_dir = self.src_dir / "templates"
        self.styles_dir = self.templates_dir / "styles"
        self.utils_dir = self.src_dir / "utils"
        self.output_dir = self.project_root / "output"
        self.html_output_dir = self.output_dir / "html"
        self.images_output_dir = self.output_dir / "images"

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.src_dir, self.scripts_dir, self.templates_dir, self.styles_dir,
            self.utils_dir, self.output_dir, self.html_output_dir, self.images_output_dir
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_template_files(self) -> List[Path]:
        """Get list of template files."""
        return [self.templates_dir / f"{i}.html" for i in range(1, 7)]  # 1-6 templates

    def get_style_files(self) -> List[Path]:
        """Get list of style files."""
        return [self.styles_dir / f"style{i}.css" for i in range(1, 7)]  # style.css to style6.css

    def get_html_output_path(self, template_num: int) -> Path:
        """Get the output HTML file path for a given template number."""
        return self.html_output_dir / f"{template_num}_output.html"

    def get_image_output_path(self, template_num: int, format: str = "jpg") -> Path:
        """Get the output image file path for a given template number."""
        return self.images_output_dir / f"{template_num}_output.{format}"


@dataclass
class ImageConfig:
    """Configuration for image generation and quality settings."""

    width: int = field(default_factory=lambda: int(os.getenv('IMAGE_WIDTH', '1080')))  # Instagram standard
    height: int = field(default_factory=lambda: int(os.getenv('IMAGE_HEIGHT', '1080')))
    quality: int = field(default_factory=lambda: int(os.getenv('IMAGE_QUALITY', '95')))
    format: str = field(default_factory=lambda: os.getenv('IMAGE_FORMAT', 'jpg'))
    browser_timeout: int = field(default_factory=lambda: int(os.getenv('BROWSER_TIMEOUT', '60000')))  # ms
    viewport_scale: float = field(default_factory=lambda: float(os.getenv('VIEWPORT_SCALE', '1.0')))

    def validate(self) -> None:
        """Validate image configuration."""
        if not (100 <= self.width <= 10000) or not (100 <= self.height <= 10000):
            raise ValueError(f"Invalid image dimensions: {self.width}x{self.height}")
        if not (1 <= self.quality <= 100):
            raise ValueError(f"Invalid image quality: {self.quality}")
        if self.format.lower() not in ['jpg', 'png', 'jpeg']:
            raise ValueError(f"Unsupported image format: {self.format}")


@dataclass
class AppConfig:
    """General application configuration."""

    # Timezone settings
    timezone: timezone = field(default_factory=lambda: timezone.utc)
    datetime_format: str = field(default_factory=lambda: os.getenv('DATETIME_FORMAT', '%d %b, %Y'))
    time_format: str = field(default_factory=lambda: os.getenv('TIME_FORMAT', '%I:%M:%S %p'))

    # Application metadata
    version: str = "1.8.1"
    name: str = "socials.io"

    # Feature flags
    enable_dry_run: bool = True
    enable_debug_logging: bool = field(default_factory=lambda: bool(int(os.getenv('DEBUG', '0'))))

    # Performance settings
    max_workers: int = field(default_factory=lambda: int(os.getenv('MAX_WORKERS', '4')))
    worker_timeout: int = field(default_factory=lambda: int(os.getenv('WORKER_TIMEOUT', '300')))


@dataclass
class APIConfig:
    """Configuration for external API integrations."""

    # Together AI (for content generation)
    together_api_key: Optional[str] = field(default_factory=lambda: os.getenv('TOGETHER_API_KEY'))
    together_base_url: str = "https://api.together.ai/v1"
    together_model: str = field(default_factory=lambda: os.getenv('TOGETHER_MODEL', 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'))

    # Instagram API (currently not using official API - just credential storage)
    instagram_username: Optional[str] = field(default_factory=lambda: os.getenv('INSTAGRAM_USERNAME'))
    instagram_password: Optional[str] = field(default_factory=lambda: os.getenv('INSTAGRAM_PASSWORD'))
    instagram_file_id: Optional[str] = field(default_factory=lambda: os.getenv('INSTAGRAM_DRIVE_FILE_ID'))

    # Google API credentials
    google_credentials: Optional[str] = field(default_factory=lambda: os.getenv('GCP_CREDENTIALS'))
    google_sheets_key: Optional[str] = field(default_factory=lambda: os.getenv('CRYPTO_SPREADSHEET_KEY'))

    # OpenRouter API (optional fallback)
    openrouter_api_key: Optional[str] = field(default_factory=lambda: os.getenv('OPENROUTER_API_KEY'))

    def validate(self) -> None:
        """Validate API configuration."""
        if self.together_api_key and not str(self.together_api_key).startswith('sk-'):
            raise ValueError("Invalid Together API key format")
        if self.instagram_username and not self.instagram_password:
            raise ValueError("Instagram password required when username is provided")


@dataclass
class LoggingConfig:
    """Configuration for application logging."""

    level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO').upper())
    format: str = field(default_factory=lambda: os.getenv('LOG_FORMAT', 'json'))
    file_path: Optional[Path] = None
    max_file_size: int = field(default_factory=lambda: int(os.getenv('LOG_MAX_SIZE', '10485760')))  # 10MB
    retention_days: int = field(default_factory=lambda: int(os.getenv('LOG_RETENTION', '30')))

    def __post_init__(self):
        """Initialize computed paths."""
        if os.getenv('LOG_FILE'):
            self.file_path = Path(os.getenv('LOG_FILE'))

    def validate(self) -> None:
        """Validate logging configuration."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.level not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}. Must be one of {valid_levels}")


@dataclass
class Config:
    """Main configuration class aggregating all settings."""

    # Core components
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    app: AppConfig = field(default_factory=AppConfig)
    image: ImageConfig = field(default_factory=ImageConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def validate_all(self) -> None:
        """Validate all configuration components."""
        self.database.validate()
        self.image.validate()
        self.api.validate()
        self.logging.validate()
        print("✓ All configuration validated successfully")


# Global configuration instance
config = Config()  # Can be imported directly


def load_config() -> Config:
    """Load and validate configuration from environment."""
    try:
        global config
        config = Config()
        config.validate_all()
        return config
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        raise


# Legacy compatibility functions (import from old config.paths)
TEMPLATES_DIR = config.paths.templates_dir
HTML_OUTPUT_DIR = config.paths.html_output_dir
IMAGES_OUTPUT_DIR = config.paths.images_output_dir

def get_html_output_path(filename: str) -> Path:
    """Legacy compatibility for templates with extension."""
    # Extract template number from filename (e.g., "1_output.html")
    if "_output.html" not in filename:
        raise ValueError(f"Invalid output filename format: {filename}")
    template_num = int(filename.split("_")[0])
    return config.paths.get_html_output_path(template_num)

def get_image_output_path(filename: str) -> Path:
    """Legacy compatibility for images with extension."""
    if "_output.jpg" not in filename:
        raise ValueError(f"Invalid output filename format: {filename}")
    template_num = int(filename.split("_")[0])
    return config.paths.get_image_output_path(template_num)

def ensure_directories():
    """Legacy compatibility."""
    config.paths.ensure_directories()