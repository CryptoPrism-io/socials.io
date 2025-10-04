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

### Local Development Server
```bash
# Generate content and serve HTML outputs locally on port 8080
# Step 1: Generate all available templates
python scripts/main/individual_posts/generate_1_output.py
python scripts/main/individual_posts/generate_2_output.py
python scripts/main/individual_posts/generate_3_1_output.py
python scripts/main/individual_posts/generate_3_2_output.py
python scripts/main/individual_posts/generate_4_output.py
python scripts/main/individual_posts/generate_5_output.py
python scripts/main/individual_posts/generate_6_output.py
python scripts/main/individual_posts/generate_7_output.py

# Step 2: Start local server (serves only HTML outputs from output_html/ directory)
python scripts/dev/local_server.py

# Accessible at: http://127.0.0.1:8080/
# Direct links:
# - Template 1: http://127.0.0.1:8080/1_output.html
# - Template 2: http://127.0.0.1:8080/2_output.html
# - Template 3.1: http://127.0.0.1:8080/3_1_output.html (Top Gainers >2%)
# - Template 3.2: http://127.0.0.1:8080/3_2_output.html (Top Losers <-2%)
# - Template 4: http://127.0.0.1:8080/4_output.html
# - Template 5: http://127.0.0.1:8080/5_output.html
# - Template 6: http://127.0.0.1:8080/6_output.html
# - Template 7: http://127.0.0.1:8080/7_output.html
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

#### Legacy Scripts (Monolithic)
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

#### New Modular Scripts (Recommended)
```bash
# Generate Instagram content using modular architecture
python scripts/main/instapost_new.py

# Publish generated content using modular architecture
python scripts/main/instapost_push_new.py

# Complete workflow: generation + publishing
python scripts/main/workflows/complete_workflow.py

# Individual workflow components
python scripts/main/workflows/instagram_pipeline.py
python scripts/main/workflows/publishing_workflow.py

# Migrated integrations
python scripts/main/data/gsheets_sync.py
python scripts/main/integrations/figma_api.py
```

#### Individual Post Generators (Templates 1-7)
```bash
# Generate specific templates individually with HTML + screenshot
cd scripts/main/individual_posts

# Template 1: Top Cryptocurrencies (ranks 2-24)
python generate_1_output.py

# Template 2: Extended Cryptocurrencies (ranks 25-48)
python generate_2_output.py

# Template 3.1: Top Gainers (+2% or more)
python generate_3_1_output.py

# Template 3.2: Top Losers (-2% or more)
python generate_3_2_output.py

# Template 4: Trading Opportunities
python generate_4_output.py

# Template 5: Market Overview
python generate_5_output.py

# Template 6: Bitcoin + Macro Intelligence
python generate_6_output.py

