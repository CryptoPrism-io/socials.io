# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
# Install core dependencies
pip install -r requirements.txt

# Install Playwright browsers for screenshot generation
playwright install chromium

# Windows UTF-8 setup (if needed)
scripts/setup/setup_windows_utf8.bat

# Create Instagram session (CRITICAL - do this first!)
python scripts/auth/create_instagram_session.py
```

### Testing & Validation
```bash
# Run structure validation
python tests/test_path_structure.py

# Environment validation
python scripts/dev/validate_env.py
python scripts/dev/validate_project.py

# Full test suite (when available)
python -m pytest tests/ -v --tb=short
```

### Local Development
```bash
# Generate individual templates
python scripts/main/individual_posts/generate_6_output.py   # Bitcoin + Macro Intelligence
python scripts/main/individual_posts/generate_7_output.py   # Market Intelligence (L2 AI)

# Preview generated content at http://127.0.0.1:8080/
python scripts/dev/local_server.py
```

### Instagram Session Management
```bash
# Create new session (30-day lifecycle, rate-limited to once per 7 days)
python scripts/auth/create_instagram_session.py

# Check session health
python scripts/auth/instagram_session_status.py

# CRITICAL: Always use session manager for Instagram operations
# Never login repeatedly with username/password - triggers Instagram security alerts
```

### 3-Carousel Instagram Posting (Primary System - v2.4.0)
```bash
# Generate all 7 required templates
python scripts/main/individual_posts/generate_1_output.py    # Top Cryptos 2-24
python scripts/main/individual_posts/generate_2_output.py    # Extended 25-48
python scripts/main/individual_posts/generate_3_1_output.py  # Top Gainers
python scripts/main/individual_posts/generate_3_2_output.py  # Top Losers
python scripts/main/individual_posts/generate_4_1_output.py  # Long Calls
python scripts/main/individual_posts/generate_4_2_output.py  # Short Calls
python scripts/main/individual_posts/generate_6_output.py    # Bitcoin Intelligence

