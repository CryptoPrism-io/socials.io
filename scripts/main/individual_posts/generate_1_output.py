#!/usr/bin/env python3
"""
Generate 1_output.html - Top Cryptocurrencies (ranks 2-24, excluding Bitcoin)
Individual post generator for Template 1
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.database import fetch_top_coins
from content.template_engine import get_template_renderer
from media.screenshot import generate_image_from_html

def generate_1_output():
    """Generate Template 1: Top Cryptocurrencies"""
    print("🚀 Generating Template 1: Top Cryptocurrencies")

    try:
        # Fetch data for coins 2-24
        df = fetch_top_coins(2, 24)

        if df.empty:
            print("❌ No data available for Template 1")
            return False

        # Get template renderer
        renderer = get_template_renderer()

        # Prepare output paths
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        output_path = os.path.join(output_dir, "12_top_cryptos_2_24_output.html")

        # Render template
        success = renderer.render_coins_page('1.html', df, output_path)

        if success:
            print(f"✅ Template 1 HTML generated: {output_path}")
            return True
        else:
            print("❌ Template 1 rendering failed")
            return False

    except Exception as e:
        print(f"❌ Template 1 generation error: {str(e)}")
        return False

async def generate_1_with_screenshot():
    """Generate Template 1 with screenshot"""
    print("📸 Generating Template 1 with screenshot...")

    # Generate HTML
    html_success = generate_1_output()
    if not html_success:
        return False

    # Generate screenshot
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
        output_path = os.path.join(output_dir, "12_top_cryptos_2_24_output.html")
        image_path = os.path.join(image_dir, "12_top_cryptos_2_24_output.jpg")

        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 1 screenshot generated: {image_path}")
        return True

    except Exception as e:
        print(f"❌ Template 1 screenshot error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run with screenshot generation
    result = asyncio.run(generate_1_with_screenshot())

    if result:
        print("🎉 Template 1 generation completed successfully!")
    else:
        print("💥 Template 1 generation failed!")
        sys.exit(1)