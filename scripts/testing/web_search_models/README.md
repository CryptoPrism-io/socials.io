# Web Search Models Testing

This directory contains testing tools for web search-enabled language models.

## Directory Structure

### `web_search_models/`
- `test_all_models.py` - Comprehensive test of all available web search models
- `test_final_search.py` - Final validation test for production models
- `test_primary_model.py` - Test specifically for our primary web search model
- `web_search_models_report.md` - **📊 Complete analysis report** of all tested models

### `root/`
- `test_working_web_search.py` - Test verified working models
- `test_hybrid_workflow.py` - Complete workflow test (web search + caption generation)

## Primary Model

**GPT-4o Mini Search Preview** (`openai/gpt-4o-mini-search-preview`)
- Most cost-effective web search model ($0.001224 per request)
- Reliable JSON response formatting
- Fast response times (2-4 seconds average)
- Primary choice for all project web search needs

## Usage

```bash
# Test primary model
python scripts/testing/web_search_models/test_primary_model.py

# Test all available models
python scripts/testing/web_search_models/test_all_models.py

# Run final validation
python scripts/testing/web_search_models/test_final_search.py
```

## Architecture

- **Web Search**: GPT-4o Mini Search (real-time data)
- **Caption Generation**: Claude Sonnet (creative content)
- **Fallback**: Standard AI models for reliability