"""Real-time crypto news generation using web search only - NO FALLBACKS."""

import os
import json
import re
from .openrouter_client import create_openrouter_client

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
    print("✅ Environment variables loaded in ai_generation_news.py")
except ImportError:
    print("⚠️ dotenv not available, using system environment variables")

def convert_macro_report_to_json(macro_report_text):
    """
    Convert rich macro intelligence report text to standardized JSON format.

    Args:
        macro_report_text: String containing the detailed macro report

    Returns:
        Dict: {'success': True, 'alerts': [...]} on success
              {'success': False, 'error': 'error message'} on failure
    """
    try:
        client = create_openrouter_client()

        json_conversion_prompt = f"""You are a data processing specialist. Convert this detailed crypto macro intelligence report into a standardized JSON format.

REPORT TO CONVERT:
{macro_report_text[:4000]}... [truncated if necessary]

INSTRUCTIONS:
1. Identify all strategic developments from the report
2. Extract key information: category, development details, coins affected, source, impact levels
3. Convert each development into a standardized alert format
4. Prioritize events marked as "High impact" or "High highlight potential"
5. If no qualifying developments exist, return error instead of creating fake alerts

REQUIRED FOR EACH ALERT:
- category: "Regulatory Update", "Institutional Alert", "FOMC Alert", "News Alert", "Technological Alert", "Environmental Alert", "Legal Alert", "Adoption Alert"
- description: 60-120 character clear description
- tag: Exact match to category (e.g., "Regulatory Alert" for "Regulatory Update")
- source: Original source from the report
- coins_affected: Array of abbreviated coin names (e.g., ["BTC"], ["ETH", "SOL"])
- impact_level: "High", "Medium", or "Low"
- highlight_potential: "High", "Medium", or "Low"

JSON FORMAT:
{{
  "alerts": [
    {{
      "category": "Institutional Alert",
      "description": "BlackRock launches Bitcoin ETF with $1B in committed capital",
      "tag": "Institutional Alert",
      "source": "Bloomberg",
      "coins_affected": ["BTC"],
      "impact_level": "High",
      "highlight_potential": "High"
    }}
  ]
}}

Return ONLY valid JSON. If the report contains no actual strategic developments, return:
{{"error": "No qualifying strategic developments found in last 24 hours"}}"""

        print("🔄 Converting rich macro report to JSON format...")
        conversion_result = client.chat_completion(
            prompt=json_conversion_prompt,
            model='openai/gpt-4o-mini',  # Use lightweight model for conversion
            max_tokens=3000,
            temperature=0.1  # Low temperature for consistent formatting
        )

        if not conversion_result['success']:
            return {
                'success': False,
                'error': f"JSON conversion failed: {conversion_result.get('error', 'Unknown error')}"
            }

        converted_json = conversion_result['content']

        # Extract and validate JSON
        try:
            start = converted_json.find('{')
            end = converted_json.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = converted_json[start:end]
                data = json.loads(json_str)

                # Check if it's an error response
                if 'error' in data:
                    return {
                        'success': False,
                        'error': data['error']
                    }

                # Validate structure
                if 'alerts' not in data or not isinstance(data['alerts'], list):
                    raise ValueError("Invalid JSON structure: missing 'alerts' array")

                print(f"✅ Macro report converted to JSON: {len(data['alerts'])} alerts")
                return {
                    'success': True,
                    'alerts': data['alerts']
                }
            else:
                raise ValueError("No valid JSON found in conversion response")

        except (json.JSONDecodeError, ValueError) as e:
            error_message = f"JSON conversion parsing failed: {str(e)}"
            print(f"❌ {error_message}")
            return {
                'success': False,
                'error': error_message
            }

    except Exception as e:
        error_message = f"JSON conversion system error: {str(e)}"
        print(f"❌ {error_message}")
        return {
            'success': False,
            'error': error_message
        }

