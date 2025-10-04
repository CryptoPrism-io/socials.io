#!/usr/bin/env python3
"""
Generate 4_output.html - Trading Opportunities
Individual post generator for Template 4
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.database import fetch_trading_opportunities, close_connection
from content.template_engine import get_template_renderer
from media.screenshot import generate_image_from_html

def generate_4_output():
    """Generate Template 4: Trading Opportunities"""
    print("🚀 Generating Template 4: Trading Opportunities")

    try:
        # Fetch both long and short trading opportunities (top 5 each)
        long_df = fetch_trading_opportunities("long", 5)
        short_df = fetch_trading_opportunities("short", 5)

        # Only use real trading opportunities data - no fallbacks
        if long_df.empty and short_df.empty:
            print("❌ No real trading opportunities data available")
            # Create error HTML instead of failing
            error_html = """<!DOCTYPE html><html><head><title>Template 4 Error</title></head>
            <body><h1>Error: No Real Trading Opportunities Data Available</h1>
            <p>The FE_DMV_ALL and FE_RATIOS tables don't contain sufficient data for real trading opportunities.</p>
            <p>Please ensure the CRON jobs have populated the required tables with trading data.</p></body></html>"""

            output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
            output_path = os.path.join(output_dir, "4_output.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(error_html)
            print(f"✅ Error message written to: {output_path}")
            return False

        # Get template renderer
        renderer = get_template_renderer()

        # Prepare output paths
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        output_path = os.path.join(output_dir, "4_output.html")

        # Render template
        success = renderer.render_trading_opportunities_page('4.html', long_df, short_df, output_path)

        if success:
            print(f"✅ Template 4 HTML generated: {output_path}")
            return True
        else:
            print("❌ Template 4 rendering failed")
            return False

    except Exception as e:
        print(f"❌ Template 4 generation error: {str(e)}")
        return False
    finally:
        close_connection()

async def generate_4_with_screenshot():
    """Generate Template 4 with screenshot"""
    print("📸 Generating Template 4 with screenshot...")

    # Generate HTML
    html_success = generate_4_output()
    if not html_success:
        return False

    # Generate screenshot
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
        output_path = os.path.join(output_dir, "4_output.html")
        image_path = os.path.join(image_dir, "4_output.jpg")

        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 4 screenshot generated: {image_path}")
        return True

    except Exception as e:
        print(f"❌ Template 4 screenshot error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run with screenshot generation
    result = asyncio.run(generate_4_with_screenshot())

    if result:
        print("🎉 Template 4 generation completed successfully!")
    else:
        print("💥 Template 4 generation failed!")
        sys.exit(1)