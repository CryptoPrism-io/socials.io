# Socials.io: Complete Instagram Content Automation System v2.1.0

A comprehensive social media automation platform featuring 19 professional Instagram templates, AI-powered market analysis, and real-time data integration. Transform crypto market data into engaging visual content through automated HTML-to-image conversion and intelligent publishing workflows.

---

## 🔍 WHAT - System Overview

### Architecture
Socials.io operates on a **multi-source data pipeline** designed for automated content creation:

- **Data Sources** - PostgreSQL database, Google Sheets, and Google Drive integration
- **Content Generation** - AI-powered content creation using Together AI API
- **Template System** - HTML/CSS template engine with Jinja2 rendering
- **Image Generation** - Playwright-based HTML-to-image conversion
- **Publishing Platform** - Instagram API integration via instagrapi

### Core Components (4 Specialized Scripts)

#### 📊 **Data Collection & Management**
- **`src/scripts/gsheets.py`** - PostgreSQL to Google Sheets data synchronization
- **`src/scripts/figma.py`** - Figma-based design workflow integration

#### 🎨 **Content Generation Engine**
- **`src/scripts/instapost.py`** - Main content generation pipeline with HTML-to-image conversion
- **`src/scripts/instapost_push.py`** - Enhanced content publishing with advanced error handling

### 🚀 Complete Instagram Template System (19 Templates)
- **Core Templates**: `core_templates/` directory with professional designs:
  - **Legacy Templates**: `1.html` through `5.html` (coin grids and market overviews)
  - **Advanced Templates**: `6.html` through `16.html` (specialized content types)
  - **🆕 Trading Performance Templates**: `17.html` through `19.html` (transparency & credibility)
  - **AI-Powered Template 6**: Real-time market analysis with VIBES/GIANTS/CATALYSTS structure
  - **Comprehensive Coverage**: Every major crypto content category covered

#### 📊 Template Categories & Coverage
- **Market Analysis** (Templates 6, 10): AI sentiment analysis, Fear & Greed Index
- **Performance Tracking** (Templates 7, 11): Gainers/losers, weekly recaps
- **News & Events** (Templates 8, 14): Breaking news, crypto calendar
- **Trading Intelligence** (Templates 9, 12): Liquidations, whale alerts
- **DeFi Ecosystem** (Template 13): TVL rankings, protocol analysis
- **Scaling Solutions** (Template 15): Layer 2 comparisons, gas savings
- **Meme Culture** (Template 16): Viral tracking with risk warnings
- **🆕 Trading Performance** (Templates 17-19): Transparency, portfolio tracking, trading statistics

- **Professional Design System**:
  - **Unified CRYPTO PRISM Branding**: Consistent visual identity across all templates
  - **Glassmorphism Effects**: Modern backdrop filters and transparency layers
  - **Instagram Optimization**: Perfect 1080x1080 format with mobile-first design
  - **Color-Coded Data**: Impact ratings, performance indicators, risk assessments
  - **Animation Systems**: Subtle animations and hover effects for engagement

- **AI Integration**: OpenRouter API with Claude 3.5 Sonnet for intelligent analysis
- **Real-Time Data**: Live market data integration across all templates
- **Generated Content**: `output/` directory with HTML and image outputs
- **Dynamic Rendering**: Jinja2-powered template system with live data injection

### 🆕 Trading Performance & Transparency Templates (17-19)

**Build credibility through transparent trading performance:**

#### 📊 **Template 17: Trade History & Performance**
- **Recent Trades**: Last 10 completed trades with entry/exit details
- **P&L Tracking**: Transparent profit/loss results in USD and percentage
- **Win/Loss Analytics**: Clear success/failure indicators with color coding
- **Risk Management**: Risk-reward ratios and trade duration tracking
- **Performance Summary**: Overall stats and best/worst trade highlights

#### 💼 **Template 18: Portfolio Dashboard**
- **Real-Time Portfolio Value**: Current USD value with 7D/30D/90D performance
- **Open Positions**: Active trades with current P&L and allocation percentages
- **Asset Allocation**: Visual breakdown by cryptocurrency holdings
- **Risk Metrics**: Professional metrics (Sharpe ratio, max drawdown, volatility)
- **Balance History**: Portfolio value progression over time

