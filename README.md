# Socials.io: Automated Social Media Content Generation & Publishing System

**Version 2.4.0** - Intelligent social media automation platform that transforms cryptocurrency data into engaging Instagram content through automated 3-carousel posting, AI-powered content generation, and smart session management.

---

## 🔍 WHAT - System Overview

### Architecture
Socials.io operates on a **multi-source data pipeline** designed for automated content creation:

- **Data Sources** - PostgreSQL database, Google Sheets, and Google Drive integration
- **Content Generation** - AI-powered content creation using OpenRouter API (GPT-4o-mini, Claude, Llama)
- **Template System** - 10 specialized HTML/CSS templates with Jinja2 rendering
- **Image Generation** - Playwright-based HTML-to-image conversion
- **Publishing Platform** - Instagram 3-carousel automation via instagrapi
- **Session Management** - Smart Instagram session persistence (30-day lifecycle, rate-limiting protection)

### Core System Components

#### 🤖 **Automated 3-Carousel Posting** (v2.4.0)
- **Daily Instagram Automation** - 3 distinct carousels posted daily at 02:00 UTC
- **Carousel 1**: Bitcoin Intelligence + Top Cryptos (Templates 6, 1, 2)
- **Carousel 2**: Market Movers (Templates 3.1 Gainers, 3.2 Losers)
- **Carousel 3**: Trading Opportunities (Templates 4.1 Long, 4.2 Short)
- **AI Captions**: Generated via OpenRouter API for each carousel

#### 📊 **Individual Template Generators** (Primary System)
- **`scripts/main/individual_posts/`** - 9 standalone template generators
  - `generate_1_output.py` - Top Cryptocurrencies (ranks 2-24)
  - `generate_2_output.py` - Extended Cryptocurrencies (ranks 25-48)
  - `generate_3_1_output.py` - Top Gainers (+2% or more)
  - `generate_3_2_output.py` - Top Losers (-2% or more)
  - `generate_4_1_output.py` - Long Call Positions
  - `generate_4_2_output.py` - Short Call Positions
  - `generate_5_output.py` - Market Overview
  - `generate_6_output.py` - Bitcoin + Macro Intelligence
  - `generate_7_output.py` - Market Intelligence (L2 AI Filtered)

#### 🔐 **Session Management & Authentication**
- **`scripts/auth/create_instagram_session.py`** - Create persistent Instagram session
- **`scripts/main/publishing/session_manager.py`** - Smart session lifecycle management
- **30-day session persistence** - Reduces login frequency
- **Rate-limiting protection** - 7-day minimum between fresh logins
- **Instagram-compliant** - Prevents account security issues

#### 🎨 **Legacy Monolithic Scripts** (Still Functional)
- **`scripts/main/instapost.py`** - Legacy content generation (use individual generators)
- **`scripts/main/instapost_push.py`** - Legacy publishing (use modular workflows)
- **`scripts/main/gsheets.py`** - PostgreSQL to Google Sheets synchronization
- **`scripts/main/figma.py`** - Figma-based design workflow integration

### Template System - 10 Specialized Variations
- **Base Templates**: `base_templates/` directory contains:
  - **HTML Templates**: 11 files (1.html, 2.html, 3.html, 3_1.html, 3_2.html, 4.html, 4_1.html, 4_2.html, 5.html, 6.html, 7.html)
  - **CSS Stylesheets**: Dedicated style1.css through style7.css with glassmorphism effects
  - **Modern Architecture**: Auto-layout flexbox systems (no absolute positioning)
  - **Instagram-Optimized**: 1080x1080 format with 2160x2700 viewport for screenshot generation

- **Template Specializations**:
  1. **Template 1**: Top Cryptocurrencies (ranks 2-24) - Coin grid layout
  2. **Template 2**: Extended Cryptocurrencies (ranks 25-48)
  3. **Template 3.1**: Top Gainers (+2% or more) - Performance highlights
  4. **Template 3.2**: Top Losers (-2% or more) - Performance highlights
  5. **Template 4.1**: Long Call Positions - Bullish opportunities
  6. **Template 4.2**: Short Call Positions - Bearish opportunities
  7. **Template 5**: Market Overview - Global metrics
  8. **Template 6**: Bitcoin + Macro Intelligence - Fear & Greed Index + BTC Price dual-axis chart
  9. **Template 7**: Market Intelligence - L2 AI filtering system with web search

