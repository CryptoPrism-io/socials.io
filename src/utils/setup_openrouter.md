# OpenRouter API Setup Guide

## 1. Get OpenRouter API Key

1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for an account
3. Navigate to the API Keys section
4. Generate a new API key
5. Copy the key (starts with `sk-or-v1-...`)

## 2. Set Environment Variable

### Windows:
```bash
set OPENROUTER_API_KEY=your_api_key_here
```

### Linux/Mac:
```bash
export OPENROUTER_API_KEY=your_api_key_here
```

### Or create a `.env` file:
```
OPENROUTER_API_KEY=your_api_key_here
```

## 3. Install Dependencies

```bash
pip install requests python-dotenv
```

## 4. Models Available

The analyzer is configured to use:
- **Primary**: `perplexity/llama-3.1-sonar-large-128k-online` (Web access + excellent analysis)
- **Alternatives**:
  - `openai/gpt-4-turbo-preview` (Good analysis, no web access)
  - `anthropic/claude-3-sonnet` (Excellent analysis)
  - `meta-llama/llama-3.1-405b-instruct` (Very capable)

## 5. Usage in Code

```python
from src.utils.openrouter_analyzer import OpenRouterAnalyzer

# Initialize analyzer
analyzer = OpenRouterAnalyzer()

# Get analysis for current BTC price
btc_price = 117301.67
analysis = analyzer.get_market_analysis(btc_price)

# Generate HTML structure
html_content = analyzer.generate_html_structure(analysis)
```

## 6. Cost Estimation

- Perplexity Sonar: ~$0.001-0.002 per request
- GPT-4: ~$0.01-0.03 per request
- Claude-3: ~$0.008-0.015 per request

For daily Instagram posts: ~$0.30-0.90 per month

## 7. Fallback Behavior

If API key is not set or request fails:
- Uses intelligent fallback analysis
- Still generates proper HTML structure
- No errors or breaking changes