#!/usr/bin/env python3
"""
Two-step macro intelligence generation with JSON conversion
Combines macro report generation + automatic JSON conversion
"""

import os
import json
import re
from datetime import datetime, timedelta
from sys import path
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'content'))
from openrouter_client import create_openrouter_client

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
    print("✅ Environment variables loaded in generate_macro_news.py")
except ImportError:
    print("⚠️ dotenv not available, using system environment variables")

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

        # Extract individual developments using regex (now includes date extraction)
        development_pattern = r'(\d+)\. \*\*(Regulatory Update|Institutional Alert|FOMC Alert|News Alert|Technological Alert|Environmental Alert|Legal Alert|Adoption Alert)\*\*.*?\n.*?-\s+\*\*Development:\*\*(.*?)\n.*?-\s+\*\*Coins/Tokens Affected:\*\*(.*?)\n.*?-\s+\*\*Impact Level:\*\*(.*?)\n.*?-\s+\*\*Strategic Impact:\*\*(.*?)\n.*?-\s+\*\*Post Highlight Potential:\*\*(.*?)\n.*?-\s+\*\*Source:\*\*(.*?)(?=\n\n|\n\d+\.|$)'

        matches = re.finditer(development_pattern, macro_report_text, re.DOTALL)

        for match in matches:
            try:
                category = match.group(2)
                development_text = match.group(3).strip()
                coins_affected_text = match.group(4).strip()
                impact_level_text = match.group(5).strip().split()[0] if len(match.group(5).strip().split()) > 0 else 'Medium'
                strategic_impact = match.group(6).strip()
                highlight_potential_text = match.group(7).strip().split()[0] if len(match.group(7).strip().split()) > 0 else 'Medium'
                source_text = match.group(8).strip()

                # Parse coins affected (extract coin symbols)
                coin_symbols = []
                coin_pattern = r'\b(BTC|ETH|SOL|ADA|DOT|MATIC|LINK|AVAX|USDT|USDC|BUSD|BNB|LTC|UNI|AAVE|COMP|MKR|YFI|BAT|ZRX|REP|SNT|OMG|STORJ|BNT|ANT|GNT|STORM|DENT|FUN|KIN|MANA|NMR|ELE|ETC|BSV|BCH|XRP|EOS|TRX|NEO|VEN|LRC|KNC|XEM|DASH|BTG|ZEC|PIVX|ARK|WAVES|STRAT|MCO|HSR|ARK|EOSDAC|EOSN|MEETONE|ACOIN|XYO|REN|BAL|CRV|YFI|REN|NXM|RAM|BADGER|PNT|LDO|AURA|FXS|CNC|CRO|FTT|HT|OKB|PAX|HUSD|TUSD|USDC|BUSD|HUSD|PAX|GUSD|USDP|USDT|BTT|WIN|MX|BIDR|RUB|TRY|EUR|ZAR|NGN|VND|IDR|PHP|KRW|MYR|SGD|AUD|ARS|BRL|CLP|COP|MXN|PEN|UYU|CTS|DAI)\b'
                coin_matches = re.findall(coin_pattern, coins_affected_text.upper())
                coin_symbols = list(set(coin_matches)) if coin_matches else ['BTC']  # Default to BTC if none found

                # Extract date from development text or source (look for date patterns)
                date_pattern = r'(?:Published on|Published:|Date:|on)\s*(?:September|Sep|Oct|October|Nov|November|Dec|December|Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August)\s+\d{1,2},?\s+\d{4}'
                date_match = re.search(date_pattern, development_text + " " + source_text, re.IGNORECASE)

                # Fallback: look for any date pattern
                if not date_match:
                    fallback_pattern = r'(?:September|Sep|Oct|October|Nov|November|Dec|December|Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August)\s+\d{1,2},?\s+\d{4}'
                    date_match = re.search(fallback_pattern, development_text + " " + source_text)

                article_date = date_match.group(0) if date_match else f"Sep {datetime.now().day}, 2025"

                # Clean up article date if it includes "Published on" prefix
                if "Published" in article_date:
                    article_date = re.sub(r'Published\s*on\s*', '', article_date, flags=re.IGNORECASE).strip()

                # Create clean description (first 120 characters) + date
                base_description = development_text[:100].strip()
                description = f"{base_description}... (Published: {article_date})"

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
                    "impact_level": impact_level_text,
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
   - **Development:** [Detailed description of regulatory/institutional/macro event. MUST end with the exact publication date from the source article: "Published on September 27, 2025"]
   - **Coins/Tokens Affected:** [List specific cryptocurrencies impacted - BTC, ETH, SOL, etc.]
   - **Impact Level:** [High/Medium/Low - based on potential market effect]
   - **Strategic Impact:** [Long-term implications for crypto adoption/regulation]
   - **Post Highlight Potential:** [High/Medium/Low - how newsworthy for social posts]
   - **Source:** [News source website + exact publication date]

2. **[CATEGORY]** - [Date: {yesterday.strftime('%b %d, %Y')}]
   - **Development:** [Detailed description. MUST end with exact publication date: "Published on September 27, 2025"]
   - **Coins/Tokens Affected:** [List specific cryptocurrencies impacted]
   - **Impact Level:** [High/Medium/Low]
   - **Strategic Impact:** [Long-term implications]
   - **Post Highlight Potential:** [High/Medium/Low]
   - **Source:** [News source website + exact publication date]

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
- **Post Highlight Potential**: Rate High/Medium/Low based on social media engagement potential

**CRITICAL REQUIREMENTS**:
1. If you cannot find real macro/strategic news from {date_range}, clearly state "NO QUALIFYING STRATEGIC DEVELOPMENTS FOUND IN LAST 24 HOURS" instead of making up information.
2. Only report ACTUAL current strategic events with proper date stamps.
3. **MANDATORY**: Each development description MUST end with the exact publication date from the source article in format: "Published on September 27, 2025" or "Published on Sep 27, 2025".
4. Include source publication date in the Source field as well.
5. ALL dates must be from {date_range} period - reject any older news."""

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