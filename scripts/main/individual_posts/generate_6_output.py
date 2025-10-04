#!/usr/bin/env python3
"""
Generate 6_output.html using macro intelligence alerts
Combines real-time strategic crypto news with BTC snapshot data
"""

import os
import sys
import json
import re
import asyncio
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import create_engine

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from content.openrouter_client import create_openrouter_client

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
    print("✅ Environment variables loaded in generate_6_output.py")
except ImportError:
    print("⚠️ dotenv not available, using system environment variables")

# Database configuration
DB_CONFIG = {
    'host': '34.55.195.199',        # GCP PostgreSQL instance public IP
    'database': 'dbcp',             # Database name
    'user': 'yogass09',             # Username
    'password': 'jaimaakamakhya',   # Password
    'port': 5432                    # PostgreSQL default port
}

def get_gcp_engine():
    """Create and return a SQLAlchemy engine for the GCP PostgreSQL database."""
    connection_url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@" \
                     f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(connection_url)

# Initialize the GCP engine
gcp_engine = get_gcp_engine()

def convert_macro_report_to_json_python_parsing(macro_report_text):
    """
    Convert using Python regex parsing instead of LLM
    More reliable and cost-effective for structured conversion

    Args:
        macro_report_text: String containing the detailed macro report

    Returns:
        Dict: {'success': True, 'alerts': [...]} on success
              {'success': False, 'error': 'error message'} on failure
    """
    try:
        alerts = []

        # Check for "NO QUALIFYING STRATEGIC DEVELOPMENTS" message
        if re.search(r'NO QUALIFYING STRATEGIC DEVELOPMENTS', macro_report_text, re.IGNORECASE):
            return {
                'success': False,
                'error': 'No qualifying strategic developments found in last 24 hours'
            }

        # Extract individual developments using regex
        development_pattern = r'(\d+)\. \*\*(Regulatory Update|Institutional Alert|FOMC Alert|News Alert|Technological Alert|Environmental Alert|Legal Alert|Adoption Alert)\*\*.*?\n.*?-\s+\*\*Development:\*\*(.*?)\n.*?-\s+\*\*Coins/Tokens Affected:\*\*(.*?)\n.*?-\s+\*\*Impact Level:\*\*(.*?)\n.*?-\s+\*\*Market Sentiment:\*\*(.*?)\n.*?-\s+\*\*Strategic Impact:\*\*(.*?)\n.*?-\s+\*\*Post Highlight Potential:\*\*(.*?)\n.*?-\s+\*\*Source:\*\*(.*?)(?=\n\n|\n\d+\.|$)'

        matches = re.finditer(development_pattern, macro_report_text, re.DOTALL)

        for match in matches:
            try:
                category = match.group(2)
                development_text = match.group(3).strip()
                coins_affected_text = match.group(4).strip()
                impact_level_text = match.group(5).strip().split()[0] if len(match.group(5).strip().split()) > 0 else 'Medium'
                sentiment_text = match.group(6).strip().split()[0] if len(match.group(6).strip().split()) > 0 else 'Neutral'
                strategic_impact = match.group(7).strip()
                highlight_potential_text = match.group(8).strip().split()[0] if len(match.group(8).strip().split()) > 0 else 'Medium'
                source_text = match.group(9).strip()

                # Parse coins affected (extract coin symbols)
                coin_symbols = []
                coin_pattern = r'\b(BTC|ETH|SOL|ADA|DOT|MATIC|LINK|AVAX|USDT|USDC|BUSD|BNB|LTC|UNI|AAVE|COMP|MKR|YFI|BAT|ZRX|REP|SNT|OMG|STORJ|BNT|ANT|GNT|STORM|DENT|FUN|KIN|MANA|NMR|ELE|ETC|BSV|BCH|XRP|EOS|TRX|NEO|VEN|LRC|KNC|XEM|DASH|BTG|ZEC|PIVX|ARK|WAVES|STRAT|MCO|HSR|ARK|EOSDAC|EOSN|MEETONE|ACOIN|XYO|REN|BAL|CRV|YFI|REN|NXM|RAM|BADGER|PNT|LDO|AURA|FXS|CNC|CRO|FTT|HT|OKB|PAX|HUSD|TUSD|USDC|BUSD|HUSD|PAX|GUSD|USDP|USDT|BTT|WIN|MX|BIDR|RUB|TRY|EUR|ZAR|NGN|VND|IDR|PHP|KRW|MYR|SGD|AUD|ARS|BRL|CLP|COP|MXN|PEN|UYU|CTS|DAI)\b'
                coin_matches = re.findall(coin_pattern, coins_affected_text.upper())
                coin_symbols = list(set(coin_matches)) if coin_matches else ['BTC']  # Default to BTC if none found

                # Create clean description (first 120 characters)
                description = development_text[:120].strip()

                # Map category to tag
                tag_mapping = {
                    'Regulatory Update': 'Regulatory Alert',
                    'Institutional Alert': 'Institutional Alert',
                    'FOMC Alert': 'FOMC Alert',
                    'News Alert': 'News Alert',
                    'Technological Alert': 'Technological Alert',
                    'Environmental Alert': 'Environmental Alert',
                    'Legal Alert': 'Legal Alert',
                    'Adoption Alert': 'Adoption Alert'
                }

                tag = tag_mapping.get(category, 'News Alert')

                alert = {
                    "category": category,
                    "description": description,
                    "tag": tag,
                    "source": source_text,
                    "coins_affected": coin_symbols,
                    "coin_name": coin_symbols[0] if coin_symbols else 'BTC',
                    "impact_level": impact_level_text,
                    "sentiment": sentiment_text,
                    "highlight_potential": highlight_potential_text
                }

                alerts.append(alert)

            except Exception as e:
                print(f"Warning: Failed to parse development {match.group(1)}: {e}")
                continue

        if len(alerts) == 0:
            return {
                'success': False,
                'error': 'No developments found in macro report'
            }

        print(f"✅ Python-parsed {len(alerts)} alerts from macro report")
        return {
            'success': True,
            'alerts': alerts
        }

    except Exception as e:
        error_message = f"Python parsing conversion error: {str(e)}"
        print(f"❌ {error_message}")
        return {
            'success': False,
            'error': error_message
        }

