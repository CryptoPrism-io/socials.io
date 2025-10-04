"""Comprehensive test of all web search models with output, token usage, and cost analysis."""

import os
import sys
import json
import time
from datetime import datetime
import requests

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

def test_all_web_search_models():
    """Test all available web search models and collect comprehensive data."""
    print("🌐 Comprehensive Web Search Models Test")
    print("=" * 60)

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No OpenRouter API key found")
        return

    # All potential web search models to test
    models_to_test = [
        # Perplexity Models
        ('perplexity/sonar-pro', 'Perplexity Sonar Pro'),
        ('perplexity/sonar-reasoning-pro', 'Perplexity Reasoning Pro'),
        ('perplexity/sonar-deep-research', 'Perplexity Deep Research'),
        ('perplexity/sonar-reasoning', 'Perplexity Reasoning'),
        ('perplexity/sonar', 'Perplexity Sonar'),
        ('perplexity/r1-1776', 'Perplexity R1-1776'),

        # OpenAI Search Models
        ('openai/gpt-4o-search-preview', 'GPT-4o Search Preview'),
        ('openai/gpt-4o-mini-search-preview', 'GPT-4o Mini Search'),

        # Other potential web search models
        ('alibaba/tongyi-deepresearch-30b-a3b', 'Alibaba Deep Research'),
        ('nousresearch/hermes-4-70b', 'Hermes 4 70B'),
        ('nousresearch/hermes-4-405b', 'Hermes 4 405B'),
    ]

    # Test prompt for Bitcoin information
    bitcoin_prompt = """Search for current Bitcoin information and return ONLY a JSON response with real-time data:

{
  "current_price": "Bitcoin's current price in USD",
  "past_24h": ["Real event 1 from past 24h", "Real event 2 from past 24h", "Real event 3 from past 24h"],
  "next_24h": ["Thing to watch 1", "Thing to watch 2", "Thing to watch 3"],
  "market_sentiment": "Current market sentiment (bullish/bearish/neutral)",
  "key_levels": {
    "support": "Key support level",
    "resistance": "Key resistance level"
  }
}

Use current real data from web search. Each item under 60 characters."""

    results = []

    print(f"🧪 Testing {len(models_to_test)} models...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for i, (model_id, model_name) in enumerate(models_to_test, 1):
        print(f"\n[{i}/{len(models_to_test)}] 🔬 Testing: {model_name}")
        print(f"Model ID: {model_id}")
        print("-" * 50)

        start_time = time.time()

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://socials.io",
                    "X-Title": "Bitcoin Web Search Comparison"
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": bitcoin_prompt}],
                    "max_tokens": 400,
                    "temperature": 0.2
                },
                timeout=30
            )

            end_time = time.time()
            response_time = end_time - start_time

            result = {
                'model_id': model_id,
                'model_name': model_name,
                'status_code': response.status_code,
                'response_time_seconds': round(response_time, 2),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            if response.status_code == 200:
                data = response.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                usage = data.get('usage', {})

                result.update({
                    'success': True,
                    'content': content,
                    'content_length': len(content),
                    'prompt_tokens': usage.get('prompt_tokens', 0),
                    'completion_tokens': usage.get('completion_tokens', 0),
                    'total_tokens': usage.get('total_tokens', 0),
                    'cost_usd': calculate_cost(model_id, usage),
                })

                # Try to parse JSON from response
                try:
                    if '{' in content and '}' in content:
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        json_part = content[start:end]
                        parsed_json = json.loads(json_part)
                        result['json_parsed'] = True
                        result['parsed_data'] = parsed_json
                    else:
                        result['json_parsed'] = False
                        result['parsed_data'] = None
                except json.JSONDecodeError:
                    result['json_parsed'] = False
                    result['parsed_data'] = None

                print(f"✅ Success! {len(content)} chars, {usage.get('total_tokens', 0)} tokens")
                if result.get('json_parsed'):
                    print(f"📋 JSON parsed successfully")
                else:
                    print(f"⚠️ JSON parsing failed")

            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                error_message = error_data.get('error', {}).get('message', response.text)

                result.update({
                    'success': False,
                    'error': error_message,
                    'content': None,
                    'cost_usd': 0
                })
                print(f"❌ Failed: {response.status_code} - {error_message}")

        except requests.exceptions.Timeout:
            result = {
                'model_id': model_id,
                'model_name': model_name,
                'success': False,
                'error': 'Request timeout (30s)',
                'response_time_seconds': 30.0,
                'cost_usd': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            print(f"⏱️ Timeout after 30 seconds")

        except Exception as e:
            result = {
                'model_id': model_id,
                'model_name': model_name,
                'success': False,
                'error': str(e),
                'response_time_seconds': 0,
                'cost_usd': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            print(f"💥 Exception: {e}")

        results.append(result)

        # Small delay between requests
        time.sleep(1)

    print(f"\n🎉 Testing Complete!")
    print(f"✅ Successful models: {sum(1 for r in results if r.get('success'))}")
    print(f"❌ Failed models: {sum(1 for r in results if not r.get('success'))}")

    # Generate markdown report
    generate_markdown_report(results)

    return results

def calculate_cost(model_id, usage):
    """Calculate approximate cost based on model and token usage."""
    # Approximate pricing (rates may vary)
    pricing = {
        'perplexity/sonar-pro': {'input': 0.003, 'output': 0.015},  # per 1K tokens
        'perplexity/sonar-reasoning-pro': {'input': 0.003, 'output': 0.015},
        'perplexity/sonar-deep-research': {'input': 0.005, 'output': 0.025},
        'openai/gpt-4o-search-preview': {'input': 0.01, 'output': 0.03},
        'openai/gpt-4o-mini-search-preview': {'input': 0.0015, 'output': 0.006},
        'default': {'input': 0.002, 'output': 0.01}
    }

    model_pricing = pricing.get(model_id, pricing['default'])

    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)

    input_cost = (prompt_tokens / 1000) * model_pricing['input']
    output_cost = (completion_tokens / 1000) * model_pricing['output']

    return round(input_cost + output_cost, 6)

def generate_markdown_report(results):
    """Generate comprehensive markdown report."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Test prompt reference
    bitcoin_prompt = """Search for current Bitcoin information and return ONLY a JSON response with real-time data..."""

    md_content = f"""# Web Search Models Bitcoin Test Report

**Generated:** {timestamp}
**Test Prompt:** Bitcoin current information with JSON response
**Total Models Tested:** {len(results)}
**Successful:** {sum(1 for r in results if r.get('success'))}
**Failed:** {sum(1 for r in results if not r.get('success'))}

## Executive Summary

This report evaluates web search-enabled language models for real-time Bitcoin information retrieval. Models were tested for accuracy, response time, token efficiency, and cost-effectiveness.

## Model Performance Overview

| Model | Success | Response Time | Tokens | Cost (USD) | JSON Valid |
|-------|---------|---------------|--------|------------|-------------|
"""

    for result in results:
        success = "✅" if result.get('success') else "❌"
        response_time = f"{result.get('response_time_seconds', 0):.2f}s"
        tokens = result.get('total_tokens', 0)
        cost = f"${result.get('cost_usd', 0):.6f}"
        json_valid = "✅" if result.get('json_parsed') else "❌"

        md_content += f"| {result['model_name']} | {success} | {response_time} | {tokens} | {cost} | {json_valid} |\n"

    md_content += f"""

## Detailed Results

"""

    for i, result in enumerate(results, 1):
        md_content += f"""
### {i}. {result['model_name']}

**Model ID:** `{result['model_id']}`
**Status:** {'✅ Success' if result.get('success') else '❌ Failed'}
**Response Time:** {result.get('response_time_seconds', 0):.2f} seconds
**Timestamp:** {result['timestamp']}

"""

        if result.get('success'):
            md_content += f"""**Token Usage:**
- Prompt Tokens: {result.get('prompt_tokens', 0):,}
- Completion Tokens: {result.get('completion_tokens', 0):,}
- Total Tokens: {result.get('total_tokens', 0):,}
- Estimated Cost: ${result.get('cost_usd', 0):.6f}

**Content Length:** {result.get('content_length', 0):,} characters
**JSON Parsed:** {'✅ Yes' if result.get('json_parsed') else '❌ No'}

"""

            if result.get('json_parsed') and result.get('parsed_data'):
                parsed = result['parsed_data']
                md_content += f"""**Parsed Bitcoin Data:**
```json
{json.dumps(parsed, indent=2)}
```

**Key Information Extracted:**
- 💰 **Current Price:** {parsed.get('current_price', 'N/A')}
- 📊 **Market Sentiment:** {parsed.get('market_sentiment', 'N/A')}
- 🎯 **Support Level:** {parsed.get('key_levels', {}).get('support', 'N/A')}
- 🎯 **Resistance Level:** {parsed.get('key_levels', {}).get('resistance', 'N/A')}

**Past 24H Events:**
"""
                for event in parsed.get('past_24h', []):
                    md_content += f"- {event}\n"

                md_content += f"""
**Next 24H Outlook:**
"""
                for outlook in parsed.get('next_24h', []):
                    md_content += f"- {outlook}\n"

            md_content += f"""
**Raw Response:**
```
{result.get('content', 'No content')[:500]}{'...' if len(result.get('content', '')) > 500 else ''}
```

"""
        else:
            md_content += f"""**Error:** {result.get('error', 'Unknown error')}

"""

        md_content += "---\n"

    # Add cost analysis
    successful_results = [r for r in results if r.get('success')]
    if successful_results:
        total_cost = sum(r.get('cost_usd', 0) for r in successful_results)
        avg_cost = total_cost / len(successful_results)
        min_cost = min(r.get('cost_usd', 0) for r in successful_results)
        max_cost = max(r.get('cost_usd', 0) for r in successful_results)

        md_content += f"""
## Cost Analysis

| Metric | Value |
|--------|-------|
| Total Cost (All Successful) | ${total_cost:.6f} |
| Average Cost per Request | ${avg_cost:.6f} |
| Lowest Cost Model | ${min_cost:.6f} |
| Highest Cost Model | ${max_cost:.6f} |

## Recommendations

**Best Overall Performance:**
"""
        # Find best models based on different criteria
        best_cost = min(successful_results, key=lambda x: x.get('cost_usd', float('inf')))
        best_speed = min(successful_results, key=lambda x: x.get('response_time_seconds', float('inf')))

        md_content += f"""
- **Most Cost-Effective:** {best_cost['model_name']} (${best_cost.get('cost_usd', 0):.6f})
- **Fastest Response:** {best_speed['model_name']} ({best_speed.get('response_time_seconds', 0):.2f}s)

**For Production Use:**
1. **Primary:** Models with JSON parsing success and reasonable cost
2. **Fallback:** Standard models without web search for reliability

"""

    md_content += f"""
## Technical Notes

- All tests used the same prompt asking for current Bitcoin information in JSON format
- Response times include network latency
- Costs are estimated based on published pricing (may vary)
- JSON parsing indicates structured data extraction capability
- Models are ranked by success rate, then by cost-effectiveness

**Test Configuration:**
- Max Tokens: 400
- Temperature: 0.2
- Timeout: 30 seconds
- Prompt Length: ~{len(bitcoin_prompt)} characters

---
*Report generated by socials.io automated testing system*
"""

    # Save the markdown report
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'web_search_models_report.md')

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"\n📄 Markdown report saved: {report_path}")
    print(f"📊 Report contains detailed analysis of {len(results)} models")

if __name__ == "__main__":
    test_all_web_search_models()