# Template 7: Market Intelligence (L2 AI Filtered)
python generate_7_output.py
```

## Architecture Overview

### Simplified Directory Structure

The project uses a clean, simplified directory structure for easy navigation and maintenance:

```
├── scripts/             # ALL Python scripts (organized by function)
│   ├── main/           # Core application scripts
│   │   ├── individual_posts/  # Individual template generators (1-7)
│   │   ├── workflows/         # Pipeline orchestration
│   │   ├── content/           # AI generation & templating
│   │   ├── data/              # Database operations
│   │   ├── media/             # Screenshot generation
│   │   ├── publishing/        # Instagram posting
│   │   └── integrations/      # External APIs
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
├── archive/             # Archived files and deprecated content
│   ├── research_docs/   # Research documents and analysis
│   ├── test_artifacts/  # Coverage reports and test cache
│   ├── old_templates/   # Deprecated template directories
│   ├── strategy_docs/   # Planning and strategy documents
│   └── old_structure/   # Previous project structure
└── .github/workflows/   # GitHub Actions automation
```

### Scripts Organization

The `scripts/` directory is organized into logical sub-folders for better maintainability:

- **`main/`** - Core application functionality:
  - **Legacy Scripts (Monolithic)**:
    - `instapost.py` - Main content generation pipeline
    - `instapost_push.py` - Instagram publishing
    - `gsheets.py` - Google Sheets synchronization
    - `figma.py` - Figma integration workflow
  - **New Modular Scripts**:
    - `instapost_new.py` - Modular content generation entry point
    - `instapost_push_new.py` - Modular publishing entry point
  - **Modular Components**:
    - `content/` - Content creation and AI generation
      - `ai_generation.py` - AI content & caption generation
      - `template_engine.py` - Jinja2 template rendering
    - `publishing/` - Social media publishing
      - `instagram.py` - Instagram API & posting logic
    - `data/` - Data management & sync
      - `database.py` - PostgreSQL operations
      - `gsheets_sync.py` - Google Sheets synchronization (migrated)
    - `media/` - Media processing & generation
      - `screenshot.py` - Playwright HTML-to-image conversion
    - `integrations/` - External service APIs
      - `figma_api.py` - Figma design workflow (migrated)
      - `google_services.py` - Google Drive/Sheets APIs
    - `workflows/` - Complete pipeline orchestration
      - `instagram_pipeline.py` - Full Instagram content workflow
      - `publishing_workflow.py` - Complete publishing workflow
      - `complete_workflow.py` - End-to-end generation + publishing
    - `individual_posts/` - Standalone template generators
      - `generate_1_output.py` - Template 1: Top Cryptocurrencies
      - `generate_2_output.py` - Template 2: Extended Cryptocurrencies
      - `generate_3_output.py` - Template 3: Top Gainers and Losers
      - `generate_4_output.py` - Template 4: Trading Opportunities
      - `generate_5_output.py` - Template 5: Market Overview
      - `generate_6_output.py` - Template 6: Bitcoin + Macro Intelligence
      - `generate_7_output.py` - Template 7: Market Intelligence (L2 AI)
      - `README.md` - Complete documentation and usage examples

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

#### Main Scripts (`scripts/main/`)

**Legacy Monolithic Scripts:**
- **`instapost.py`**: Main content generation pipeline with HTML-to-image conversion
- **`instapost_push.py`**: Enhanced content publishing with error handling and retry logic
- **`gsheets.py`**: PostgreSQL to Google Sheets data synchronization
- **`figma.py`**: Figma-based design workflow integration

**New Modular Architecture:**
- **`workflows/complete_workflow.py`**: Complete end-to-end Instagram automation
- **`workflows/instagram_pipeline.py`**: Content generation pipeline orchestration
- **`workflows/publishing_workflow.py`**: Publishing pipeline with AI caption generation
- **`data/database.py`**: PostgreSQL operations and data fetching
- **`content/template_engine.py`**: Jinja2 template rendering system
- **`content/ai_generation.py`**: AI-powered content and caption generation
- **`media/screenshot.py`**: Playwright HTML-to-image conversion
- **`publishing/instagram.py`**: Instagram API integration with session management
- **`integrations/google_services.py`**: Google Drive/Sheets API operations

#### Output Structure (Simplified)
- **`output_html/`**: Generated HTML files with live data (`*_output.html`)
- **`output_images/`**: Final Instagram posts in JPG format for publishing
- **`input_images/`**: Background images and input media files

### Technology Stack
- **Web Automation**: Playwright (async) for HTML screenshot generation
- **AI Content**: OpenRouter API for intelligent content and caption generation
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

### Modular Architecture Benefits

The new modular architecture provides several advantages for future development:

#### **Separation of Concerns**
- **Database Operations**: Isolated in `data/` module for easy testing and modification
- **Content Generation**: AI and template logic separated in `content/` module
- **Media Processing**: Screenshot generation isolated in `media/` module
- **Publishing**: Instagram API operations contained in `publishing/` module
- **Integrations**: External services (Google, Figma) in `integrations/` module
- **Workflows**: High-level orchestration in `workflows/` module

#### **Development Workflow**
```bash
# For content generation only
python scripts/main/workflows/instagram_pipeline.py

# For publishing only (requires existing images)
python scripts/main/workflows/publishing_workflow.py

# For complete automation
python scripts/main/workflows/complete_workflow.py

# For individual component testing
python scripts/main/data/database.py
python scripts/main/content/ai_generation.py
```

#### **Scalability & Maintenance**
- **Independent Testing**: Each module can be tested in isolation
- **Easy Extension**: New features can be added to specific modules
- **Reduced Complexity**: Smaller, focused files are easier to understand
- **Reusability**: Components can be reused across different workflows
- **Better Error Handling**: Issues can be isolated to specific modules

#### **Migration Strategy**
- Legacy scripts (`instapost.py`, `instapost_push.py`) remain functional
- New modular scripts (`instapost_new.py`, `instapost_push_new.py`) use new architecture
- Gradual migration: teams can migrate workflows incrementally
- Complete workflow available for end-to-end automation

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
- `OPENROUTER_API_KEY`: OpenRouter API key for AI content generation (replaces Together AI)
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