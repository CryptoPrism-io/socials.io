"""Instagram content generation pipeline workflow."""

import asyncio
import os
import sys
import pandas as pd

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️ dotenv not available, using system environment variables")

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.database import (
    fetch_top_coins, fetch_btc_snapshot, fetch_global_market_data,
    fetch_trading_opportunities, close_connection, gcp_engine
)
from content.template_engine import get_template_renderer
from generate_macro_news import generate_macro_intelligence_with_json_conversion
from media.screenshot import generate_image_from_html

async def render_page_1():
    """Render page 1: Top cryptocurrencies (ranks 2-24, excluding Bitcoin)."""
    print("🔄 Rendering Page 1: Top Cryptocurrencies")

    # Fetch data for coins 2-24
    df = fetch_top_coins(2, 24)

    if df.empty:
        print("❌ No data available for Page 1")
        return False

    # Get template renderer
    renderer = get_template_renderer()

    # Prepare output paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
    image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
    output_path = os.path.join(output_dir, "1_output.html")
    image_path = os.path.join(image_dir, "1_output.jpg")

    # Render template
    success = renderer.render_coins_page('1.html', df, output_path)

    if success:
        # Generate screenshot
        await generate_image_from_html(output_path, image_path)
        print("✅ Page 1 completed successfully")
        return True
    else:
        print("❌ Page 1 rendering failed")
        return False

async def render_page_2():
    """Render page 2: Extended cryptocurrencies (ranks 25-48)."""
    print("🔄 Rendering Page 2: Extended Cryptocurrencies")

    # Fetch data for coins 25-48
    df = fetch_top_coins(25, 48)

    if df.empty:
        print("❌ No data available for Page 2")
        return False

    # Get template renderer
    renderer = get_template_renderer()

    # Prepare output paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
    image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
    output_path = os.path.join(output_dir, "2_output.html")
    image_path = os.path.join(image_dir, "2_output.jpg")

    # Render template
    success = renderer.render_coins_page('2.html', df, output_path)

    if success:
        # Generate screenshot
        await generate_image_from_html(output_path, image_path)
        print("✅ Page 2 completed successfully")
        return True
    else:
        print("❌ Page 2 rendering failed")
        return False

async def render_page_3():
    """Render page 3: Top gainers and losers."""
    print("🔄 Rendering Page 3: Top Gainers and Losers")

    # Fetch top 100 coins with additional metrics
    df = fetch_top_coins(1, 100)

    if df.empty:
        print("❌ No data available for Page 3")
        return False

    # Filter for clean data and get top gainers/losers
    df_clean = df[
        (df['cmc_rank'] <= 100) &
        (df['percent_change24h'].notna()) &
        (df['logo'].notna())
    ]

    if df_clean.empty:
        print("❌ No clean data available for Page 3")
        return False

    # Get top 4 gainers and losers
    top_losers = df_clean.nsmallest(4, 'percent_change24h')
    top_gainers = df_clean.nlargest(4, 'percent_change24h')

    # Fetch DMV scores for gainers & losers
    slugs = set(list(top_losers['slug']) + list(top_gainers['slug']))
    slugs_placeholder = ', '.join(f"'{slug}'" for slug in slugs)
    scores_query = f"""
        SELECT *
        FROM "public"."FE_DMV_SCORES"
        WHERE slug IN ({slugs_placeholder})
    """
    scores_df = pd.read_sql_query(scores_query, gcp_engine)
    top_losers = pd.merge(top_losers, scores_df, on='slug', how='left')
    top_gainers = pd.merge(top_gainers, scores_df, on='slug', how='left')

    # Round DMV scores to 1 decimal
    for col in ['Durability_Score', 'Momentum_Score', 'Valuation_Score']:
        top_losers[col] = top_losers[col].round(1)
        top_gainers[col] = top_gainers[col].round(1)

    # Get template renderer
    renderer = get_template_renderer()

    # Prepare output paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
    image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
    output_path = os.path.join(output_dir, "3_output.html")
    image_path = os.path.join(image_dir, "3_output.jpg")

    # Render template
    success = renderer.render_gainers_losers_page('3.html', top_gainers, top_losers, output_path)

    if success:
        # Generate screenshot
        await generate_image_from_html(output_path, image_path)
        print("✅ Page 3 completed successfully")
        return True
    else:
        print("❌ Page 3 rendering failed")
        return False

