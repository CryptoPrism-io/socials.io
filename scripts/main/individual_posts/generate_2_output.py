#!/usr/bin/env python3
"""
Generate 2_output.html - Extended Cryptocurrencies (ranks 25-48)
Individual post generator for Template 2
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

def generate_2_output():
    """Generate Template 2: Extended Cryptocurrencies"""
    print("🚀 Generating Template 2: Extended Cryptocurrencies")

    try:
        # Fetch data for coins 25-48
        df = fetch_top_coins(25, 48)

        if df.empty:
            print("❌ No data available for Template 2")
            return False

        # Get template renderer
        renderer = get_template_renderer()

        # Prepare output paths
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        output_path = os.path.join(output_dir, "13_top_cryptos_25_48_output.html")

        # Render template
        success = renderer.render_coins_page('2.html', df, output_path)

        if success:
            print(f"✅ Template 2 HTML generated: {output_path}")
            return True
        else:
            print("❌ Template 2 rendering failed")
            return False

    except Exception as e:
        print(f"❌ Template 2 generation error: {str(e)}")
        return False

async def generate_2_with_screenshot():
    """Generate Template 2 with screenshot"""
    print("📸 Generating Template 2 with screenshot...")

    # Generate HTML
    html_success = generate_2_output()
    if not html_success:
        return False

    # Generate screenshot
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
        output_path = os.path.join(output_dir, "13_top_cryptos_25_48_output.html")
        image_path = os.path.join(image_dir, "13_top_cryptos_25_48_output.jpg")

        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 2 screenshot generated: {image_path}")
        return True

    except Exception as e:
        print(f"❌ Template 2 screenshot error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run with screenshot generation
    result = asyncio.run(generate_2_with_screenshot())

    if result:
        print("🎉 Template 2 generation completed successfully!")
    else:
        print("💥 Template 2 generation failed!")
        sys.exit(1)