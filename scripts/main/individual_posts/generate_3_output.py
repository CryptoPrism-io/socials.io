#!/usr/bin/env python3
"""
Generate 3_output.html - Top Gainers and Losers
Individual post generator for Template 3
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.database import fetch_top_coins, close_connection
from content.template_engine import get_template_renderer
from media.screenshot import generate_image_from_html

def generate_3_output():
    """Generate Template 3: Top Gainers and Losers"""
    print("🚀 Generating Template 3: Top Gainers and Losers")

    try:
        # Fetch data for top 50 coins for gainers/losers analysis
        df = fetch_top_coins(1, 50)

        if df.empty:
            print("❌ No data available for Template 3")
            return False

        # Get template renderer
        renderer = get_template_renderer()

        # Prepare output paths
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        output_path = os.path.join(output_dir, "3_output.html")

        # Split data into gainers and losers
        gainers_df = df[df['percent_change24h'] > 0].nlargest(10, 'percent_change24h')
        losers_df = df[df['percent_change24h'] < 0].nsmallest(10, 'percent_change24h')

        # Render template
        success = renderer.render_gainers_losers_page('3.html', gainers_df, losers_df, output_path)

        if success:
            print(f"✅ Template 3 HTML generated: {output_path}")
            return True
        else:
            print("❌ Template 3 rendering failed")
            return False

    except Exception as e:
        print(f"❌ Template 3 generation error: {str(e)}")
        return False
    finally:
        close_connection()

async def generate_3_with_screenshot():
    """Generate Template 3 with screenshot"""
    print("📸 Generating Template 3 with screenshot...")

    # Generate HTML
    html_success = generate_3_output()
    if not html_success:
        return False

    # Generate screenshot
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
        output_path = os.path.join(output_dir, "3_output.html")
        image_path = os.path.join(image_dir, "3_output.jpg")

        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 3 screenshot generated: {image_path}")
        return True

    except Exception as e:
        print(f"❌ Template 3 screenshot error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run with screenshot generation
    result = asyncio.run(generate_3_with_screenshot())

    if result:
        print("🎉 Template 3 generation completed successfully!")
    else:
        print("💥 Template 3 generation failed!")
        sys.exit(1)