#### 📈 **Template 19: Trading Statistics & Analytics**
- **Overall Performance**: Win rate, total P&L, profit factor, average win/loss
- **Long vs Short Analysis**: Separate performance metrics for each trade type
- **Monthly Performance**: Calendar view of monthly returns and trade counts
- **Asset Performance**: Best performing cryptocurrencies by profitability
- **Advanced Metrics**: Calmar ratio, Sortino ratio, streak analysis
- **Professional Risk Assessment**: Comprehensive trading analytics

**Why Trading Performance Templates Matter:**
- **Build Trust**: Transparent P&L tracking proves real trading skills
- **Demonstrate Expertise**: Professional risk metrics show sophisticated approach
- **Create Accountability**: Honest win/loss ratios build follower confidence
- **Establish Credibility**: Real results separate you from prediction-only accounts

## 📁 Project Structure

```
socials.io/
├── 📁 src/                          # Source code directory
│   ├── 📁 scripts/                  # Main application scripts
│   │   ├── 📄 instapost.py          # Main content generation pipeline
│   │   ├── 📄 instapost_push.py     # Enhanced publishing workflow
│   │   ├── 📄 gsheets.py            # Google Sheets data synchronization
│   │   ├── 📄 figma.py              # Figma integration workflow
│   │   ├── 📄 instapost_new.py      # Development/experimental script
│   │   ├── 📄 linkedin_auth.py      # LinkedIn authentication
│   │   └── 📄 twitter_auth.py       # Twitter authentication
│   └── 📁 utils/                    # Utility modules & helpers
├── 📁 core_templates/               # Complete template system (19 templates)
│   ├── 📄 1.html → 5.html           # Legacy coin grid templates
│   ├── 📄 6.html                    # AI market analysis (VIBES/GIANTS/CATALYSTS)
│   ├── 📄 7.html → 16.html          # Specialized content templates
│   ├── 📄 17.html → 19.html         # 🆕 Trading performance templates
│   └── 📄 style.css → style19.css   # Complete CSS stylesheet collection
├── 📁 output/                       # Generated content output (excluded from git)
│   ├── 📁 html/                     # Generated HTML files with descriptive naming
│   │   ├── 📄 market_overview_output.html       # Template 1: Market Overview
│   │   ├── 📄 crypto_vibes_output.html          # Template 6: AI Analysis
│   │   ├── 📄 meme_coin_tracker_output.html     # Template 16: Meme Coins
│   │   ├── 📄 trade_history_output.html         # Template 17: Trading Performance
│   │   ├── 📄 portfolio_dashboard_output.html   # Template 18: Portfolio Tracking
│   │   ├── 📄 trading_statistics_output.html    # Template 19: Trading Analytics
│   │   └── 📄 ... (all 19 templates)           # Professional descriptive naming
│   │   └── 📄 style*.css             # CSS files copied during generation
│   └── 📁 images/                   # Generated Instagram images with descriptive naming
│       ├── 📄 market_overview_output.jpg        # Template 1: Market Overview
│       ├── 📄 meme_coin_tracker_output.jpg      # Template 16: Meme Coins
│       ├── 📄 trade_history_output.jpg          # Template 17: Trading Performance
│       ├── 📄 portfolio_dashboard_output.jpg    # Template 18: Portfolio Dashboard
│       ├── 📄 trading_statistics_output.jpg     # Template 19: Trading Analytics
│       └── 📄 ... (all 19 templates)           # Instagram-ready JPG outputs
├── 📁 src/utils/                    # AI & utility modules
│   ├── 📄 openrouter_analyzer.py   # OpenRouter API integration
│   └── 📄 text_highlighter.py      # Dynamic text highlighting
├── 📁 config/                       # Configuration modules
│   └── 📄 paths.py                  # Path configuration management
├── 📁 tests/                        # Test suite
│   ├── 📄 test_path_structure.py    # Path validation tests
│   └── 📄 test_restructure.py       # Structure validation tests
├── 📁 scripts/                      # Setup & utility scripts
│   ├── 📁 demos/                    # Demo and testing scripts
│   │   ├── 📄 demo_mypy.py          # MyPy demonstration script
│   │   └── 📄 demo_retry.py         # Retry mechanism demonstration
│   ├── 📄 setup_windows_utf8.bat    # Windows UTF-8 setup (batch)
│   ├── 📄 setup_windows_utf8.ps1    # Windows UTF-8 setup (PowerShell)
│   ├── 📄 setup_powershell_utf8.ps1 # PowerShell profile UTF-8 setup
│   ├── 📄 test_unicode_system.py    # Unicode validation script
│   ├── 📄 utf8_fix.py               # UTF-8 encoding fix utility
│   ├── 📄 validate_env.py           # Environment validation
│   ├── 📄 validate_project.py       # Project validation
│   ├── 📄 .env.backup               # Environment backup file
│   ├── 📄 .env.template             # Environment template file
│   └── 📄 UNICODE_*.md              # Unicode documentation
├── 📁 docs/                         # Documentation
│   ├── 📁 assets/                   # Documentation images and media
│   ├── 📄 DEPLOYMENT_SUMMARY.md     # Deployment documentation
│   ├── 📄 TODO.md                   # Production hardening TODO
│   └── 📄 instagram_session_management.md # Instagram session docs
├── 📁 logs/                         # Application logs and temporary files
├── 📁 tests/                        # Test suite
│   ├── 📄 test_path_structure.py    # Path validation tests
│   ├── 📄 test_restructure.py       # Structure validation tests
│   ├── 📄 test_logging.py           # Logging functionality tests
│   └── 📄 test_mypy.py              # MyPy integration tests
├── 📁 .github/workflows/            # GitHub Actions CI/CD
│   ├── 📄 Instagram_Story.yml       # Instagram automation workflow
│   ├── 📄 gsheets.yml               # Google Sheets sync workflow
│   ├── 📄 figma.yml                 # Figma integration workflow
│   └── 📄 ci-cd.yml                 # CI/CD pipeline
├── 📁 delete_folder/                # Cleanup - duplicate files removed
│   └── 📄 *.html, *.css             # Old root-level duplicates
├── 📄 .env                          # Environment variables (sensitive)
├── 📄 requirements.txt              # Python dependencies
├── 📄 requirements-dev.txt          # Development dependencies
├── 📄 README.md                     # Project documentation (this file)
├── 📄 CHANGELOG.md                  # Version history & changes
├── 📄 CLAUDE.md                     # AI assistant guidance
└── 📄 .gitignore                    # Git ignore rules
```