- **Generated Content**: Output structure:
  - **HTML Output**: `output_html/` - Rendered templates with live data + CSS files
  - **Image Output**: `output_images/` - Final Instagram posts (JPG format at 95% quality)
  - **Input Assets**: `input_images/` - Background images and input media files

- **Dynamic Rendering**: Jinja2-powered data injection with proper path resolution
- **Screenshot Generation**: Playwright async browser automation (1-10 seconds per template)

## 📁 Project Structure

```
socials.io/
├── 📁 scripts/                          # ALL Python scripts (organized by function)
│   ├── 📁 main/                         # Core application scripts
│   │   ├── 📁 individual_posts/         # Individual template generators (PRIMARY)
│   │   │   ├── 📄 generate_1_output.py  # Top Cryptocurrencies (ranks 2-24)
│   │   │   ├── 📄 generate_2_output.py  # Extended Cryptocurrencies (ranks 25-48)
│   │   │   ├── 📄 generate_3_1_output.py # Top Gainers (+2%)
│   │   │   ├── 📄 generate_3_2_output.py # Top Losers (-2%)
│   │   │   ├── 📄 generate_4_1_output.py # Long Call Positions
│   │   │   ├── 📄 generate_4_2_output.py # Short Call Positions
│   │   │   ├── 📄 generate_5_output.py  # Market Overview
│   │   │   ├── 📄 generate_6_output.py  # Bitcoin + Macro Intelligence
│   │   │   ├── 📄 generate_7_output.py  # Market Intelligence (L2 AI)
│   │   │   └── 📄 README.md             # Complete generator documentation
│   │   ├── 📁 workflows/                # Pipeline orchestration
│   │   │   ├── 📄 complete_workflow.py
│   │   │   ├── 📄 instagram_pipeline.py
│   │   │   └── 📄 publishing_workflow.py
│   │   ├── 📁 content/                  # AI generation & templating
│   │   │   ├── 📄 ai_generation_captions.py
│   │   │   ├── 📄 ai_generation_news.py
│   │   │   ├── 📄 openrouter_client.py
│   │   │   └── 📄 template_engine.py
│   │   ├── 📁 data/                     # Database operations
│   │   │   ├── 📄 database.py
│   │   │   └── 📄 gsheets_sync.py
│   │   ├── 📁 media/                    # Screenshot generation
│   │   │   └── 📄 screenshot.py
│   │   ├── 📁 publishing/               # Instagram posting
│   │   │   ├── 📄 instagram.py
│   │   │   ├── 📄 session_manager.py    # Smart session management
│   │   │   ├── 📄 post_carousel.py
│   │   │   └── 📄 post_3_carousels.py   # 3-carousel automation
│   │   ├── 📁 integrations/             # External APIs
│   │   │   ├── 📄 google_services.py
│   │   │   └── 📄 figma_api.py
│   │   ├── 📄 instapost.py              # Legacy monolithic generator
│   │   ├── 📄 instapost_push.py         # Legacy monolithic publisher
│   │   ├── 📄 gsheets.py                # Google Sheets sync
│   │   └── 📄 figma.py                  # Figma integration
│   ├── 📁 auth/                         # Authentication scripts
│   │   ├── 📄 create_instagram_session.py
│   │   ├── 📄 instagram_session_status.py
│   │   ├── 📄 instapost_push_local.py
│   │   ├── 📄 linkedin_auth.py
│   │   └── 📄 twitter_auth.py
│   ├── 📁 dev/                          # Development & testing tools
│   │   ├── 📄 local_server.py           # Local dev server (port 8080)
│   │   ├── 📄 validate_env.py
│   │   ├── 📄 validate_project.py
│   │   └── 📄 test_unicode_system.py
│   ├── 📁 setup/                        # System setup & utilities
│   │   ├── 📄 setup_windows_utf8.bat
│   │   ├── 📄 setup_powershell_utf8.ps1
│   │   └── 📄 utf8_fix.py
│   └── 📁 config/                       # Configuration & documentation
│       ├── 📄 UNICODE_PERMANENT_FIX.md
│       ├── 📄 UNICODE_TROUBLESHOOTING.md
│       └── 📄 UTF8_FIX_SUMMARY.md
├── 📁 base_templates/                   # ALL base HTML and CSS files
│   ├── 📄 1.html, 2.html, 3.html, 3_1.html, 3_2.html
│   ├── 📄 4.html, 4_1.html, 4_2.html, 5.html, 6.html, 7.html
│   └── 📄 style1.css → style7.css       # Dedicated stylesheets
├── 📁 output_html/                      # Generated HTML outputs + CSS
│   ├── 📄 *_output.html                 # Rendered templates with live data
│   └── 📄 style*.css                    # CSS files for outputs
├── 📁 output_images/                    # Generated/screenshot images (.jpg)
│   └── 📄 *_output.jpg                  # Final Instagram posts
├── 📁 input_images/                     # Imported/input images (.png)
│   └── 📄 *.png                         # Background images and assets
├── 📁 data/                             # Data files & sessions
│   └── 📄 instagram_session.json        # Instagram session file
├── 📁 sessions/                         # Session backups
│   └── 📄 instagram_session.json        # Session backup
├── 📁 tests/                            # Testing infrastructure
│   └── 📄 test_path_structure.py        # Path validation tests
├── 📁 docs/                             # Documentation
│   ├── 📄 DEPLOYMENT_SUMMARY.md
│   └── 📄 instagram_session_management.md
├── 📁 archive/                          # Archived files and deprecated content
│   ├── 📁 research_docs/
│   ├── 📁 test_artifacts/
│   └── 📁 old_structure/
├── 📁 .github/workflows/                # GitHub Actions automation
│   ├── 📄 Instagram_3_Carousels.yml     # 3-carousel daily (02:00 UTC)
│   ├── 📄 Instagram_Story.yml           # Legacy single carousel (00:31 UTC)
│   ├── 📄 gsheets.yml                   # Google Sheets sync (00:31 UTC)
│   ├── 📄 figma.yml                     # Manual trigger
│   └── 📄 ci-cd.yml                     # CI/CD pipeline
├── 📄 .env                              # Environment variables (DO NOT COMMIT)
├── 📄 .env.template                     # Environment template
├── 📄 requirements.txt                  # Core dependencies
├── 📄 requirements-dev.txt              # Development dependencies
├── 📄 README.md                         # Project documentation (this file)
├── 📄 CHANGELOG.md                      # Version history
├── 📄 CLAUDE.md                         # AI assistant guidance
├── 📄 TODO.md                           # Production hardening tasks
└── 📄 .gitignore                        # Git ignore rules
```