async def render_page_4():
    """Render page 4: Trading opportunities (long and short)."""
    print("🔄 Rendering Page 4: Trading Opportunities")

    # Fetch trading opportunities
    long_opportunities = fetch_trading_opportunities("long", 15)
    short_opportunities = fetch_trading_opportunities("short", 15)

    if long_opportunities.empty and short_opportunities.empty:
        print("❌ No trading opportunities data available")
        return False

    # Get top 4 from each
    top_longs = long_opportunities.head(4) if not long_opportunities.empty else long_opportunities
    top_shorts = short_opportunities.head(4) if not short_opportunities.empty else short_opportunities

    # Get template renderer
    renderer = get_template_renderer()

    # Prepare output paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
    image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
    output_path = os.path.join(output_dir, "4_output.html")
    image_path = os.path.join(image_dir, "4_output.jpg")

    # Render template
    success = renderer.render_trading_opportunities_page('4.html', top_longs, top_shorts, output_path)

    if success:
        # Generate screenshot
        await generate_image_from_html(output_path, image_path)
        print("✅ Page 4 completed successfully")
        return True
    else:
        print("❌ Page 4 rendering failed")
        return False

async def render_page_5():
    """Render page 5: Market overview with BTC snapshot."""
    print("🔄 Rendering Page 5: Market Overview")

    # Fetch global market data and BTC snapshot
    global_data = fetch_global_market_data()
    btc_data = fetch_btc_snapshot()

    if global_data.empty and btc_data.empty:
        print("❌ No market data available for Page 5")
        return False

    # Get template renderer
    renderer = get_template_renderer()

    # Prepare output paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
    image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
    output_path = os.path.join(output_dir, "5_output.html")
    image_path = os.path.join(image_dir, "5_output.jpg")

    # Render template
    success = renderer.render_market_overview_page('5.html', global_data, btc_data, output_path)

    if success:
        # Generate screenshot
        await generate_image_from_html(output_path, image_path)
        print("✅ Page 5 completed successfully")
        return True
    else:
        print("❌ Page 5 rendering failed")
        return False

async def render_page_6():
    """Render page 6: Bitcoin snapshot with macro intelligence alerts."""
    print("🔄 Rendering Page 6: Bitcoin Snapshot with Macro Intelligence")

    # Fetch BTC data and generate macro intelligence
    btc_data = fetch_btc_snapshot()
    news_events = generate_macro_intelligence_with_json_conversion()

    if btc_data.empty:
        print("❌ No BTC data available for Page 6")
        return False

    # Convert BTC data to correct format for the template
    # The template expects a list of dictionaries with specific field names
    btc_snapshot_formatted = []
    if not btc_data.empty:
        btc_row = btc_data.iloc[0]  # Take the first row
        # Ensure logo exists, use Bitcoin SVG if not
        logo_url = btc_row.get('logo', '')
        if not logo_url or pd.isna(logo_url):
            logo_url = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiNGOUE4RDQiLz4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTIiIGZpbGw9IiNGRkYiLz4KPHRleHQgeD0iMTYiIHk9IjI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiNGOUE4RDQiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkI8L3RleHQ+PC9zdmc+'

        btc_snapshot_formatted = [{
            'logo': logo_url,
            'price': btc_row.get('price', '$112,957'),  # Already formatted by database.py
            'market_cap': btc_row.get('market_cap', '$2.2T'),  # Already formatted by database.py
            'volume24h': btc_row.get('volume24h', '$45.1B'),  # Already formatted by database.py
            'percent_change24h': btc_row.get('percent_change24h', '+1.84'),  # Already formatted by database.py
            'percent_change7d': btc_row.get('percent_change7d', '+8.92'),  # Already formatted by database.py
            'percent_change30d': btc_row.get('percent_change30d', '+12.34'),  # Already formatted by database.py
            'bearish': str(int(btc_row.get('bearish', 23))),  # bearish column from database
            'neutral': str(int(btc_row.get('neutral', 45))), # neutral column from database
            'bullish': str(int(btc_row.get('bullish', 32))),  # bullish column from database
            'Trend': btc_row.get('Trend', 'Bullish')
        }]

    # Get template renderer
    renderer = get_template_renderer()

    # Prepare output paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
    image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
    output_path = os.path.join(output_dir, "6_output.html")
    image_path = os.path.join(image_dir, "6_output.jpg")

    # Create template data in the format expected by 6.html
    from jinja2 import Environment, FileSystemLoader
    from datetime import datetime
    current_time = datetime.now()

    template_data = {
        'current_date': current_time.strftime('%d %b, %Y'),
        'current_time': current_time.strftime('%I:%M:%S %p'),
        'news_events': news_events,
        'snap': btc_snapshot_formatted
    }

    # Setup Jinja2 template directly since the renderer might not handle our new format
    template_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'base_templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('6.html')

    # Render HTML
    rendered_html = template.render(**template_data)

    # Save HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    # Generate screenshot
    try:
        await generate_image_from_html(output_path, image_path)
        print("✅ Page 6 (Macro Intelligence) completed successfully")
        return True
    except Exception as screenshot_error:
        print(f"⚠️ Page 6 HTML generated but screenshot failed: {screenshot_error}")
        return False