# Post 3 carousels to Instagram (with AI captions)
python scripts/main/publishing/post_3_carousels.py
```

## High-Level Architecture

### Data Flow Pipeline
```
PostgreSQL Database → Python Data Fetching → Jinja2 Template Rendering →
HTML Generation → Playwright Screenshot (2160x2700 viewport) →
JPG Image (1080x1080, 95% quality) → Instagram Posting (instagrapi)
```

### 3-Carousel System (v2.4.0 - Primary Automation)
Daily automated Instagram posting at 02:00 UTC via GitHub Actions:

**Carousel 1** (3 slides): Bitcoin Intelligence + Market Overview
- Template 6: Bitcoin + Macro Intelligence (Fear & Greed Index + BTC Price dual-axis chart)
- Template 1: Top Cryptocurrencies (ranks 2-24)
- Template 2: Extended Cryptocurrencies (ranks 25-48)

**Carousel 2** (2 slides): Market Movers
- Template 3.1: Top Gainers (+2% or more in 24h)
- Template 3.2: Top Losers (-2% or more in 24h)

**Carousel 3** (2 slides): Trading Opportunities
- Template 4.1: Long Call Positions (bullish opportunities)
- Template 4.2: Short Call Positions (bearish opportunities)

Each carousel gets AI-generated captions via OpenRouter API (GPT-4o-mini). 5-minute delays between posts.

### Module Organization (Modular Architecture)

**Core Modules** (`scripts/main/`):
- `individual_posts/` - 9 standalone template generators (PRIMARY system)
- `publishing/session_manager.py` - Instagram session lifecycle (30-day persistence, 7-day rate-limiting)
- `publishing/post_3_carousels.py` - 3-carousel automation system
- `content/openrouter_client.py` - AI content generation (replaces Together AI)
- `content/template_engine.py` - Jinja2 template rendering
- `media/screenshot.py` - Playwright HTML-to-image conversion
- `data/database.py` - PostgreSQL operations via SQLAlchemy
- `workflows/` - Complete pipeline orchestration (generation + publishing)

**Authentication** (`scripts/auth/`):
- `create_instagram_session.py` - Create persistent session (CRITICAL step)
- `instagram_session_status.py` - Monitor session health and age

**Development Tools** (`scripts/dev/`):
- `local_server.py` - Preview HTML outputs on port 8080
- `validate_env.py` - Environment variable validation

### Instagram Session Management (CRITICAL)

**Why it matters**: Frequent username/password logins trigger Instagram security alerts, 2FA challenges, and account lockouts.

**Session Lifecycle**:
1. Create session once: `scripts/auth/create_instagram_session.py`
2. Session stored: `data/instagram_session.json` (also backed up to `sessions/`)
3. 30-day validity with automatic metadata tracking
4. Rate-limiting: 7-day minimum between fresh logins (168 hours)
5. All publishing scripts use session instead of credentials

**Key Methods**:
- `get_smart_client()` - Load existing session or create new (respects rate-limiting)
- `get_client_bypass_validation()` - Bypass instagrapi ~2.1 validation bugs for stale sessions
- `force_refresh_session()` - Emergency refresh (bypasses rate-limiting)

**NEVER** repeatedly login with username/password. **ALWAYS** use session manager.

### Template System

**10 Template Variations** (`base_templates/`):
- Templates 1-7 (11 HTML files total due to splits: 3_1/3_2, 4_1/4_2)
- Auto-layout flexbox architecture (no absolute positioning)
- Dedicated CSS stylesheets (style1.css → style7.css)
- Instagram-optimized: 1080x1080 output from 2160x2700 viewport
- Jinja2 dynamic data injection with proper path resolution

**Template 6 & 7 Special Features**:
- Template 6: Dual-axis chart (Fear & Greed Index + Bitcoin Price)
- Template 7: L2 AI filtering (web search + quality validation)

### GitHub Actions Workflows

**Primary**: `.github/workflows/Instagram_3_Carousels.yml` (Daily 02:00 UTC)
- Generates 7 templates → Posts 3 carousels with AI captions
- Python 3.11, Ubuntu latest, Playwright Chromium
- Secrets: INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, OPENROUTER_API_KEY, GCP_CREDENTIALS

**Secondary**:
- `Instagram_Story.yml` - Legacy single carousel (00:31 UTC, superseded)
- `gsheets.yml` - Google Sheets sync (00:31 UTC)
- `figma.yml` - Manual trigger only

## Code Architecture Patterns

### Database Operations
```python
# PostgreSQL via SQLAlchemy with connection pooling
from scripts.main.data.database import fetch_top_coins, fetch_btc_snapshot

# Clean connection lifecycle - always close connections
coins = fetch_top_coins(start_rank=2, end_rank=24)
```

### Template Rendering
```python
# Jinja2 with absolute path resolution
from scripts.main.content.template_engine import render_template

html = render_template('6.html', context={
    'btc_data': btc_snapshot,
    'news_items': ai_generated_news
})
```

### Screenshot Generation
```python
# Playwright async pattern with proper viewport scaling
from scripts.main.media.screenshot import generate_screenshot
import asyncio

await generate_screenshot(
    html_file='output_html/6_output.html',
    output_file='output_images/6_output.jpg',
    width=2160, height=2700  # Instagram viewport
)
```

### AI Content Generation
```python
# OpenRouter API (replaces Together AI)
from scripts.main.content.openrouter_client import OpenRouterClient

client = OpenRouterClient()
caption = client.generate_caption(
    model="openai/gpt-4o-mini",  # Cheapest GPT-4 option
    prompt="Generate Instagram caption for crypto market update..."
)
```

### Instagram Session Usage
```python
# ALWAYS use session manager
from scripts.main.publishing.session_manager import InstagramSessionManager

session_mgr = InstagramSessionManager(session_file="data/instagram_session.json")
client = session_mgr.get_client_bypass_validation()  # For stale sessions

# Post carousel
media = client.album_upload(paths=[...], caption=ai_caption)
```

## Environment Variables

**Required** (in `.env` file):
```bash
# Database
DB_HOST=your_postgresql_host
DB_NAME=dbcp
DB_USER=your_username
DB_PASSWORD=your_password