### 📂 Directory Purposes

| Directory | Purpose | Contains |
|-----------|---------|----------|
| **`scripts/main/individual_posts/`** | Template generators | 9 standalone generators for each template variation |
| **`scripts/main/workflows/`** | Pipeline orchestration | Complete workflow scripts for generation + publishing |
| **`scripts/main/content/`** | Content creation | AI generation, template rendering, OpenRouter client |
| **`scripts/main/publishing/`** | Instagram posting | Session manager, carousel posting, Instagram API |
| **`scripts/auth/`** | Authentication | Instagram session creation and status monitoring |
| **`scripts/dev/`** | Development tools | Local server, validation scripts, testing utilities |
| **`base_templates/`** | Template system | 11 HTML files + 7 CSS stylesheets (10 template variations) |
| **`output_html/`** | Generated HTML | Rendered templates with live cryptocurrency data |
| **`output_images/`** | Generated images | Final JPG Instagram posts for publishing |
| **`data/` & `sessions/`** | Session storage | Instagram session JSON files (30-day lifecycle) |
| **`tests/`** | Testing suite | Structure validation, path tests |
| **`docs/`** | Documentation | Deployment guides, session management docs |
| **`.github/workflows/`** | Automation | Daily 3-carousel posting, Google Sheets sync |
| **`archive/`** | Deprecated content | Old templates, research docs, test artifacts |

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Automation** | Playwright (async) | HTML screenshot generation (Chromium, Firefox, WebKit) |
| **AI Content** | OpenRouter API | GPT-4o-mini, Claude Haiku, Llama-3.3 for captions & news |
| **Instagram API** | instagrapi ~2.1 | Automated carousel posting and publishing |
| **Session Management** | Custom SessionManager | 30-day persistence, 7-day rate-limiting protection |
| **Template Engine** | Jinja2 ~3.1 | Dynamic HTML content rendering |
| **Database** | PostgreSQL + SQLAlchemy ~2.0 | Data storage and management |
| **Google Services** | gspread, Google Drive/Sheets API | Cloud data integration |
| **Image Processing** | Pillow ~10.1 | Image optimization and processing |

### 🔄 Automated Publishing Pipeline

#### **GitHub Actions Automation**
Socials.io features a **4-workflow automated system** that runs daily:

```
DATA SYNC → TEMPLATE GENERATION → 3-CAROUSEL POSTING
```

