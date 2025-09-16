# Socials.io Changelog

All notable changes to the Socials.io project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version Numbering
- **Major (x.0.0)**: Breaking changes, architecture modifications, workflow restructuring
- **Minor (x.y.0)**: New features, workflow additions, template enhancements, non-breaking improvements
- **Patch (x.y.z)**: Bug fixes, documentation updates, configuration tweaks, minor optimizations

## [v1.0.0] - 2025-09-16 20:07 UTC

### 📋 INITIAL: Repository Documentation & Structure
- **Comprehensive Documentation System**: Created complete documentation suite following CryptoPrism-DB standards
  - **CLAUDE.md**: AI assistant guidance with project overview, commands, architecture details, and environment variables
  - **README.md**: Professional project documentation with WHAT/WHY/HOW structure, installation guide, and usage examples
  - **CHANGELOG.md**: Standardized change tracking system with semantic versioning and maintenance protocols

### 🏗️ **Project Architecture Documentation**
- **System Overview**:
  - Multi-source data pipeline for automated Instagram content creation
  - HTML/CSS template system with Jinja2 rendering engine
  - Playwright-based HTML-to-image conversion at 1080x1080 format
  - AI-powered content generation via Together AI API
  - PostgreSQL + Google Sheets + Google Drive integration

- **Core Components Analysis**:
  - **Data Management**: `gsheets.py` (PostgreSQL→Google Sheets sync), `figma.py` (Figma integration)
  - **Content Generation**: `instapost.py` (main pipeline), `instapost_push.py` (enhanced publishing)
  - **Template System**: 5 HTML templates with corresponding CSS stylesheets
  - **Automation**: GitHub Actions workflows for daily content publishing

### 🛠️ **Technical Stack Documentation**
- **Dependencies**: Complete installation guide for all required packages
  - Core: `together`, `psycopg2`, `pandas`, `gspread`, `instagrapi`, `playwright`, `jinja2`
  - Browsers: Chromium, Firefox, WebKit installation via Playwright
  - Python: 3.10+ requirement for GitHub Actions compatibility

- **Environment Configuration**: Comprehensive .env setup with 6 required variables
  - `GCP_CREDENTIALS`: Google Cloud service account JSON
  - `TOGETHER_API_KEY`: AI content generation API
  - `INSTAGRAM_USERNAME/PASSWORD`: Publishing credentials
  - `INSTAGRAM_DRIVE_FILE_ID`: Google Drive file integration
  - `CRYPTO_SPREADSHEET_KEY`: Data source spreadsheet

### 🔄 **GitHub Actions Workflow Analysis**
- **3-Workflow Automation System**:
  - **Google Sheets Sync** (gsheets.yml): Daily 00:30 UTC data synchronization
  - **Instagram Content Pipeline** (Instagram_Story.yml): Sequential content generation + publishing
  - **Figma Integration** (figma.yml): Manual trigger for design workflow

- **Workflow Dependencies**:
  - Sequential execution: `instapost.py` → `instapost_push.py`
  - Environment management with GitHub Secrets
  - Error handling and retry mechanisms

### 📊 **Template & Content System**
- **5-Template Design System**:
  - Base templates: `1.html` through `5.html`
  - Dynamic output: `*_output.html` files with data injection
  - Styling: Individual CSS files (`style.css` through `style5.css`)
  - Image generation: PNG/JPG outputs for Instagram posting

### 💡 **Rationale**
**Professional Documentation Standards**: Established enterprise-grade documentation system following proven patterns from CryptoPrism-DB repository. This comprehensive documentation ensures:

- **Rapid Onboarding**: Clear architecture overview and setup instructions for new developers
- **Operational Clarity**: Complete command reference and workflow understanding for daily operations
- **Maintenance Excellence**: Standardized changelog maintenance protocols for consistent change tracking
- **Technical Preservation**: Detailed environment and dependency documentation for reliable deployments

**Business Value**: Professional documentation enables efficient team collaboration, reduces debugging time, and ensures consistent deployment practices across the social media automation pipeline.

The documentation system supports the project's core mission of automated, data-driven Instagram content creation by providing clear operational guidelines and comprehensive technical reference materials.

**Commit Hash**: [To be added after commit]

---

## 📋 CHANGELOG MAINTENANCE PROTOCOL