async def render_page_7():
    """Render page 7: Market Intelligence with L2 AI filtered top 5 news."""
    print("🔄 Rendering Page 7: Market Intelligence (L2 AI Filtered)")

    # Import the generate_7_output function
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from generate_7_output import generate_macro_intelligence_with_json_conversion

    # Generate high-quality filtered news alerts
    alerts_result = generate_macro_intelligence_with_json_conversion()

    if not alerts_result['success']:
        print(f"❌ No market intelligence data available for Page 7: {alerts_result.get('error', 'Unknown error')}")
        return False

    # Prepare template data
    from datetime import datetime
    current_time = datetime.now()

    template_data = {
        'current_date': current_time.strftime('%d %b, %Y'),
        'current_time': current_time.strftime('%I:%M:%S %p'),
        'news_events': alerts_result
    }

    # Setup Jinja2 template
    from jinja2 import Environment, FileSystemLoader
    template_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'base_templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('7.html')

    # Render HTML
    rendered_html = template.render(**template_data)

    # Prepare output paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
    image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
    output_path = os.path.join(output_dir, "7_output.html")
    image_path = os.path.join(image_dir, "7_output.jpg")

    # Save HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    # Copy CSS file if needed
    import shutil
    css_source = os.path.join(template_dir, 'style7.css')
    css_dest = os.path.join(output_dir, 'style7.css')
    if not os.path.exists(css_dest) and os.path.exists(css_source):
        shutil.copy2(css_source, css_dest)

    # Generate screenshot
    try:
        await generate_image_from_html(output_path, image_path)
        print(f"✅ Page 7 (L2 AI Market Intelligence) completed successfully")
        print(f"📊 Generated with {len(alerts_result['alerts'])} high-impact alerts")
        return True
    except Exception as screenshot_error:
        print(f"⚠️ Page 7 HTML generated but screenshot failed: {screenshot_error}")
        return False

async def run_complete_pipeline():
    """Run the complete Instagram content generation pipeline."""
    print("🚀 Starting Instagram Content Generation Pipeline")
    print("=" * 60)

    # Run all pages in sequence
    results = []

    try:
        results.append(await render_page_1())
        results.append(await render_page_2())
        results.append(await render_page_3())
        results.append(await render_page_4())
        results.append(await render_page_5())
        results.append(await render_page_6())
        results.append(await render_page_7())

        # Close database connection
        close_connection()

        # Summary
        successful_pages = sum(results)
        total_pages = len(results)

        print("\n" + "=" * 60)
        print("🎉 INSTAGRAM CONTENT GENERATION COMPLETE!")
        print("=" * 60)
        print(f"✅ Successful pages: {successful_pages}/{total_pages}")

        if successful_pages == total_pages:
            print("✅ All pages generated successfully!")
            return True
        else:
            print(f"⚠️  {total_pages - successful_pages} pages failed to generate")
            return False

    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
        close_connection()
        return False

if __name__ == "__main__":
    asyncio.run(run_complete_pipeline())