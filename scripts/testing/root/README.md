# Root Testing Directory

This directory contains core testing scripts that validate the fundamental functionality of the social media automation platform.

## Files

### `test_working_web_search.py`
- Tests verified working web search models
- Validates Bitcoin data retrieval
- Direct API testing for model availability

### `test_hybrid_workflow.py`
- Complete end-to-end workflow test
- Web search (GPT-4o Mini Search) + Caption generation (Claude Sonnet)
- Cost analysis and performance metrics

## Usage

```bash
# Test working web search models
python scripts/testing/root/test_working_web_search.py

# Test complete hybrid workflow
python scripts/testing/root/test_hybrid_workflow.py
```

## Architecture Validation

These tests ensure:
- ✅ Web search models are accessible and working
- ✅ Real-time Bitcoin data retrieval
- ✅ Caption generation with Claude Sonnet
- ✅ Cost-effective operations
- ✅ Instagram-ready output formatting

## Dependencies

Requires:
- OpenRouter API key set in environment
- Active internet connection for web search
- Python packages: requests, json