### 📋 CHANGELOG.MD MAINTENANCE PROTOCOL
```
│ 📋 CHANGELOG.MD MAINTENANCE PROTOCOL                                    │
│                                                                         │
│ For EVERY file modification, code change, or system update, ALWAYS     │
│ update CHANGELOG.md with proper versioning before committing changes.  │
│                                                                         │
│ Auto-trigger changelog updates when:                                    │
│ 1. Script modifications - Any Python file, HTML template, or CSS changes │
│ 2. New features added - Templates, workflows, integrations, etc.       │
│ 3. Security improvements - Credential handling, API security fixes     │
│ 4. Infrastructure changes - GitHub Actions, environment config         │
│ 5. Bug fixes - Error corrections, publishing improvements              │
│ 6. Documentation updates - README changes, setup instructions          │
│                                                                         │
│ Version increment rules:                                                │
│ - Major (X.0.0): Breaking changes, workflow restructuring              │
│ - Minor (X.Y.0): New features, template additions, workflow improvements │
│ - Patch (X.Y.Z): Bug fixes, documentation updates, minor configuration │
│                                                                         │
│ Required changelog entries:                                             │
│ - Version number with UTC timestamp                                     │
│ - Added/Changed/Fixed/Security/Removed categories                       │
│ - Detailed rationale explaining business/technical justification        │
│ - Commit hash reference after committing                                │
│ - Impact analysis and social media workflow considerations              │
│                                                                         │
│ Process:                                                                │
│ 1. Before changes: Plan version increment based on change scope        │
│ 2. Make modifications: Document what's being changed and why           │
│ 3. Update CHANGELOG.md: Add comprehensive entry with business rationale │
│ 4. Commit changes: Include descriptive commit message                   │
│ 5. Add commit hash: Reference back to changelog entry                   │
```

### Change Categories
- **Added**: New scripts, templates, workflows, features, or integrations
- **Changed**: Modified existing functionality, template updates, workflow improvements
- **Deprecated**: Features or templates marked for future removal
- **Removed**: Deleted files, features, or deprecated functionality
- **Fixed**: Bug repairs, publishing errors, template rendering issues
- **Security**: Security-related improvements, credential protection, API security

### Socials.io Specific Considerations

#### Content Generation Changes
- **Template Modifications**: Document visual changes, layout updates, styling improvements
- **AI Prompt Updates**: Track content generation prompt modifications and effectiveness
- **Publishing Logic**: Record Instagram API changes, posting frequency adjustments

#### Infrastructure Changes
- **GitHub Actions**: Document workflow timing changes, dependency updates, secret modifications
- **Database Integration**: Track PostgreSQL connection changes, Google Sheets API updates
- **Environment Variables**: Document new credentials, API key changes, configuration updates

#### Performance & Monitoring
- **Screenshot Generation**: Track Playwright performance improvements, browser optimization
- **Publishing Success Rates**: Document Instagram API reliability improvements
- **Template Rendering**: Record Jinja2 optimization, CSS performance enhancements

### Git Integration Process
1. **Before Committing**: Update changelog with planned changes and version increment
2. **After Committing**: Add commit hash to changelog entry for traceability
3. **Batch Updates**: For multiple related commits, create comprehensive changelog entries
4. **Template Changes**: Include before/after visual descriptions for template modifications

### Useful Git Commands for Socials.io Maintenance
```bash
# Get recent commits with file changes (useful for template tracking)
git log --stat -10

# Get commit messages with dates for scheduling correlation
git log --pretty=format:"%h|%ad|%s|%an" --date=iso -20

# View files changed in specific commit (template/script tracking)
git show --name-only <commit-hash>

# Get commits affecting specific templates
git log --oneline -- "*.html" "*.css"

# Track workflow changes
git log --oneline -- ".github/workflows/"
```

### Template for Future Entries
```markdown
## [vX.Y.Z] - YYYY-MM-DD HH:MM UTC

### Added
- New templates, features, or workflow improvements

### Changed
- Template modifications, workflow updates, or publishing improvements

### Fixed
- Instagram publishing issues, template rendering bugs, or workflow errors

### Security
- Credential protection, API security improvements, or access control

### Rationale
- Business justification for changes
- Social media impact analysis
- Technical benefits and performance improvements
- Risk considerations for Instagram compliance

**Commit Hash**: `abc1234`
```

### Version Increment Guidelines for Socials.io

1. **Major Version (X.0.0)**: Reserved for breaking changes:
   - Complete workflow restructuring
   - Template system overhauls
   - Instagram API breaking changes
   - Database schema modifications

2. **Minor Version (X.Y.0)**: For enhancements and new features:
   - New template designs or layouts
   - Additional social media platform integrations
   - Workflow improvements or new automation features
   - AI content generation enhancements

3. **Patch Version (X.Y.Z)**: For maintenance and fixes:
   - Template bug fixes or minor visual adjustments
   - Publishing error corrections
   - Configuration updates or dependency patches
   - Documentation improvements

### Social Media Compliance Tracking
- **Instagram Policy Changes**: Document updates to comply with Instagram API policies
- **Publishing Frequency**: Track timing adjustments to maintain account standing
- **Content Guidelines**: Record template modifications for platform compliance
- **Engagement Monitoring**: Document changes affecting post engagement and reach