# AI Content Generation
OPENROUTER_API_KEY=your_key_here  # Replaces TOGETHER_API_KEY

# Instagram
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Google Cloud
GCP_CREDENTIALS={"type": "service_account", ...}
CRYPTO_SPREADSHEET_KEY=your_sheets_key
```

## Critical Production Notes

### Session Management
- Session files in `data/` and `sessions/` are .gitignored (contain auth tokens)
- 7-day rate-limiting prevents Instagram security blocks
- Session metadata tracks: creation date, login count, device UUIDs, validation timestamps

### Together AI → OpenRouter Migration
- **Old**: `TOGETHER_API_KEY` (deprecated, removed from requirements.txt)
- **New**: `OPENROUTER_API_KEY` with `openai/gpt-4o-mini` model
- All AI caption generation now uses OpenRouter API

### Template Split Architecture (v2.3.0+)
- Template 3 split: 3.html → 3_1.html (Gainers) + 3_2.html (Losers)
- Template 4 split: 4.html → 4_1.html (Long) + 4_2.html (Short)
- Maintains backward compatibility with base templates

### Windows UTF-8 Handling
- Windows doesn't default to UTF-8 encoding
- Run `scripts/setup/setup_windows_utf8.bat` if encountering encoding errors
- Troubleshooting docs: `scripts/config/UNICODE_TROUBLESHOOTING.md`

### Playwright Best Practices
- Always use async/await pattern
- Set viewport to 2160x2700 for Instagram-optimized screenshots
- Images saved as JPEG 95% quality (Instagram optimization)
- Browser cleanup in try/finally blocks

### Instagram API Compliance
- 5-minute delays between carousel posts (rate-limiting)
- Session persistence prevents security alerts
- Respect Instagram ToS and posting frequency limits
- Never use force_refresh_session() unless absolutely necessary

## Common Pitfalls

1. **Forgetting to create session**: Run `scripts/auth/create_instagram_session.py` first
2. **Using wrong AI API**: Use `OPENROUTER_API_KEY`, not `TOGETHER_API_KEY`
3. **Absolute positioning in templates**: Use flexbox auto-layout instead
4. **Template path errors**: Use absolute path resolution in Jinja2
5. **Session rate-limiting**: Wait 7 days between fresh logins
6. **Windows UTF-8**: Run setup script if encoding errors occur
7. **Committing session files**: Both `data/` and `sessions/` are .gitignored

## Development Workflow

### Adding New Templates
1. Create HTML in `base_templates/X.html` with flexbox layout
2. Create CSS in `base_templates/styleX.css`
3. Create generator in `scripts/main/individual_posts/generate_X_output.py`
4. Follow existing generator pattern (see `individual_posts/README.md`)
5. Test with local server: `python scripts/dev/local_server.py`
6. Update 3-carousel workflow if needed

### Modifying Existing Templates
1. Edit base template in `base_templates/`
2. Update corresponding CSS in same directory
3. Test generation: `python scripts/main/individual_posts/generate_X_output.py`
4. Preview: http://127.0.0.1:8080/X_output.html
5. Verify screenshot output in `output_images/`

### Troubleshooting Instagram 403 Errors
1. Check session age: `python scripts/auth/instagram_session_status.py`
2. If expired, create new: `python scripts/auth/create_instagram_session.py`
3. Verify credentials in `.env` file
4. Ensure not hitting 7-day rate-limit

## Production Hardening (TODO.md)

**P0 Critical**:
- Session management rate-limiting (✅ DONE)
- OpenRouter API migration (✅ DONE)
- Dependency cleanup (requirements.txt duplicates)
- Script consolidation (multiple instapost variants)

**P1 Important**:
- Configuration module (pydantic-settings for env vars)
- Structured logging with correlation IDs
- Type checking with mypy

**P2 Longer Term**:
- Package structure (pyproject.toml)
- Containerization with Dockerfile
- Pre-commit hooks