#### **Workflow 1: Instagram 3-Carousel Daily Post** (Daily 02:00 UTC) ⭐ PRIMARY
- **File**: `.github/workflows/Instagram_3_Carousels.yml`
- **Purpose**: Automated 3-carousel Instagram posting system
- **Process**:
  1. Generate 7 templates (1, 2, 3.1, 3.2, 4.1, 4.2, 6)
  2. Post 3 separate carousels with 5-minute delays:
     - **Carousel 1**: Templates 6, 1, 2 (Bitcoin Intelligence + Top Cryptos)
     - **Carousel 2**: Templates 3.1, 3.2 (Top Gainers & Losers)
     - **Carousel 3**: Templates 4.1, 4.2 (Long/Short Call Positions)
  3. AI-generated captions via OpenRouter API (GPT-4o-mini)
- **Technology**: Python 3.11, Playwright Chromium, OpenRouter API
- **Session**: Uses persistent session from `data/instagram_session.json`

#### **Workflow 2: Google Sheets Sync** (Daily 00:31 UTC)
- **File**: `.github/workflows/gsheets.yml`
- **Purpose**: Synchronize PostgreSQL data with Google Sheets
- **Module**: `scripts/main/gsheets.py`
- **Output**: Updated spreadsheets with latest cryptocurrency data

#### **Workflow 3: Instagram Single Carousel** (Daily 00:31 UTC) - LEGACY
- **File**: `.github/workflows/Instagram_Story.yml`
- **Purpose**: Legacy single carousel posting (superseded by 3-carousel system)
- **Execution Order**:
  1. `scripts/main/instapost.py` - Content generation
  2. `scripts/main/instapost_push.py` - Publishing
- **Status**: Active but consider using Workflow 1 instead

#### **Workflow 4: Figma Integration** (Manual Trigger)
- **File**: `.github/workflows/figma.yml`
- **Purpose**: Figma-based content creation workflow
- **Module**: `scripts/main/figma.py`
- **Trigger**: Manual workflow dispatch

#### **Pipeline Features**
- **Sequential Dependencies** - Data sync → Template generation → Publishing
- **Error Handling** - Comprehensive retry logic and error recovery
- **Multi-browser Support** - Chromium, Firefox, WebKit for screenshot generation
- **AI Integration** - OpenRouter API for intelligent caption generation
- **Session Management** - 30-day persistent sessions prevent login issues
- **Credential Security** - GitHub Secrets for API keys and passwords
- **Rate Limiting** - 5-minute delays between carousel posts

---

## 🎯 WHY - Business Rationale

### Social Media Automation Challenges

#### **Content Creation Complexity**
- Manual content creation is time-intensive and inconsistent
- Maintaining visual brand consistency across multiple posts
- Scaling content production for daily publishing requirements
- Integrating data insights into engaging visual content

#### **Publishing Workflow Inefficiencies**
- Manual posting processes prone to scheduling errors
- Inconsistent posting times affecting engagement rates
- Difficulty maintaining posting frequency and quality
- Complex multi-platform content adaptation requirements

#### **Data-Driven Content Needs**
- **Real-time Data Integration** - Dynamic content based on current data
- **Template Standardization** - Consistent visual branding and layouts
- **AI-Enhanced Copywriting** - Intelligent caption and content generation
- **Performance Tracking** - Automated publishing with engagement monitoring

### Competitive Advantages

#### **Automated Content Pipeline**
- **Complete Automation** - End-to-end content creation and publishing
- **Data-Driven Insights** - Real-time data integration into visual content
- **AI-Powered Content** - Intelligent content generation with Together AI
- **Professional Templates** - High-quality HTML/CSS design system

#### **Scalable Architecture**
- **Multi-Source Integration** - PostgreSQL, Google Sheets, and Google Drive
- **Browser Automation** - Playwright for reliable screenshot generation
- **Error Recovery** - Comprehensive error handling and retry mechanisms
- **Cloud-Native** - GitHub Actions for serverless automation

---

## ⚙️ HOW - Implementation Guide

### Prerequisites

#### **System Requirements**
- Python 3.11+ (3.11 recommended for GitHub Actions compatibility)
- PostgreSQL database access
- Google Cloud Platform service account
- Instagram account credentials
- OpenRouter API access

#### **External Services Setup**
```bash
# Required API Keys and Credentials
GCP_CREDENTIALS           # Google Cloud service account JSON
OPENROUTER_API_KEY       # OpenRouter API key (replaces Together AI)
INSTAGRAM_USERNAME       # Instagram account username
INSTAGRAM_PASSWORD       # Instagram account password
INSTAGRAM_DRIVE_FILE_ID  # Google Drive file ID for content storage
CRYPTO_SPREADSHEET_KEY   # Google Sheets key for data source
```

