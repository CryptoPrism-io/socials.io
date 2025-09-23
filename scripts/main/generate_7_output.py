#!/usr/bin/env python3
"""
Generate 7_output.html using macro intelligence alerts
Standalone page with consistent styling matching other templates
"""

import os
import json
import re
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import create_engine
from content.openrouter_client import create_openrouter_client

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
    print("✅ Environment variables loaded in generate_7_output.py")
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
        development_pattern = r'(\d+)\. \*\*(Regulatory Update|Institutional Alert|FOMC Alert|News Alert|Technological Alert|Environmental Alert|Legal Alert|Adoption Alert)\*\*.*?\n.*?-\s+\*\*Development:\*\*(.*?)\n.*?-\s+\*\*Article Date:\*\*(.*?)\n.*?-\s+\*\*Most Affected Coin:\*\*(.*?)\n.*?-\s+\*\*Impact Analysis:\*\*(.*?)\n.*?-\s+\*\*Coins/Tokens Affected:\*\*(.*?)\n.*?-\s+\*\*Impact Level:\*\*(.*?)\n.*?-\s+\*\*Market Sentiment:\*\*(.*?)\n.*?-\s+\*\*Strategic Impact:\*\*(.*?)\n.*?-\s+\*\*Post Highlight Potential:\*\*(.*?)\n.*?-\s+\*\*Source:\*\*(.*?)(?=\n\n|\n\d+\.|$)'

        matches = re.finditer(development_pattern, macro_report_text, re.DOTALL)

        for match in matches:
            try:
                category = match.group(2)
                development_text = match.group(3).strip()
                article_date_text = match.group(4).strip()
                most_affected_coin_text = match.group(5).strip()
                impact_analysis_text = match.group(6).strip()
                coins_affected_text = match.group(7).strip()
                impact_level_text = match.group(8).strip().split()[0] if len(match.group(8).strip().split()) > 0 else 'Medium'
                sentiment_text = match.group(9).strip().split()[0] if len(match.group(9).strip().split()) > 0 else 'Neutral'
                strategic_impact = match.group(10).strip()
                highlight_potential_text = match.group(11).strip().split()[0] if len(match.group(11).strip().split()) > 0 else 'Medium'
                source_text = match.group(12).strip()

                # Extract most affected coin
                coin_pattern = r'\b(BTC|ETH|SOL|ADA|DOT|MATIC|LINK|AVAX|USDT|USDC|BUSD|BNB|LTC|UNI|AAVE|COMP|MKR|YFI|BAT|ZRX|REP|SNT|OMG|STORJ|BNT|ANT|GNT|STORM|DENT|FUN|KIN|MANA|NMR|ELE|ETC|BSV|BCH|XRP|EOS|TRX|NEO|VEN|LRC|KNC|XEM|DASH|BTG|ZEC|PIVX|ARK|WAVES|STRAT|MCO|HSR|ARK|EOSDAC|EOSN|MEETONE|ACOIN|XYO|REN|BAL|CRV|YFI|REN|NXM|RAM|BADGER|PNT|LDO|AURA|FXS|CNC|CRO|FTT|HT|OKB|PAX|HUSD|TUSD|USDC|BUSD|HUSD|PAX|GUSD|USDP|USDT|BTT|WIN|MX|BIDR|RUB|TRY|EUR|ZAR|NGN|VND|IDR|PHP|KRW|MYR|SGD|AUD|ARS|BRL|CLP|COP|MXN|PEN|UYU|CTS|DAI)\b'

                # Extract most affected coin (first match from "Most Affected Coin" field)
                most_affected_matches = re.findall(coin_pattern, most_affected_coin_text.upper())
                most_affected_coin = most_affected_matches[0] if most_affected_matches else None

                # Parse all affected coins
                coin_matches = re.findall(coin_pattern, coins_affected_text.upper())
                coin_symbols = list(set(coin_matches)) if coin_matches else ['BTC']  # Default to BTC if none found

                # If no most affected coin found, use first from affected coins
                if not most_affected_coin:
                    most_affected_coin = coin_symbols[0] if coin_symbols else 'BTC'

                # Use full description (no truncation)
                description = development_text.strip()

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
                    "article_date": article_date_text,
                    "tag": tag,
                    "source": source_text,
                    "coins_affected": coin_symbols,
                    "coin_name": coin_symbols[0] if coin_symbols else 'BTC',  # Legacy field
                    "most_affected": most_affected_coin,
                    "impact_analysis": impact_analysis_text,
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

        # L2 AI FILTERING: Select top 5 highest impact news with quality validation
        print(f"🔍 L2 AI Processing: Evaluating {len(alerts)} alerts for impact-based filtering...")

        # Step 1: Quality validation - reject poor quality news
        quality_filtered_alerts = []
        for alert in alerts:
            # Quality checks
            quality_score = 0
            reject_reasons = []

            # Check for specific names (not vague terms)
            vague_terms = ['major exchange', 'leading institution', 'prominent protocol', 'major company', 'regulatory body']
            has_vague_terms = any(term.lower() in alert['description'].lower() for term in vague_terms)
            if not has_vague_terms:
                quality_score += 30
            else:
                reject_reasons.append("Contains vague terms")

            # Check description length and detail (more lenient for full descriptions)
            if len(alert['description']) >= 40:
                quality_score += 20
            else:
                reject_reasons.append("Description too short")

            # Check for proper article date (freshness validation)
            import datetime
            current_date = datetime.datetime.now()
            yesterday = current_date - datetime.timedelta(days=1)

            try:
                # Parse article date
                article_date_str = alert['article_date'].strip()
                # Handle various date formats
                for fmt in ['%b %d, %Y', '%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d', '%d %b, %Y']:
                    try:
                        article_date = datetime.datetime.strptime(article_date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If no format matches, try to extract just the day/month
                    if any(word in article_date_str.lower() for word in ['sep', 'september']):
                        if any(str(day) in article_date_str for day in [current_date.day, yesterday.day]):
                            quality_score += 25  # Recent date detected
                        else:
                            reject_reasons.append("Stale news (not from last 24 hours)")
                    else:
                        reject_reasons.append("Invalid date format")

                # Check if date is within last 24 hours
                if 'article_date' in locals() and (current_date - article_date).days <= 1:
                    quality_score += 25
                elif len(reject_reasons) == 0:  # Only add if we haven't already flagged date issues
                    reject_reasons.append("Article not from last 24 hours")

            except Exception as e:
                reject_reasons.append(f"Date parsing error: {str(e)}")

            # Impact level consideration
            if alert.get('impact_level', '').lower() == 'high':
                quality_score += 15
            elif alert.get('impact_level', '').lower() == 'medium':
                quality_score += 10

            # Post highlight potential
            if alert.get('highlight_potential', '').lower() == 'high':
                quality_score += 10

            # Accept if quality score >= 50 (out of 100)
            if quality_score >= 50:
                alert['quality_score'] = quality_score
                quality_filtered_alerts.append(alert)
                print(f"✅ Accepted: {alert['category']} (Quality: {quality_score}/100)")
            else:
                print(f"❌ Rejected: {alert['category']} (Quality: {quality_score}/100) - {', '.join(reject_reasons)}")

        print(f"📊 Quality filtering: {len(quality_filtered_alerts)}/{len(alerts)} alerts passed validation")

        # Step 2: Impact-based ranking for top 5 selection
        def calculate_impact_score(alert):
            """Calculate comprehensive impact score for ranking"""
            score = 0

            # Impact level weight (40 points max)
            impact_level = alert.get('impact_level', '').lower()
            if impact_level == 'high':
                score += 40
            elif impact_level == 'medium':
                score += 25
            elif impact_level == 'low':
                score += 10

            # Sentiment clarity (20 points max)
            sentiment = alert.get('sentiment', '').lower()
            if sentiment in ['bullish', 'bearish']:
                score += 20  # Clear directional sentiment
            elif sentiment == 'neutral':
                score += 10

            # Post highlight potential (20 points max)
            highlight = alert.get('highlight_potential', '').lower()
            if highlight == 'high':
                score += 20
            elif highlight == 'medium':
                score += 12
            elif highlight == 'low':
                score += 5

            # Category importance (10 points max)
            category = alert.get('category', '')
            high_impact_categories = ['Regulatory Update', 'Institutional Alert', 'Legal Alert']
            medium_impact_categories = ['Technological Alert', 'Adoption Alert', 'Environmental Alert']

            if category in high_impact_categories:
                score += 10
            elif category in medium_impact_categories:
                score += 6
            else:
                score += 3

            # Quality score bonus (10 points max)
            quality_bonus = min(alert.get('quality_score', 0) / 10, 10)
            score += quality_bonus

            return score

        # Rank alerts by impact score
        for alert in quality_filtered_alerts:
            alert['impact_score'] = calculate_impact_score(alert)

        # Sort by impact score (highest first)
        ranked_alerts = sorted(quality_filtered_alerts, key=lambda x: x['impact_score'], reverse=True)

        # Select top 6
        top_alerts = ranked_alerts[:6]

        if len(top_alerts) == 0:
            return {
                'success': False,
                'error': 'No qualifying high-impact developments found after L2 AI filtering'
            }

        print(f"🎯 L2 AI Impact Ranking:")
        for i, alert in enumerate(top_alerts, 1):
            print(f"   {i}. {alert['category']} (Impact: {alert['impact_score']:.1f}/100, Quality: {alert['quality_score']}/100)")

        print(f"✅ L2 AI filtered to top {len(top_alerts)} highest-impact alerts")
        return {
            'success': True,
            'alerts': top_alerts
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

        macro_prompt = f"""You are a senior crypto market intelligence analyst creating content for a crypto market events table.
Your task: Search the web for **Bitcoin, Ethereum, and major cryptocurrency news from TODAY'S DATE: {today_display}.**

**CONTEXT**: This data will be displayed in a structured table with columns: Category | Description | Impact (Bullish/Bearish/Neutral) | Most Affected Coin

✅ Focus only on **{date_range}** (last 24 hours). Ignore older news.
✅ We are NOT interested in price % moves or technical levels.
✅ Instead, focus on **macro, regulatory, institutional, and strategic developments** that have clear cryptocurrency impact:

**Event Types to Search For:**
- **Regulatory**: SEC decisions, ETF approvals/rejections, government regulations, policy changes
- **Institutional**: Corporate adoption, fund launches, custody services, partnerships
- **Technological**: Protocol upgrades, security incidents, blockchain improvements
- **Environmental**: Mining regulations, energy policies, ESG concerns
- **Legal**: Lawsuits, compliance issues, regulatory enforcement
- **Adoption**: Payment integrations, merchant adoption, mainstream acceptance

✅ **CRITICAL REQUIREMENT**: For each event, analyze and identify the **SINGLE MOST AFFECTED** cryptocurrency:
- Which specific coin/token will be most impacted by this news?
- Consider direct relationships (e.g., Ethereum upgrades → ETH, Bitcoin ETF → BTC)
- For broader market events, identify the primary beneficiary or victim
- Provide reasoning based on the event's direct technical, regulatory, or business impact

✅ **PRIORITY**: Events with named institutions (BlackRock, Fidelity, Coinbase, Binance, SEC, Federal Reserve, JPMorgan, Goldman Sachs, MicroStrategy, Tesla, PayPal, Visa, Mastercard)

Create a detailed market intelligence report covering the TOP 10 most important macro/strategic developments from the last 24 hours.

**IMPORTANT**: Provide EXACTLY 10 developments, no more. If fewer than 10 qualifying events exist, provide only the available ones. Quality over quantity. (Note: L2 AI will filter these to the top 6 highest-impact alerts for display.)

**CRYPTO MACRO INTELLIGENCE REPORT**
**Date: {today_display}**

**EXECUTIVE SUMMARY:**
[Brief overview of key macro/strategic developments and implications]

**TOP STRATEGIC DEVELOPMENTS:**

1. **[CATEGORY]** - [Date: {yesterday.strftime('%b %d, %Y')}]
   - **Development:** [SPECIFIC detailed description with actual company/entity names - e.g., "Binance faces lawsuit by SEC" not "major exchange faces lawsuit"]
   - **Article Date:** [Exact date when this news was published - e.g., "Sep 23, 2025" or "September 23"]
   - **Most Affected Coin:** [Single cryptocurrency most impacted - BTC, ETH, SOL, etc.]
   - **Impact Analysis:** [Why this specific coin is most affected - technical, regulatory, or business reasoning]
   - **Coins/Tokens Affected:** [All cryptocurrencies impacted - BTC, ETH, SOL, etc.]
   - **Impact Level:** [High/Medium/Low - based on potential market effect]
   - **Market Sentiment:** [Bullish/Bearish/Neutral - how this affects market sentiment]
   - **Strategic Impact:** [Long-term implications for crypto adoption/regulation]
   - **Post Highlight Potential:** [High/Medium/Low - how newsworthy for social posts]
   - **Source:** [News source website]

2. **[CATEGORY]** - [Date: {yesterday.strftime('%b %d, %Y')}]
   - **Development:** [SPECIFIC detailed description with actual names - avoid vague terms like "major institution", "prominent exchange"]
   - **Article Date:** [Exact date when this news was published]
   - **Most Affected Coin:** [Single cryptocurrency most impacted]
   - **Impact Analysis:** [Why this specific coin is most affected]
   - **Coins/Tokens Affected:** [All cryptocurrencies impacted]
   - **Impact Level:** [High/Medium/Low]
   - **Market Sentiment:** [Bullish/Bearish/Neutral]
   - **Strategic Impact:** [Long-term implications]
   - **Post Highlight Potential:** [High/Medium/Low]
   - **Source:** [News source website]

[Continue for all developments - MAXIMUM 10 total]

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
- **Development**: MUST include specific names and details. NO vague terms like:
  ❌ "major cryptocurrency exchange" → ✅ "Coinbase" or "Binance"
  ❌ "leading financial institution" → ✅ "JPMorgan" or "Goldman Sachs"
  ❌ "prominent DeFi protocol" → ✅ "Uniswap" or "Aave"
  ❌ "regulatory body" → ✅ "SEC" or "CFTC"
- **Article Date**: EXACT publication date (e.g., "Sep 23, 2025" or "September 23") - verify articles are from {date_range}
- **Most Affected Coin**: SINGLE cryptocurrency most impacted (BTC, ETH, SOL, USDT, USDC, ADA, DOT, MATIC, etc.)
- **Impact Analysis**: Clear reasoning why this specific coin is most affected by the event
- **Coins/Tokens Affected**: All cryptocurrencies directly impacted (BTC, ETH, SOL, USDT, USDC, ADA, DOT, MATIC, etc.)
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

def generate_7_output_html():
    """
    Generate 7_output.html using macro intelligence alerts
    """
    try:
        print("🚀 Generating 7_output.html with macro intelligence...")

        # Step 1: Get macro intelligence alerts
        print("🔍 Generating macro intelligence alerts...")
        alerts_result = generate_macro_intelligence_with_json_conversion()

        # Step 2: Prepare template data
        current_time = datetime.now()

        template_data = {
            'current_date': current_time.strftime('%d %b, %Y'),
            'current_time': current_time.strftime('%I:%M:%S %p'),
            'news_events': alerts_result
        }

        print(f"📊 Template data prepared:")
        print(f"   - Macro alerts: {len(alerts_result['alerts']) if alerts_result['success'] else 0}")
        print(f"   - Current timestamp: {template_data['current_date']} {template_data['current_time']}")

        # Step 3: Setup Jinja2 template
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'base_templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('7.html')

        # Step 4: Render HTML
        rendered_html = template.render(**template_data)

        # Step 5: Save to 7_output.html
        output_html_path = os.path.join(os.path.dirname(__file__), '..', '..', 'output_html', '7_output.html')

        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)

        print(f"✅ Successfully generated: {output_html_path}")
        print(f"📄 HTML file size: {len(rendered_html)} characters")

        # Step 6: Also copy the CSS file if it doesn't exist
        import shutil
        css_source = os.path.join(template_dir, 'style7.css')
        css_dest = os.path.join(os.path.dirname(output_html_path), 'style7.css')

        if not os.path.exists(css_dest):
            if os.path.exists(css_source):
                shutil.copy2(css_source, css_dest)
                print("📁 Copied style7.css to output_html directory")

        return {
            'success': True,
            'html_path': output_html_path,
            'alerts_count': len(alerts_result['alerts']) if alerts_result['success'] else 0,
            'data': template_data
        }

    except Exception as e:
        error_msg = f"7_output generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

if __name__ == "__main__":
    # Generate the 7_output.html file
    result = generate_7_output_html()

    if result['success']:
        print(f"\n🎉 SUCCESS! Generated 7_output.html with {result['alerts_count']} macro intelligence alerts")
        print(f"📂 Location: {result['html_path']}")
        print("\nNext steps:")
        print("1. Open output_html/7_output.html in browser to preview")
        print("2. Use screenshot tool to convert to image if needed")
        print("3. Ready for Instagram posting!")
    else:
        print(f"\n❌ Failed to generate 7_output: {result['error']}")
        print("Check OpenRouter API key and network connection")