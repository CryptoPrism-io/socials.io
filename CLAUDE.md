# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install Playwright browsers for screenshot generation
playwright install chromium
playwright install firefox
playwright install webkit

# Windows UTF-8 setup (if needed)
scripts/setup/setup_windows_utf8.bat
```

### Testing
```bash
# Run structure validation tests
python tests/test_path_structure.py

# Run full test suite
python -m pytest tests/ -v --tb=short

# Environment validation
python scripts/dev/validate_env.py
python scripts/dev/validate_project.py
```

### Code Quality
```bash
# Linting
flake8 scripts/
pylint scripts/

# Code formatting
black scripts/
isort scripts/

# Security scanning
bandit -r scripts/

# Type checking
mypy scripts/
```

### Main Application Scripts
```bash
# Generate Instagram content from database
python scripts/main/instapost.py

# Publish generated content to Instagram
python scripts/main/instapost_push.py

# Sync PostgreSQL data to Google Sheets
python scripts/main/gsheets.py

# Figma integration workflow
python scripts/main/figma.py
```

## Architecture Overview

### Simplified Directory Structure

The project uses a clean, simplified directory structure for easy navigation and maintenance:

```
├── scripts/             # ALL Python scripts (organized by function)
│   ├── main/           # Core application scripts
│   ├── auth/           # Authentication scripts
│   ├── dev/            # Development & testing tools
│   ├── setup/          # System setup & utilities
│   └── config/         # Configuration & documentation
├── base_templates/      # ALL base HTML and CSS files
├── output_html/         # Generated HTML outputs + their CSS
├── output_images/       # Generated/screenshot images (.jpg)
├── input_images/        # Imported/input images (.png backgrounds)
├── tests/               # Testing infrastructure
├── docs/                # Documentation
└── .github/workflows/   # GitHub Actions automation
```

### Scripts Organization

The `scripts/` directory is organized into logical sub-folders for better maintainability:

- **`main/`** - Core application functionality:
  - `instapost.py` - Main content generation pipeline
  - `instapost_push.py` - Instagram publishing
  - `gsheets.py` - Google Sheets synchronization
  - `figma.py` - Figma integration workflow

- **`auth/`** - Authentication modules:
  - `linkedin_auth.py` - LinkedIn authentication
  - `twitter_auth.py` - Twitter authentication

- **`dev/`** - Development and testing tools:
  - `local_server.py` - Local development server
  - `validate_env.py` - Environment validation
  - `validate_project.py` - Project structure validation
  - `test_unicode_system.py` - Unicode testing

- **`setup/`** - System configuration utilities:
  - `utf8_fix.py` - UTF-8 encoding fixes
  - `setup_windows_utf8.bat` - Windows UTF-8 setup
  - `setup_powershell_utf8.ps1` - PowerShell UTF-8 setup

- **`config/`** - Configuration files and documentation:
  - `.env.template` - Environment template
  - Unicode troubleshooting documentation

### Core Pipeline
Socials.io is a **social media automation platform** that follows a multi-stage data pipeline:

1. **Data Sources** → PostgreSQL database, Google Sheets, Google Drive
2. **Content Generation** → AI-powered content creation using Together AI API
3. **Template Rendering** → HTML/CSS templates with Jinja2 dynamic data injection
4. **Image Generation** → Playwright browser automation for HTML-to-image screenshots
5. **Publishing** → Instagram API integration via instagrapi

### Key Components

#### Template System (`base_templates/`)
- **HTML Templates**: `1.html` through `6.html` - Base templates with auto-layout architecture
- **CSS Stylesheets**: `style1.css` through `style6.css` - Flexbox-based layouts with glassmorphism effects
- **Jinja2 Integration**: Dynamic data injection with proper path resolution
- **Instagram Format**: Optimized for 1080x1080 square screenshots

#### Main Scripts (`scripts/`)
- **`instapost.py`**: Main content generation pipeline with HTML-to-image conversion
- **`instapost_push.py`**: Enhanced content publishing with error handling and retry logic
- **`gsheets.py`**: PostgreSQL to Google Sheets data synchronization
- **`figma.py`**: Figma-based design workflow integration

#### Output Structure (Simplified)
- **`output_html/`**: Generated HTML files with live data (`*_output.html`)
- **`output_images/`**: Final Instagram posts in JPG format for publishing
- **`input_images/`**: Background images and input media files

### Technology Stack
- **Web Automation**: Playwright (async) for HTML screenshot generation
- **AI Content**: Together AI API for intelligent content and caption generation
- **Instagram API**: instagrapi for automated posting and publishing
- **Template Engine**: Jinja2 for dynamic HTML content rendering
- **Database**: PostgreSQL + SQLAlchemy for data storage and management
- **Google Services**: gspread, Google Drive/Sheets API for cloud data integration

### Automated Workflows (GitHub Actions)
- **Instagram Content Pipeline** (`.github/workflows/Instagram_Story.yml`): Daily at 00:31 UTC
  - Runs structure validation tests
  - Executes `instapost.py` → `instapost_push.py` sequence
  - Environment: Python 3.11, Ubuntu latest, Playwright Chromium
- **Google Sheets Sync** (`.github/workflows/gsheets.yml`): Daily data synchronization
- **Figma Integration** (`.github/workflows/figma.yml`): Manual trigger workflow

## Development Guidelines

### Template Development
- Templates use auto-layout container systems (no absolute positioning)
- All templates must be Instagram-compatible (1080x1080 aspect ratio)
- Use Poppins font family for brand consistency
- Jinja2 variables for dynamic content injection
- CSS uses flexbox layouts with glassmorphism design effects

### Screenshot Generation
- Playwright generates high-quality screenshots at 2160x2700 viewport
- Images are saved as JPEG with 95% quality for Instagram optimization
- Browser automation includes proper viewport scaling and media emulation

### Database Integration
- PostgreSQL connection via SQLAlchemy engine
- Database credentials configured in environment variables
- Data flows: PostgreSQL → Python processing → Jinja2 rendering → HTML → Screenshot

### Environment Configuration
Required environment variables:
- `GCP_CREDENTIALS`: Google Cloud Platform service account JSON
- `TOGETHER_API_KEY`: Together AI API key for content generation
- `INSTAGRAM_USERNAME/PASSWORD`: Instagram account credentials
- `INSTAGRAM_DRIVE_FILE_ID`: Google Drive file ID for content storage
- `CRYPTO_SPREADSHEET_KEY`: Google Sheets key for data source

### Code Patterns
- Async/await pattern for Playwright browser automation
- SQLAlchemy engine initialization with connection pooling
- Jinja2 Environment with FileSystemLoader for template rendering
- Error handling with comprehensive retry logic in publishing workflows

## Important Notes

- Never commit sensitive credentials to repository
- All file paths use absolute path resolution for cross-platform compatibility
- Windows UTF-8 encoding issues are handled by setup scripts in `scripts/`
- Template customization requires updating both HTML and corresponding CSS files
- Instagram posting respects API rate limits and account restrictions