def generate_macro_intelligence_with_json_conversion():
    """
    Two-step macro intelligence generation:
    1. Generate rich macro report using GPT-4o Mini Search Preview
    2. Convert to JSON format using Python parsing (more reliable)
    """
    try:
        client = create_openrouter_client()

        # Step 1: Generate macro report
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        today_str = today.strftime("%Y-%m-%d")
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        today_display = today.strftime("September %d, %Y")
        date_range = f"{yesterday.strftime('September %d')}–{today.strftime('%d, %Y')}"

        macro_prompt = f"""You are a senior crypto market intelligence analyst.
Your task: Search the web for **Bitcoin, Ethereum, and major cryptocurrency news from TODAY'S DATE: {today_display}.**

✅ Focus only on **{date_range}** (last 24 hours). Ignore older news.
✅ We are NOT interested in price % moves or technical levels.
✅ Instead, focus on **macro, regulatory, institutional, and strategic developments** (PESTEL framework):
- Political/regulatory actions (laws, bans, approvals, Fed/FOMC, SEC decisions)
- Economic/macroeconomic signals (inflation, monetary policy, ETF approvals, central bank actions)
- Social trends (mass adoption, sentiment shifts, new user demographics)
- Technological developments (major protocol upgrades, security issues, acquisitions)
- Environmental/legal factors (energy usage rules, lawsuits, ESG compliance)
- Large-scale institutional moves (M&A, new product launches, corporate investments, fund flows)

✅ **PRIORITY**: Prioritize events with named institutions (e.g., BlackRock, Fidelity, Coinbase, Binance, SEC, Federal Reserve, JPMorgan, Goldman Sachs, MicroStrategy, Tesla, PayPal, Visa, Mastercard).

Create a detailed market intelligence report covering the TOP 10 most important macro/strategic developments from the last 24 hours:

**CRYPTO MACRO INTELLIGENCE REPORT**
**Date: {today_display}**

**EXECUTIVE SUMMARY:**
[Brief overview of key macro/strategic developments and implications]

**TOP STRATEGIC DEVELOPMENTS:**

1. **[CATEGORY]** - [Date: {yesterday.strftime('%b %d, %Y')}]
   - **Development:** [Detailed description of regulatory/institutional/macro event]
   - **Coins/Tokens Affected:** [List specific cryptocurrencies impacted - BTC, ETH, SOL, etc.]
   - **Impact Level:** [High/Medium/Low - based on potential market effect]
   - **Market Sentiment:** [Bullish/Bearish/Neutral - how this affects market sentiment]
   - **Strategic Impact:** [Long-term implications for crypto adoption/regulation]
   - **Post Highlight Potential:** [High/Medium/Low - how newsworthy for social posts]
   - **Source:** [News source website]

2. **[CATEGORY]** - [Date: {yesterday.strftime('%b %d, %Y')}]
   - **Development:** [Detailed description]
   - **Coins/Tokens Affected:** [List specific cryptocurrencies impacted]
   - **Impact Level:** [High/Medium/Low]
   - **Market Sentiment:** [Bullish/Bearish/Neutral]
   - **Strategic Impact:** [Long-term implications]
   - **Post Highlight Potential:** [High/Medium/Low]
   - **Source:** [News source website]

[Continue for all 10 developments]

**REGULATORY LANDSCAPE ANALYSIS:**
[Overview of regulatory developments and policy implications]

**INSTITUTIONAL ADOPTION TRENDS:**
[Analysis of institutional moves and corporate adoption]

**STRATEGIC OUTLOOK:**
[Forward-looking analysis based on today's developments]

**COIN IMPACT SUMMARY:**
[Summary table of which coins/tokens were most affected by today's developments]

**POST HIGHLIGHT RECOMMENDATIONS:**
[List of top 3-5 news items with "High" post highlight potential for social media content]

**Categories to focus on**: Regulatory Update, Institutional Alert, FOMC Alert, News Alert, Technological Alert, Environmental Alert, Legal Alert, Adoption Alert

**REQUIRED FIELDS FOR EACH DEVELOPMENT:**
- **Coins/Tokens Affected**: Always specify which cryptocurrencies are directly impacted (BTC, ETH, SOL, USDT, USDC, ADA, DOT, MATIC, etc.)
- **Impact Level**: Rate High/Medium/Low based on potential price/adoption effect
- **Market Sentiment**: Rate Bullish/Bearish/Neutral based on how this news affects overall market sentiment
- **Post Highlight Potential**: Rate High/Medium/Low based on social media engagement potential

**CRITICAL**: If you cannot find real macro/strategic news from {date_range}, clearly state "NO QUALIFYING STRATEGIC DEVELOPMENTS FOUND IN LAST 24 HOURS" instead of making up information. Only report ACTUAL current strategic events with proper date stamps."""

        print("🔍 Step 1: Generating rich macro intelligence report...")
        macro_result = client.chat_completion(
            prompt=macro_prompt,
            model='openai/gpt-4o-mini-search-preview',
            max_tokens=6500,
            temperature=0.3
        )

        if not macro_result['success']:
            return {
                'success': False,
                'error': f"Macro report generation failed: {macro_result.get('error', 'Unknown error')}"
            }

        macro_report = macro_result['content']
        print(f"📄 Generated macro report: {len(macro_report)} characters")

        # Step 2: Convert to JSON using Python parsing (more reliable than LLM)
        print("🔄 Step 2: Converting to JSON format using Python parsing...")
        json_result = convert_macro_report_to_json_python_parsing(macro_report)

        if json_result['success']:
            return json_result
        else:
            return {
                'success': False,
                'error': json_result.get('error', 'Unknown conversion error')
            }

    except Exception as e:
        error_message = f"Macro intelligence generation error: {str(e)}"
        print(f"❌ {error_message}")
        return {
            'success': False,
            'error': error_message
        }

