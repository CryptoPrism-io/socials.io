# Socials.io: Automated Social Media Content Generation & Publishing System

An intelligent social media automation platform that transforms data-driven insights into engaging Instagram content through automated HTML-to-image conversion, AI-powered content generation, and seamless publishing workflows.

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
- **`gsheets.py`** - PostgreSQL to Google Sheets data synchronization
- **`figma.py`** - Figma-based design workflow integration

#### 🎨 **Content Generation Engine**
- **`instapost.py`** - Main content generation pipeline with HTML-to-image conversion
- **`instapost_push.py`** - Enhanced content publishing with advanced error handling

### Template System
- **Base Templates**: `1.html` through `5.html` with corresponding CSS stylesheets
- **Dynamic Rendering**: Jinja2-powered data injection into templates
- **Image Output**: Automated screenshot generation at 1080x1080 Instagram format
- **Style Variations**: 5 different visual themes (`style.css` through `style5.css`)

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
- **Instagram Format**: 1080x1080 square aspect ratio
- **Font System**: Poppins font family for consistency
- **Responsive Design**: Viewport-optimized for screenshot generation
- **Brand Colors**: Customizable color schemes per template

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
async def generate_custom_image(html_file, output_path, width=1080, height=1080):
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