### 📂 Directory Purposes

| Directory | Purpose | Contains |
|-----------|---------|----------|
| **`src/`** | Source code | Main application scripts, templates, utilities |
| **`src/scripts/`** | Core functionality | Instagram automation, data sync, publishing |
| **`core_templates/`** | Template system | Auto-layout HTML templates, flexbox CSS styles |
| **`output/`** | Generated content | HTML outputs, generated images for posting |
| **`config/`** | Configuration | Path management, system configuration |
| **`tests/`** | Testing suite | Unit tests, validation scripts, test data |
| **`scripts/`** | Setup utilities | Installation scripts, environment setup, validation |
| **`docs/`** | Documentation | Deployment guides, technical documentation |
| **`.github/workflows/`** | Automation | CI/CD pipelines, GitHub Actions workflows |
| **`delete_folder/`** | Cleanup | Duplicate files removed during organization |

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Automation** | Playwright (async) | HTML screenshot generation |
| **AI Content** | Together AI API | Content generation and captions |
| **Instagram API** | instagrapi | Automated posting and publishing |
| **Template Engine** | Jinja2 | Dynamic HTML content rendering |
| **Database** | PostgreSQL + SQLAlchemy | Data storage and management |
| **Google Services** | gspread, Google Drive/Sheets API | Cloud data integration |
| **Image Processing** | Pillow (PIL) | Image optimization and processing |

### 🔄 Automated Publishing Pipeline

#### **GitHub Actions Automation**
Socials.io features a **3-workflow automated system** that runs daily:

```
DATA SYNC → CONTENT GENERATION → PUBLISHING
```

#### **Workflow 1: Google Sheets Sync** (Daily 00:30 UTC)
- **Purpose**: Synchronize PostgreSQL data with Google Sheets
- **Module**: `gsheets.py`
- **Output**: Updated spreadsheets with latest data

#### **Workflow 2: Instagram Content Pipeline** (Daily 00:30 UTC)
- **Purpose**: Generate and publish Instagram carousel posts
- **Execution Order**:
  1. `instapost.py` - Content generation and image creation
  2. `instapost_push.py` - Enhanced publishing with error handling
- **Technology**: Python 3.10, Playwright browsers, AI content generation

