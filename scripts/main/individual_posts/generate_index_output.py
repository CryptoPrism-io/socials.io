#!/usr/bin/env python3
"""
Generate Index Slide - Market Pulse Overview
Second slide of the mega-carousel with section list and quick stats
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Load environment variables
load_dotenv()

from scripts.main.content.template_engine import TemplateRenderer
from scripts.main.media.screenshot import generate_image_from_html
from scripts.main.data.database import fetch_btc_snapshot, fetch_top_coins

def get_fear_greed_label(value):
    """
    Convert Fear & Greed value to label

    Args:
        value: Fear & Greed index (0-100)

    Returns:
        str: Label text
    """
    if value is None:
        return "Unknown"

    if value < 25:
        return "Extreme Fear"
    elif value < 40:
        return "Fear"
    elif value < 60:
        return "Neutral"
    elif value < 75:
        return "Greed"
    else:
        return "Extreme Greed"

async def generate_index_output():
    """Generate index slide with market snapshot"""
    print("📸 Generating Index Slide...")
    print("🎬 Creating market overview with quick stats...")

    try:
        # Get current time
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")

        # Fetch Bitcoin snapshot for Fear & Greed and BTC price
        print("🔍 Fetching Bitcoin snapshot...")
        btc_data = fetch_btc_snapshot()

        fear_greed_value = None
        btc_price = "Loading..."
        btc_change_24h = 0

        if btc_data is not None and not btc_data.empty:
            btc_row = btc_data.iloc[0]
            fear_greed_value = btc_row.get('fear_greed_value')
            price_raw = btc_row.get('price', 0)
            # Convert price to float if it's a string
            try:
                price_float = float(price_raw)
                btc_price = f"{price_float:,.0f}"
            except (ValueError, TypeError):
                btc_price = str(price_raw)
            btc_change_24h = round(btc_row.get('percent_change_24h', 0), 2)
            print(f"  📊 Fear & Greed: {fear_greed_value}")
            print(f"  ₿ BTC Price: ${btc_price}")
            print(f"  📈 BTC Change: {btc_change_24h}%")

        fear_greed_label = get_fear_greed_label(fear_greed_value)

        # Fetch top coins to find top gainer and loser
        print("🔍 Fetching top movers...")
        all_coins_df = fetch_top_coins(start_rank=1, end_rank=100)

        # Find top gainer
        if not all_coins_df.empty:
            gainer_idx = all_coins_df['percent_change24h'].idxmax()
            top_gainer = all_coins_df.loc[gainer_idx]
            top_gainer_symbol = top_gainer.get('symbol', 'N/A')
            top_gainer_change = round(top_gainer.get('percent_change24h', 0), 2)
            print(f"  🚀 Top Gainer: {top_gainer_symbol} (+{top_gainer_change}%)")

            # Find top loser
            loser_idx = all_coins_df['percent_change24h'].idxmin()
            top_loser = all_coins_df.loc[loser_idx]
            top_loser_symbol = top_loser.get('symbol', 'N/A')
            top_loser_change = round(top_loser.get('percent_change24h', 0), 2)
            print(f"  📉 Top Loser: {top_loser_symbol} ({top_loser_change}%)")
        else:
            top_gainer_symbol = 'N/A'
            top_gainer_change = 0
            top_loser_symbol = 'N/A'
            top_loser_change = 0

        # Prepare template context
        context = {
            'current_time': current_time,
            'fear_greed_value': fear_greed_value if fear_greed_value else 'N/A',
            'fear_greed_label': fear_greed_label,
            'btc_price': btc_price,
            'btc_change_24h': btc_change_24h,
            'top_gainer_symbol': top_gainer_symbol,
            'top_gainer_change': top_gainer_change,
            'top_loser_symbol': top_loser_symbol,
            'top_loser_change': top_loser_change
        }

        # Initialize template renderer
        renderer = TemplateRenderer()

        # Prepare output paths
        output_dir = Path(__file__).parent.parent.parent.parent / 'output_html'
        output_html = output_dir / '02_index_output.html'
        output_image = Path(__file__).parent.parent.parent.parent / 'output_images' / '02_index_output.jpg'

        # Ensure directories exist
        output_dir.mkdir(parents=True, exist_ok=True)
        output_image.parent.mkdir(parents=True, exist_ok=True)

        # Render template
        html_content = renderer.render_template('index.html', context)

        if not html_content:
            print("❌ Failed to render index template")
            return False

        # Save HTML
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Index HTML generated: {output_html}")

        # Copy CSS files to output_html directory
        import shutil
        base_templates_dir = Path(__file__).parent.parent.parent.parent / 'base_templates'
        css_files = ['style_index.css', 'style_base.css']

        for css_file in css_files:
            css_source = base_templates_dir / css_file
            css_dest = output_dir / css_file
            if css_source.exists() and not css_dest.exists():
                shutil.copy2(css_source, css_dest)
                print(f"📁 Copied {css_file} to output_html directory")

        # Generate screenshot
        await generate_image_from_html(
            output_html_file=str(output_html),
            output_image_path=str(output_image)
        )
        print(f"✅ Index screenshot generated: {output_image}")
        print("🎉 Index slide generation completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Error generating index slide: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    result = asyncio.run(generate_index_output())
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