### Installation

#### **1. Clone Repository**
```bash
git clone https://github.com/your-repo/socials.io.git
cd socials.io
```

#### **2. Install Dependencies**
```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Install Playwright browsers for screenshot generation
playwright install chromium
playwright install firefox
playwright install webkit

# Windows UTF-8 setup (if needed)
scripts/setup/setup_windows_utf8.bat
```

#### **3. Environment Configuration**
Create `.env` file with required variables (use `.env.template` as reference):
```env
# Database Configuration
DB_HOST=your_postgresql_host
DB_PORT=5432
DB_NAME=dbcp
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_SSL_MODE=prefer
DB_CONNECTION_TIMEOUT=30

# Google Cloud Platform
GCP_CREDENTIALS={"type": "service_account", "project_id": "..."}
CRYPTO_SPREADSHEET_KEY=your_google_sheets_key

# AI Content Generation (OpenRouter API)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Instagram Publishing
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
INSTAGRAM_DRIVE_FILE_ID=your_google_drive_file_id

# Logging and Development
LOG_LEVEL=INFO
DEBUG=1

# Image Generation Settings
IMAGE_WIDTH=1080
IMAGE_HEIGHT=1080
IMAGE_QUALITY=95
IMAGE_FORMAT=jpg
BROWSER_TIMEOUT=60000
```

#### **4. Create Instagram Session** (CRITICAL STEP)
```bash
# Create persistent Instagram session to avoid login issues
python scripts/auth/create_instagram_session.py

# This creates data/instagram_session.json (30-day lifecycle)
# Session prevents Instagram security alerts from frequent logins
```

#### **5. Test Environment**
```bash
# Validate environment configuration
python scripts/dev/validate_env.py

# Validate project structure
python scripts/dev/validate_project.py
```

### Execution Workflows

#### **Individual Template Generation** (Recommended Approach)
```bash
# Generate individual templates
python scripts/main/individual_posts/generate_1_output.py   # Top Cryptocurrencies
python scripts/main/individual_posts/generate_6_output.py   # Bitcoin + Macro Intelligence
python scripts/main/individual_posts/generate_7_output.py   # Market Intelligence (L2 AI)

# Generate all templates for 3-carousel system
python scripts/main/individual_posts/generate_1_output.py
python scripts/main/individual_posts/generate_2_output.py
python scripts/main/individual_posts/generate_3_1_output.py
python scripts/main/individual_posts/generate_3_2_output.py
python scripts/main/individual_posts/generate_4_1_output.py
python scripts/main/individual_posts/generate_4_2_output.py
python scripts/main/individual_posts/generate_6_output.py

# Expected output:
# - HTML files: output_html/*_output.html
# - JPG images: output_images/*_output.jpg
```

#### **3-Carousel Instagram Posting** (Primary System)
```bash
# Post 3 carousels to Instagram (automated)
python scripts/main/publishing/post_3_carousels.py

# This posts:
# - Carousel 1: Templates 6, 1, 2 (Bitcoin Intelligence + Top Cryptos)
# - Carousel 2: Templates 3.1, 3.2 (Top Gainers & Losers)
# - Carousel 3: Templates 4.1, 4.2 (Long/Short Call Positions)

# Expected output: 3 Instagram carousel posts with AI-generated captions
```

#### **Session Management**
```bash
# Create new Instagram session
python scripts/auth/create_instagram_session.py

# Check session status and health
python scripts/auth/instagram_session_status.py

# Test local posting with session
python scripts/auth/instapost_push_local.py
```

#### **Local Development & Preview**
```bash
# Start local server on port 8080
python scripts/dev/local_server.py

# Access templates in browser:
# http://127.0.0.1:8080/1_output.html
# http://127.0.0.1:8080/6_output.html
# http://127.0.0.1:8080/7_output.html
```

#### **Complete Workflows** (Modular System)
```bash
# Generation only
python scripts/main/workflows/instagram_pipeline.py

# Publishing only (requires existing images)
python scripts/main/workflows/publishing_workflow.py

# End-to-end automation
python scripts/main/workflows/complete_workflow.py
```

#### **Data Synchronization**
```bash
# Sync PostgreSQL data to Google Sheets
python scripts/main/gsheets.py

# Expected output: Updated spreadsheets with latest database records
```

