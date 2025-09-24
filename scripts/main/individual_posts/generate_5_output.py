#!/usr/bin/env python3
"""
Generate 5_output.html - Market Overview
Individual post generator for Template 5
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.database import fetch_global_market_data, fetch_btc_snapshot, close_connection
from content.template_engine import get_template_renderer
from media.screenshot import generate_image_from_html

def generate_5_output():
    """Generate Template 5: Market Overview"""
    print("🚀 Generating Template 5: Market Overview")

    try:
        # Fetch global market data and BTC snapshot
        global_data = fetch_global_market_data()
        btc_data = fetch_btc_snapshot()

        if global_data.empty and btc_data.empty:
            print("❌ No market data available for Template 5")
            return False

        # Get template renderer
        renderer = get_template_renderer()

        # Prepare output paths
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        output_path = os.path.join(output_dir, "5_output.html")

        # Render template
        success = renderer.render_market_overview_page('5.html', global_data, btc_data, output_path)

        if success:
            print(f"✅ Template 5 HTML generated: {output_path}")
            return True
        else:
            print("❌ Template 5 rendering failed")
            return False

    except Exception as e:
        print(f"❌ Template 5 generation error: {str(e)}")
        return False
    finally:
        close_connection()

async def generate_5_with_screenshot():
    """Generate Template 5 with screenshot"""
    print("📸 Generating Template 5 with screenshot...")

    # Generate HTML
    html_success = generate_5_output()
    if not html_success:
        return False

    # Generate screenshot
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
        output_path = os.path.join(output_dir, "5_output.html")
        image_path = os.path.join(image_dir, "5_output.jpg")

        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 5 screenshot generated: {image_path}")
        return True

    except Exception as e:
        print(f"❌ Template 5 screenshot error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run with screenshot generation
    result = asyncio.run(generate_5_with_screenshot())

    if result:
        print("🎉 Template 5 generation completed successfully!")
    else:
        print("💥 Template 5 generation failed!")
        sys.exit(1)