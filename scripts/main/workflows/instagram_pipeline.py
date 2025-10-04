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

    try:
        # Step 1: Get macro intelligence alerts
        print("🔍 Generating macro intelligence alerts...")
        alerts_result = generate_macro_intelligence_with_json_conversion()

        # Step 2: Get BTC snapshot data from database
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
                    if _k in snap and snap[_k]:
                        snap[_k] = snap[_k].lstrip('$')
        else:
            print("❌ No BTC data available for Page 6")
            return False

        # Step 3: Prepare template data
        from datetime import datetime
        current_time = datetime.now()

        template_data = {
            'current_date': current_time.strftime('%d %b, %Y'),
            'current_time': current_time.strftime('%I:%M:%S %p'),
            'news_events': alerts_result,
            'snaps': btc_snapshots[0] if btc_snapshots else {}  # Pass as single dict, not list
        }

        print(f"📊 Template data prepared:")
        print(f"   - Macro alerts: {len(alerts_result['alerts']) if alerts_result['success'] else 0}")
        print(f"   - BTC snapshots: {len(btc_snapshots)}")
        print(f"   - Current timestamp: {template_data['current_date']} {template_data['current_time']}")

        # Step 4: Setup Jinja2 template
        from jinja2 import Environment, FileSystemLoader
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'base_templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('6.html')

        # Step 5: Render HTML
        rendered_html = template.render(**template_data)

        # Step 6: Save to 6_output.html
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
        output_path = os.path.join(output_dir, "6_output.html")
        image_path = os.path.join(image_dir, "6_output.jpg")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)

        print(f"✅ Successfully generated: {output_path}")
        print(f"📄 HTML file size: {len(rendered_html)} characters")

        # Step 7: Also copy the CSS file if it doesn't exist
        import shutil
        css_source = os.path.join(template_dir, 'style6.css')
        css_dest = os.path.join(output_dir, 'style6.css')

        if not os.path.exists(css_dest):
            if os.path.exists(css_source):
                shutil.copy2(css_source, css_dest)
                print("📁 Copied style6.css to output_html directory")

        # Generate screenshot
        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 6 screenshot generated: {image_path}")
        print("✅ Page 6 completed successfully")
        return True

    except Exception as e:
        print(f"❌ Page 6 generation error: {str(e)}")
        return False

async def render_page_7():
    """Render page 7: Market Intelligence with L2 AI filtered top 5 news."""
    print("🔄 Rendering Page 7: Market Intelligence (L2 AI Filtered)")

    try:
        # Generate high-quality filtered news alerts using the same function as Page 6
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

        print(f"📊 Template 7 data prepared:")
        print(f"   - High-impact alerts: {len(alerts_result['alerts']) if alerts_result['success'] else 0}")
        print(f"   - Current timestamp: {template_data['current_date']} {template_data['current_time']}")

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

        print(f"✅ Successfully generated: {output_path}")
        print(f"📄 HTML file size: {len(rendered_html)} characters")

        # Copy CSS file if needed
        import shutil
        css_source = os.path.join(template_dir, 'style7.css')
        css_dest = os.path.join(output_dir, 'style7.css')
        if not os.path.exists(css_dest) and os.path.exists(css_source):
            shutil.copy2(css_source, css_dest)
            print("📁 Copied style7.css to output_html directory")

        # Generate screenshot
        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 7 screenshot generated: {image_path}")
        print(f"✅ Page 7 (L2 AI Market Intelligence) completed successfully")
        print(f"📊 Generated with {len(alerts_result['alerts'])} high-impact alerts")
        return True

    except Exception as e:
        print(f"❌ Page 7 generation error: {str(e)}")
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