#### **Legacy Workflows** (Still Functional)
```bash
# Legacy content generation (use individual generators instead)
python scripts/main/instapost.py

# Legacy publishing (use modular workflows instead)
python scripts/main/instapost_push.py

# Figma integration (manual trigger)
python scripts/main/figma.py
```

### Template Customization

#### **HTML Template Structure**
```html
<!-- Example template structure -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Jinja2 template variables for dynamic content -->
    <div class="content">
        <h1>{{ heading }}</h1>
        <p>{{ description }}</p>
        <div class="data-section">
            {% for item in data_items %}
            <div class="data-item">{{ item }}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
```

#### **CSS Styling Guidelines**
- **High-Resolution Format**: 2160x2700px template containers with auto-layout flexbox architecture
- **Font System**: Poppins font family for consistency with rem-based responsive scaling
- **Auto-Layout Architecture**: Modern flexbox layouts eliminated absolute positioning dependencies
- **Responsive Design**: Viewport-optimized for screenshot generation with natural document flow
- **Brand Colors**: Customizable color schemes per template with conditional DMV score coloring
- **Glassmorphism Effects**: Enhanced visual effects with backdrop-filter and gradient overlays

### Automation Setup

#### **GitHub Actions Configuration**
```yaml
# Example workflow configuration
name: Instagram Content Pipeline

on:
  schedule:
    - cron: "30 0 * * *"  # Daily at 00:30 UTC
  workflow_dispatch: {}

jobs:
  content_generation:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install [dependencies]
        playwright install chromium

    - name: Generate content
      run: python instapost.py
      env:
        GCP_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
        TOGETHER_API_KEY: ${{ secrets.TOGETHER_API_KEY }}
        # ... other environment variables

    - name: Publish content
      run: python instapost_push.py
      env:
        # Same environment variables
```

### Usage Examples

#### **Custom Template Creation**
```python
# Example of custom template data injection
from jinja2 import Environment, FileSystemLoader

# Load template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('custom_template.html')

# Inject data
rendered_html = template.render(
    title="Daily Market Update",
    heading="Cryptocurrency Insights",
    data_items=["Bitcoin: $45,000", "Ethereum: $3,200"],
    timestamp=datetime.now().strftime("%Y-%m-%d")
)

# Save rendered template
with open('custom_output.html', 'w') as f:
    f.write(rendered_html)
```

#### **Playwright Screenshot Generation**
```python
# Example screenshot generation with custom dimensions
async def generate_custom_image(html_file, output_path, width=2160, height=2700):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_viewport_size({"width": width, "height": height})
        await page.goto(f'file://{os.path.abspath(html_file)}')
        await page.screenshot(path=output_path, full_page=True)

        await browser.close()
```

### 🔐 Instagram Session Management (CRITICAL)

#### **Why Session Management is Essential**
Instagram's security systems flag frequent username/password logins as suspicious activity, which can lead to:
- Account security alerts and lockouts
- Two-factor authentication challenges
- CAPTCHA requirements
- Temporary account restrictions

**Solution**: Socials.io uses persistent session files that last up to 30 days, dramatically reducing login frequency.

#### **How It Works**
1. **Initial Session Creation**: Run `scripts/auth/create_instagram_session.py` once
2. **Session Storage**: Saved to `data/instagram_session.json` (also backed up to `sessions/`)
3. **Session Reuse**: All publishing scripts use this session instead of username/password
4. **Rate Limiting**: 7-day minimum between fresh logins (168 hours)
5. **Automatic Refresh**: Session manager handles expiration and renewal

#### **Session Manager Features**
- **Smart Client Loading**: Automatically loads existing valid sessions
- **Bypass Validation**: Works around instagrapi ~2.1 session validation bugs
- **Health Monitoring**: Track session age, login count, last validation
- **Device UUID Preservation**: Maintains consistent device fingerprint
- **Metadata Tracking**: Created date, last updated, validation timestamps

#### **Session Management Commands**
```bash
# Create new session (do this ONCE initially)
python scripts/auth/create_instagram_session.py

# Check session health and age
python scripts/auth/instagram_session_status.py

# Test posting with current session
python scripts/auth/instapost_push_local.py
```

#### **Session File Location**
- **Primary**: `data/instagram_session.json` (used by all scripts)
- **Backup**: `sessions/instagram_session.json` (automatic backup)
- **DO NOT COMMIT**: Both locations are in `.gitignore`

