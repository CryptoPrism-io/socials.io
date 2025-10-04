# Individual Post Generators

This directory contains individual Python scripts for generating each template output independently. Each script generates both HTML and screenshot images for Instagram-ready content.

## Available Templates

### Template 1: Top Cryptocurrencies
**File**: `generate_1_output.py`
**Description**: Generates top cryptocurrencies list (ranks 2-24, excluding Bitcoin)
**Data Source**: `fetch_top_coins(2, 24)`
**Output**: `1_output.html` + `1_output.jpg`

```bash
cd scripts/main/individual_posts
python generate_1_output.py
```

### Template 2: Extended Cryptocurrencies
**File**: `generate_2_output.py`
**Description**: Generates extended cryptocurrencies list (ranks 25-48)
**Data Source**: `fetch_top_coins(25, 48)`
**Output**: `2_output.html` + `2_output.jpg`

```bash
cd scripts/main/individual_posts
python generate_2_output.py
```

### Template 3: Top Gainers and Losers
**File**: `generate_3_output.py`
**Description**: Generates top gainers and losers analysis
**Data Source**: `fetch_top_coins(1, 50)` with gainers/losers processing
**Output**: `3_output.html` + `3_output.jpg`

```bash
cd scripts/main/individual_posts
python generate_3_output.py
```

### Template 4: Trading Opportunities
**File**: `generate_4_output.py`
**Description**: Generates trading opportunities and signals
**Data Source**: `fetch_trading_opportunities()`
**Output**: `4_output.html` + `4_output.jpg`

```bash
cd scripts/main/individual_posts
python generate_4_output.py
```

### Template 5: Market Overview
**File**: `generate_5_output.py`
**Description**: Generates global market overview with BTC snapshot
**Data Source**: `fetch_global_market_data()` + `fetch_btc_snapshot()`
**Output**: `5_output.html` + `5_output.jpg`

```bash
cd scripts/main/individual_posts
python generate_5_output.py
```

### Template 6: Bitcoin Snapshot with Macro Intelligence
**File**: `generate_6_output.py`
**Description**: Generates Bitcoin snapshot with strategic crypto news
**Data Source**: `fetch_btc_snapshot()` + AI-generated macro intelligence
**Output**: `6_output.html` + `6_output.jpg`

```bash
cd scripts/main/individual_posts
python generate_6_output.py
```

### Template 7: Market Intelligence (L2 AI Filtered)
**File**: `generate_7_output.py`
**Description**: Generates market intelligence with L2 AI filtering system
**Data Source**: L1 AI web search + L2 AI quality validation
**Output**: `7_output.html` + `7_output.jpg`

```bash
cd scripts/main/individual_posts
python generate_7_output.py
```

## Features

### Automatic Screenshot Generation
All individual generators include automatic screenshot generation using Playwright:
- **HTML Output**: Generated in `output_html/` directory
- **Image Output**: Generated in `output_images/` directory as JPG files
- **Instagram Ready**: 1080x1080 aspect ratio optimized for social media

### Error Handling
Each script includes comprehensive error handling:
- Database connection failures
- Template rendering errors
- Screenshot generation failures
- Proper cleanup and connection closing

### Standalone Execution
Each script can be run independently:
- No dependencies on other templates
- Self-contained data fetching
- Individual success/failure reporting

## Usage Patterns

### Single Template Generation
Generate a specific template when you need just one post:
```bash
python generate_7_output.py  # Latest Market Intelligence
```

### Batch Generation
Generate multiple templates in sequence:
```bash
# Generate market overview templates
python generate_5_output.py
python generate_6_output.py
python generate_7_output.py
```

### Development and Testing
Use individual generators for:
- **Template Development**: Test specific template changes
- **Data Validation**: Verify database connections and data quality
- **Design Iteration**: Quick preview of styling changes
- **Content Testing**: Validate AI content generation

## Dependencies

All generators require the following modules from the parent directory:
- `data.database` - Database operations and data fetching
- `content.template_engine` - Jinja2 template rendering
- `media.screenshot` - Playwright HTML-to-image conversion
- `content.openrouter_client` - AI content generation (Templates 6 & 7)

## Output Structure

```
output_html/
├── 1_output.html     # Top Cryptocurrencies
├── 2_output.html     # Extended Cryptocurrencies
├── 3_output.html     # Top Gainers and Losers
├── 4_output.html     # Trading Opportunities
├── 5_output.html     # Market Overview
├── 6_output.html     # Bitcoin + Macro Intelligence
└── 7_output.html     # Market Intelligence (L2 AI)

output_images/
├── 1_output.jpg      # Instagram-ready screenshots
├── 2_output.jpg
├── 3_output.jpg
├── 4_output.jpg
├── 5_output.jpg
├── 6_output.jpg
└── 7_output.jpg
```

## Adding New Templates

To add a new template generator:

1. **Create Generator File**: `generate_X_output.py`
2. **Follow Template Structure**:
   ```python
   #!/usr/bin/env python3
   """
   Generate X_output.html - [Template Description]
   Individual post generator for Template X
   """

   import os
   import sys
   import asyncio

   # Add imports and database operations

   def generate_X_output():
       """Generate Template X: [Description]"""
       # Implementation here

   async def generate_X_with_screenshot():
       """Generate Template X with screenshot"""
       # HTML + Screenshot generation

   if __name__ == "__main__":
       result = asyncio.run(generate_X_with_screenshot())
       # Success/failure handling
   ```

3. **Update This Documentation**: Add template description and usage examples
4. **Test Integration**: Verify template works with existing pipeline

## Performance Notes

- **Database Connections**: Each generator manages its own database connection lifecycle
- **Memory Usage**: Individual generators use less memory than full pipeline
- **Execution Time**: Varies by template complexity (1-10 seconds typical)
- **API Usage**: Templates 6 & 7 consume OpenRouter API credits

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Verify `.env` file and database credentials
2. **Template Rendering Failures**: Check `base_templates/` directory exists
3. **Screenshot Generation Errors**: Ensure Playwright is properly installed
4. **Missing Dependencies**: Run from correct directory with proper Python path

### Debug Mode
Add debug logging by modifying the print statements in individual generators:
```python
print("🔍 Debug: Data fetched successfully")
print(f"📊 Debug: Generated {len(data)} records")
```

### File Permissions
Ensure write permissions for output directories:
```bash
chmod -R 755 output_html/ output_images/
```

---

**Note**: This individual post system complements the main Instagram pipeline (`workflows/instagram_pipeline.py`) and provides granular control for content generation and testing.