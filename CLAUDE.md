# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a social media automation system called "socials.io" focused on automating customer acquisition through automated social media content creation and posting. The system primarily generates Instagram posts from data sources and uses various APIs for content creation and social media posting.

## Key Commands

### Running Scripts Locally
```bash
# Main Instagram post generation and publishing
python instapost.py

# Push additional Instagram content
python instapost_push.py

# Generate Figma-based content
python figma.py

# Update Google Sheets data
python gsheets.py
```

### GitHub Actions Workflows
The project uses three automated workflows:

- **Instagram Story Workflow** (`Instagram_Story.yml`): Runs daily at 00:30 UTC, executes both `instapost.py` and `instapost_push.py`
- **Google Sheets Update** (`gsheets.yml`): Runs daily at 00:30 UTC, executes `gsheets.py`
- **Figma Content Generation** (`figma.yml`): Manual trigger only, executes `figma.py`

### Dependencies Installation
```bash
# For Instagram posting workflow
pip install together psycopg2 nest_asyncio requests pandas gspread oauth2client google-api-python-client google-auth-httplib2 google-auth-oauthlib instagrapi playwright python-dotenv pillow sqlalchemy jinja2

# For Google Sheets workflow
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas numpy matplotlib seaborn mysql-connector-python sqlalchemy requests psycopg2-binary gspread oauth2client gspread-dataframe

# For Figma workflow
pip install requests pandas gspread oauth2client google-api-python-client google-auth-httplib2 google-auth-oauthlib together Pillow instagrapi

# Install Playwright browsers (required for screenshot generation)
playwright install chromium && playwright install firefox && playwright install webkit
```

## Architecture Overview

### Core Components

1. **Content Generation Pipeline**:
   - `instapost.py`: Main Instagram content generator using Playwright for HTML-to-image conversion
   - `instapost_push.py`: Secondary content publisher with enhanced error handling
   - `figma.py`: Figma-based content integration
   - `gsheets.py`: Google Sheets data synchronization

2. **HTML Templates & Styling**:
   - Template files: `1.html` through `5.html` (base templates)
   - Generated output: `1_output.html` through `5_output.html` (rendered with data)
   - Corresponding CSS: `style.css` through `style5.css`
   - Image outputs: `*.png` and `*.jpg` files generated from HTML templates

3. **Data Sources**:
   - PostgreSQL database (GCP-hosted at 34.55.195.199)
   - Google Sheets integration via gspread
   - Google Drive API for file management

### Technology Stack

- **Web Automation**: Playwright (async) for HTML screenshot generation
- **Instagram API**: instagrapi for posting content
- **AI Content**: Together AI API for content generation
- **Template Engine**: Jinja2 for HTML template rendering
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Google Services**: gspread, Google Drive API, Google Sheets API
- **Image Processing**: Pillow (PIL)

### Environment Variables Required

All scripts require these environment variables:
- `GCP_CREDENTIALS`: Google Cloud Platform service account JSON
- `TOGETHER_API_KEY`: Together AI API key
- `INSTAGRAM_DRIVE_FILE_ID`: Google Drive file ID for Instagram content
- `CRYPTO_SPREADSHEET_KEY`: Google Sheets key for crypto data
- `INSTAGRAM_USERNAME`: Instagram account username
- `INSTAGRAM_PASSWORD`: Instagram account password

### Data Flow

1. `gsheets.py` pulls data from PostgreSQL database and updates Google Sheets
2. `instapost.py` reads data from Google Sheets, generates HTML content using Jinja2 templates, converts to images via Playwright, and posts to Instagram
3. `instapost_push.py` performs additional content publishing with refined workflows
4. `figma.py` integrates Figma-based design workflows

### File Structure

- **Scripts**: `*.py` files in root directory
- **Templates**: `1.html` - `5.html` (base templates), `*_output.html` (rendered)
- **Styles**: `style*.css` files
- **Generated Images**: `*.png` and `*.jpg` files
- **Config**: `.github/workflows/` for GitHub Actions automation