#### **Session Lifecycle**
```
Day 0:  Create session → data/instagram_session.json
Day 1-29: Scripts reuse session (no login required)
Day 30: Session expires → Auto-refresh (if within rate limit)
Day 30+: If rate-limited, wait until 7 days since last fresh login
```

#### **Important Notes**
- ⚠️ **NEVER** login repeatedly with username/password
- ✅ **ALWAYS** use session manager for Instagram operations
- 🔄 Session automatically backed up to `sessions/` directory
- 🕐 Monitor session age with `instagram_session_status.py`
- 🔒 Session files contain sensitive auth tokens - never commit to git

---

### 🤖 3-Carousel Automation System (v2.4.0)

#### **System Overview**
The 3-carousel system posts **3 distinct carousels** daily to Instagram at **02:00 UTC**, each with AI-generated captions and specific content focus.

#### **Carousel Configuration**

**Carousel 1: Bitcoin Intelligence + Market Overview**
- **Templates**: 6 → 1 → 2 (3 slides)
- **Content**:
  - Slide 1: Bitcoin + Macro Intelligence (Fear & Greed Index + BTC Price)
  - Slide 2: Top Cryptocurrencies (ranks 2-24)
  - Slide 3: Extended Cryptocurrencies (ranks 25-48)
- **Caption Theme**: Professional market analysis, Bitcoin-focused
- **Target Audience**: Bitcoin investors, market analysts

**Carousel 2: Market Movers**
- **Templates**: 3.1 → 3.2 (2 slides)
- **Content**:
  - Slide 1: Top Gainers (+2% or more in 24h)
  - Slide 2: Top Losers (-2% or more in 24h)
- **Caption Theme**: Energetic, trading-focused
- **Target Audience**: Day traders, volatility seekers

**Carousel 3: Trading Opportunities**
- **Templates**: 4.1 → 4.2 (2 slides)
- **Content**:
  - Slide 1: Long Call Positions (bullish opportunities)
  - Slide 2: Short Call Positions (bearish opportunities)
- **Caption Theme**: Professional trading signals
- **Target Audience**: Active traders, position traders

#### **AI Caption Generation**
- **Model**: OpenRouter API - `openai/gpt-4o-mini`
- **Length**: 120-150 characters per carousel
- **Features**:
  - Carousel-specific prompts
  - 3-5 relevant hashtags
  - 1-2 contextual emojis
  - Engagement-optimized hooks
- **Fallback**: Default captions if AI generation fails

#### **Posting Workflow**
```
1. Generate 7 templates (1, 2, 3.1, 3.2, 4.1, 4.2, 6)
   ↓ (uses individual_posts/ generators)
2. Post Carousel 1 (Templates 6, 1, 2)
   ↓
3. Wait 5 minutes (300 seconds)
   ↓
4. Post Carousel 2 (Templates 3.1, 3.2)
   ↓
5. Wait 5 minutes (300 seconds)
   ↓
6. Post Carousel 3 (Templates 4.1, 4.2)
   ↓
7. Report success/failure summary
```

#### **GitHub Actions Automation**
- **Workflow File**: `.github/workflows/Instagram_3_Carousels.yml`
- **Schedule**: Daily at 02:00 UTC (cron: "0 2 * * *")
- **Manual Trigger**: Supports workflow_dispatch
- **Environment**: Ubuntu latest, Python 3.11, Playwright Chromium
- **Secrets Required**:
  - `INSTAGRAM_USERNAME`, `INSTAGRAM_PASSWORD`
  - `OPENROUTER_API_KEY`
  - `GCP_CREDENTIALS`, `CRYPTO_SPREADSHEET_KEY`

#### **Running Manually**
```bash
# Generate all required templates first
python scripts/main/individual_posts/generate_1_output.py
python scripts/main/individual_posts/generate_2_output.py
python scripts/main/individual_posts/generate_3_1_output.py
python scripts/main/individual_posts/generate_3_2_output.py
python scripts/main/individual_posts/generate_4_1_output.py
python scripts/main/individual_posts/generate_4_2_output.py
python scripts/main/individual_posts/generate_6_output.py

# Post all 3 carousels (with 5-minute delays)
python scripts/main/publishing/post_3_carousels.py
```

#### **Key Benefits**
- ✅ **Consistent Daily Presence**: 3 posts keep audience engaged
- ✅ **Diverse Content**: Different themes appeal to different followers
- ✅ **Automated AI Captions**: No manual caption writing needed
- ✅ **Rate-Limit Compliant**: 5-minute delays between posts
- ✅ **Session Management**: Uses persistent sessions to avoid login issues