#### **Workflow 3: Figma Integration** (Manual Trigger)
- **Purpose**: Figma-based content creation workflow
- **Module**: `figma.py`
- **Trigger**: Manual workflow dispatch

#### **Pipeline Features**
- **Sequential Dependencies** - Content generation → Publishing workflow
- **Error Handling** - Comprehensive error management and retry logic
- **Multi-browser Support** - Chromium, Firefox, and WebKit for screenshot generation
- **AI Integration** - Together AI for intelligent content creation
- **Credential Security** - Environment variable-based authentication

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
- Python 3.10+
- PostgreSQL database access
- Google Cloud Platform service account
- Instagram account credentials
- Together AI API access

#### **External Services Setup**
```bash
# Required API Keys and Credentials
GCP_CREDENTIALS           # Google Cloud service account JSON
TOGETHER_API_KEY         # Together AI API key
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
# Core dependencies for all workflows
pip install together psycopg2 nest_asyncio requests pandas gspread oauth2client google-api-python-client google-auth-httplib2 google-auth-oauthlib instagrapi playwright python-dotenv pillow sqlalchemy jinja2

# Install Playwright browsers for screenshot generation
playwright install chromium
playwright install firefox
playwright install webkit
```

#### **3. Environment Configuration**
Create `.env` file with required variables:
```env
# Google Cloud Platform
GCP_CREDENTIALS={"type": "service_account", "project_id": "..."}

# AI Content Generation
TOGETHER_API_KEY=your_together_api_key_here

# Instagram Publishing
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# Google Drive Integration
INSTAGRAM_DRIVE_FILE_ID=your_google_drive_file_id
CRYPTO_SPREADSHEET_KEY=your_google_sheets_key

# Database Connection (if running locally)
DB_HOST=your_postgresql_host
DB_NAME=dbcp
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_PORT=5432
```

### Execution Workflows

#### **Data Synchronization**
```bash
# Sync PostgreSQL data to Google Sheets
python gsheets.py

# Expected output: Updated spreadsheets with latest database records
```

#### **Content Generation & Publishing**
```bash
# Generate Instagram content from data
python instapost.py

# Publish generated content with enhanced error handling
python instapost_push.py

# Expected output:
# - Generated HTML files (1_output.html through 5_output.html)
# - Screenshot images (*.jpg files)
# - Published Instagram carousel posts
```

#### **Figma Integration**
```bash
# Generate Figma-based content
python figma.py

# Expected output: Figma design integration with data sources
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

### Monitoring & Performance

#### **Key Metrics Monitored**
- Content generation success rate
- Instagram publishing success rate
- Template rendering performance
- Screenshot generation timing
- Database query performance
- API rate limit monitoring

#### **Error Handling Features**
- **Retry Logic** - Automatic retry for failed operations
- **Fallback Templates** - Alternative templates for generation failures
- **Credential Validation** - Environment variable verification
- **Database Connection** - Connection pooling and error recovery
- **API Rate Limiting** - Intelligent request throttling

### Troubleshooting

#### **Common Issues**
1. **Playwright Browser Issues** - Ensure all browsers installed correctly
2. **Instagram API Limits** - Monitor posting frequency and account restrictions
3. **Template Rendering Errors** - Verify Jinja2 syntax and data structure
4. **Database Connectivity** - Check PostgreSQL connection and credentials
5. **Google API Quotas** - Monitor Sheets/Drive API usage limits

#### **Performance Optimization**
- Use connection pooling for database operations
- Implement caching for frequently accessed templates
- Optimize screenshot generation with browser reuse
- Monitor and tune template complexity for rendering speed

---

## 📈 Getting Started

1. **Environment Setup** - Configure all required API keys and credentials
2. **Test Data Flow** - Run `gsheets.py` to verify data synchronization
3. **Template Testing** - Generate test content with `instapost.py`
4. **Publishing Test** - Verify Instagram integration with `instapost_push.py`
5. **Automation Setup** - Configure GitHub Actions for daily automation

## 🤝 Contributing

This project is designed for social media automation and data-driven content creation. Contributions welcome for:
- Additional template designs and layouts
- Enhanced AI content generation prompts
- Performance optimizations for image generation
- New social media platform integrations
- Analytics and engagement tracking features

---

**⚠️ Disclaimer**: This system is for legitimate social media automation and content creation purposes. Ensure compliance with Instagram's Terms of Service and API usage policies. Monitor posting frequency and engagement to maintain account standing.