def get_btc_snapshot_data():
    """
    Get BTC snapshot data for the template
    For now using placeholder data - in production this would be real API calls
    """
    return [
        {
            'logo': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiNGOUE4RDQiLz4KPHA+OZ8=</PA==',
            'price': '112,957',
            'market_cap': '2.2T',
            'volume24h': '45.1B',
            'percent_change24h': '+1.84',
            'percent_change7d': '+8.92',
            'percent_change30d': '+12.34',
            'bearish': '23',
            'neutral': '45',
            'bullish': '32',
            'Trend': 'Bullish'
        }
    ]

def generate_6_output_html():
    """
    Generate 6_output.html using macro intelligence alerts
    """
    try:
        print("🚀 Generating 6_output.html with macro intelligence...")

        # Step 1: Get macro intelligence alerts
        print("🔍 Generating macro intelligence alerts...")
        alerts_result = generate_macro_intelligence_with_json_conversion()

        # Step 2: Get BTC snapshot data from database
        from data.database import fetch_btc_snapshot
        btc_data_df = fetch_btc_snapshot()
        if not btc_data_df.empty:
            btc_snapshots = btc_data_df.to_dict('records')
            # Add fear_greed_history from DataFrame column to the first record
            if len(btc_snapshots) > 0:
                if 'fear_greed_history_json' in btc_snapshots[0] and btc_snapshots[0]['fear_greed_history_json']:
                    # Parse the JSON string back to list
                    import ast
                    try:
                        btc_snapshots[0]['fear_greed_history'] = ast.literal_eval(btc_snapshots[0]['fear_greed_history_json'])
                    except:
                        # Fallback in case of parsing error
                        btc_snapshots[0]['fear_greed_history'] = [
                            {'day': i+1, 'value': 50, 'price': 0, 'label': 'Neutral'} for i in range(30)
                        ]
                else:
                    # Fallback: create basic history if not available
                    btc_snapshots[0]['fear_greed_history'] = [
                        {'day': i+1, 'value': 50, 'price': 0, 'label': 'Neutral'} for i in range(30)
                    ]
                print(f"🔍 Debug: fear_greed_history has {len(btc_snapshots[0]['fear_greed_history'])} entries")
            # Normalize numeric strings by stripping leading '$'
            for snap in btc_snapshots:
                for _k in ('price', 'market_cap', 'volume24h'):
                    snap[_k] = snap[_k].lstrip('$')
        else:
            btc_snapshots = []

        # Step 3: Prepare template data
        current_time = datetime.now()

        template_data = {
            'current_date': current_time.strftime('%d %b, %Y'),
            'current_time': current_time.strftime('%I:%M:%S %p'),
            'news_events': alerts_result,
            'snap': btc_snapshots
        }

        print(f"📊 Template data prepared:")
        print(f"   - Macro alerts: {len(alerts_result['alerts']) if alerts_result['success'] else 0}")
        print(f"   - BTC snapshots: {len(btc_snapshots)}")
        print(f"   - Current timestamp: {template_data['current_date']} {template_data['current_time']}")

        # Step 4: Setup Jinja2 template
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'base_templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('6.html')

        # Step 5: Render HTML
        rendered_html = template.render(**template_data)

        # Step 6: Save to 6_output.html
        output_html_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html', '6_output.html')

        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)

        print(f"✅ Successfully generated: {output_html_path}")
        print(f"📄 HTML file size: {len(rendered_html)} characters")

        # Step 7: Also copy the CSS file if it doesn't exist
        import shutil
        css_source = os.path.join(template_dir, 'style6.css')
        css_dest = os.path.join(os.path.dirname(output_html_path), 'style6.css')

        if not os.path.exists(css_dest):
            if os.path.exists(css_source):
                shutil.copy2(css_source, css_dest)
                print("📁 Copied style6.css to output_html directory")

        return {
            'success': True,
            'html_path': output_html_path,
            'alerts_count': len(alerts_result['alerts']) if alerts_result['success'] else 0,
            'data': template_data
        }

    except Exception as e:
        error_msg = f"6_output generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

async def generate_6_with_screenshot():
    """Generate Template 6 with screenshot"""
    print("📸 Generating Template 6 with screenshot...")

    # Generate HTML
    result = generate_6_output_html()
    if not result['success']:
        return False

    # Generate screenshot
    try:
        from media.screenshot import generate_image_from_html

        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
        output_path = os.path.join(output_dir, "6_output.html")
        image_path = os.path.join(image_dir, "6_output.jpg")

        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 6 screenshot generated: {image_path}")
        return True

    except Exception as e:
        print(f"❌ Template 6 screenshot error: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio

    # Run with screenshot generation
    result = asyncio.run(generate_6_with_screenshot())

    if result:
        print("🎉 Template 6 generation completed successfully!")
    else:
        print("💥 Template 6 generation failed!")
        sys.exit(1)