---

### Monitoring & Performance

#### **Key Metrics Monitored**
- Content generation success rate (7 templates per run)
- Instagram publishing success rate (3 carousels per day)
- Template rendering performance (1-10 seconds per template)
- Screenshot generation timing
- Session health and age
- AI caption generation success rate
- Database query performance
- API rate limit monitoring

#### **Error Handling Features**
- **Retry Logic** - Automatic retry for failed operations
- **Session Recovery** - Bypass validation for stale sessions
- **Credential Validation** - Environment variable verification
- **Database Connection** - Connection pooling and error recovery
- **AI Fallback Captions** - Default captions if AI generation fails
- **API Rate Limiting** - 5-minute delays between carousel posts

### Troubleshooting

#### **Common Issues**

**1. Instagram Login Issues (403 Forbidden)**
- **Cause**: Session expired or invalid
- **Solution**: Run `python scripts/auth/create_instagram_session.py`
- **Prevention**: Monitor session age with `instagram_session_status.py`

**2. AI Caption Generation 404 Error**
- **Cause**: Incorrect OpenRouter model name
- **Solution**: Verify `OPENROUTER_API_KEY` is set correctly
- **Fixed**: Updated to `openai/gpt-4o-mini` in v2.4.0

**3. Template Generation Failures**
- **Cause**: Database connection issues or missing data
- **Solution**: Check PostgreSQL connection and run `validate_env.py`

**4. Playwright Browser Issues**
- **Cause**: Browsers not installed
- **Solution**: Run `playwright install chromium`

**5. GitHub Actions Workflow Failures**
- **Cause**: Deprecated actions or dependency version conflicts
- **Solution**: Check workflow logs, update action versions
- **Recent Fix**: Upgraded `actions/upload-artifact@v3` → `v4`

**6. UTF-8 Encoding Errors (Windows)**
- **Cause**: Windows doesn't default to UTF-8
- **Solution**: Run `scripts/setup/setup_windows_utf8.bat`

#### **Performance Optimization**
- Use connection pooling for database operations
- Implement caching for frequently accessed templates
- Optimize screenshot generation with browser reuse
- Monitor and tune template complexity for rendering speed
- Use session persistence to avoid repeated logins

---

## 📈 Getting Started

### **Quick Start Guide**

1. **Environment Setup**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   playwright install chromium

   # Configure environment variables (copy .env.template to .env)
   # Add: OPENROUTER_API_KEY, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, etc.
   ```

2. **Create Instagram Session** (CRITICAL - do this first!)
   ```bash
   python scripts/auth/create_instagram_session.py
   # Creates data/instagram_session.json (30-day lifecycle)
   ```

3. **Test Environment**
   ```bash
   python scripts/dev/validate_env.py
   python scripts/dev/validate_project.py
   ```

4. **Generate First Template**
   ```bash
   python scripts/main/individual_posts/generate_6_output.py
   # Output: output_html/6_output.html and output_images/6_output.jpg
   ```

5. **Preview Generated Content**
   ```bash
   python scripts/dev/local_server.py
   # Open http://127.0.0.1:8080/6_output.html in browser
   ```

6. **Test 3-Carousel System** (optional)
   ```bash
   # Generate all templates
   python scripts/main/individual_posts/generate_1_output.py
   python scripts/main/individual_posts/generate_2_output.py
   python scripts/main/individual_posts/generate_3_1_output.py
   python scripts/main/individual_posts/generate_3_2_output.py
   python scripts/main/individual_posts/generate_4_1_output.py
   python scripts/main/individual_posts/generate_4_2_output.py
   python scripts/main/individual_posts/generate_6_output.py

   # Post to Instagram (WARNING: posts to live account!)
   python scripts/main/publishing/post_3_carousels.py
   ```

7. **Automation Setup**
   - GitHub Actions workflows run automatically (see `.github/workflows/`)
   - Primary: Instagram 3-Carousel Daily Post (02:00 UTC)
   - Ensure all GitHub Secrets are configured

## 🤝 Contributing

This project is designed for social media automation and data-driven content creation. Contributions welcome for:
- Additional template designs and layouts
- Enhanced AI content generation prompts
- Performance optimizations for image generation
- New social media platform integrations
- Analytics and engagement tracking features

---

**⚠️ Disclaimer**: This system is for legitimate social media automation and content creation purposes. Ensure compliance with Instagram's Terms of Service and API usage policies. Monitor posting frequency and engagement to maintain account standing.