def generate_crypto_market_news():
    """
    Generate real-time cryptocurrency market news using web search ONLY.

    Returns:
        Dict: {'success': True, 'alerts': [...]} on success
              {'success': False, 'error': 'error message'} on failure

    NO FALLBACKS - If web search fails, returns error instead of fake data.
    """
    try:
        client = create_openrouter_client()

        # Web search prompt for real-time crypto market intelligence
        web_search_prompt = """You are a crypto market intelligence analyst. Search for current cryptocurrency market news, events, and data across ALL major cryptocurrencies (Bitcoin, Ethereum, major altcoins, DeFi, etc.) and generate 8 comprehensive market alerts.

SEARCH FOR REAL-TIME DATA ON:
🔍 Live price movements, technical breakouts/breakdowns across crypto markets
🔍 Institutional activity, large transactions, whale movements
🔍 Regulatory developments, government announcements, policy changes
🔍 FOMC/Fed decisions, monetary policy impacts on crypto
🔍 Exchange news, trading volumes, market sentiment shifts
🔍 DeFi protocol updates, yield changes, TVL movements
🔍 Major project announcements, partnerships, technological developments

✅ **PRIORITY**: Prioritize events with named institutions (e.g., BlackRock, Fidelity, Coinbase, Binance, SEC, Federal Reserve, JPMorgan, Goldman Sachs, MicroStrategy, Tesla, PayPal, Visa, Mastercard).

REQUIRED: Generate exactly 8 market alerts covering different alert types. Each alert MUST include:
- category: Specific market category (e.g., "Price Movement", "Whale Activity", "Regulatory Update")
- description: Detailed 40-80 character description with specific data/numbers
- tag: ONE of these exact tags: "Price Alert", "Technical Alert", "News Alert", "Volume Alert", "Whale Alert", "Institutional Alert", "Regulatory Alert", "FOMC Alert"
- source: Real news source or data provider (e.g., "CoinDesk", "CryptoSlam", "Whale Alert", "Federal Reserve")
- coins_affected: List of specific cryptocurrencies impacted (e.g., ["BTC", "ETH"] or ["SOL", "USDT"])
- impact_level: Rate as "High", "Medium", or "Low" based on potential market effect
- highlight_potential: Rate as "High", "Medium", or "Low" for social media post worthiness

ENSURE DIVERSITY: Include alerts from different cryptocurrencies and market segments. Use CURRENT, FACTUAL data from your web search.

Return ONLY valid JSON in this EXACT format:
{
  "alerts": [
    {
      "category": "Price Movement",
      "description": "Bitcoin breaks above $115,000 resistance level",
      "tag": "Price Alert",
      "source": "CoinMarketCap",
      "coins_affected": ["BTC"],
      "impact_level": "High",
      "highlight_potential": "High"
    },
    {
      "category": "Whale Activity",
      "description": "Large BTC transfer of 2,500 coins to unknown wallet",
      "tag": "Whale Alert",
      "source": "Whale Alert",
      "coins_affected": ["BTC"],
      "impact_level": "Medium",
      "highlight_potential": "Medium"
    }
  ]
}

CRITICAL: Use real-time web search data, include actual numbers/prices, ensure 8 diverse alerts covering different crypto assets and market aspects."""

        # ONLY use GPT-4o Mini Search Preview - NO FALLBACKS
        print("🔍 Fetching real-time crypto market data via GPT-4o Mini Search Preview...")
        result = client.chat_completion(
            prompt=web_search_prompt,
            model='openai/gpt-4o-mini-search-preview',
            max_tokens=4100,
            temperature=0.3
        )

        # If web search fails, return error immediately
        if not result['success']:
            error_message = f"Web search failed: {result.get('error', 'Unknown error')}"
            print(f"❌ {error_message}")
            return {
                'success': False,
                'error': error_message
            }

        ai_response = result['content']
        print(f"📡 Raw web search response received: {len(ai_response)} characters")

        # Extract JSON from response
        try:
            # Find JSON in the response
            start = ai_response.find('{')
            end = ai_response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = ai_response[start:end]
                news_data = json.loads(json_str)

                # Validate structure
                if 'alerts' not in news_data or not isinstance(news_data['alerts'], list):
                    raise ValueError("Invalid JSON structure: missing 'alerts' array")

                if len(news_data['alerts']) == 0:
                    raise ValueError("No alerts generated")

                print(f"✅ Real-time crypto news generated successfully: {len(news_data['alerts'])} alerts")
                return {
                    'success': True,
                    'alerts': news_data['alerts']
                }
            else:
                raise ValueError("No valid JSON found in AI response")

        except (json.JSONDecodeError, ValueError) as e:
            error_message = f"JSON parsing failed: {str(e)}"
            print(f"❌ {error_message}")
            return {
                'success': False,
                'error': error_message
            }

    except Exception as e:
        error_message = f"News generation system error: {str(e)}"
        print(f"❌ {error_message}")
        return {
            'success': False,
            'error': error_message
        }