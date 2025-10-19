#!/usr/bin/env python3
"""
Generate Cover Slide - Crypto Market Pulse
First slide of the mega-carousel with branding and date
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
from scripts.main.data.database import fetch_btc_snapshot

def get_sentiment_hook(fear_greed_value):
    """
    Generate dynamic sentiment hook based on Fear & Greed Index

    Args:
        fear_greed_value: Fear & Greed index (0-100)

    Returns:
        str: Sentiment hook text
    """
    if fear_greed_value is None:
        return "Daily Market Intelligence"

    if fear_greed_value < 25:
        return "Extreme Fear Grips the Market"
    elif fear_greed_value < 40:
        return "Fear Creeps In"
    elif fear_greed_value < 60:
        return "Markets Hold Steady"
    elif fear_greed_value < 75:
        return "Greed Rising"
    else:
        return "Extreme Greed Takes Over"

async def generate_cover_output():
    """Generate cover slide with dynamic data"""
    print("📸 Generating Cover Slide...")
    print("🎬 Creating Market Pulse hero card...")

    try:
        # Get current date and time
        now = datetime.now()
        current_date = now.strftime("%d %b, %Y")  # "18 Oct, 2025"
        current_time = now.strftime("%I:%M:%S %p")  # "02:00:00 AM"

        # Fetch Fear & Greed index for sentiment hook from BTC snapshot
        fear_greed_value = None
        try:
            btc_data = fetch_btc_snapshot()
            if btc_data and len(btc_data) > 0:
                fear_greed_value = btc_data[0].get('fear_greed_value')
                print(f"🟠 Fear & Greed Index: {fear_greed_value}")
        except Exception as e:
            print(f"⚠️  Could not fetch Fear & Greed: {e}")
            print("   Using default sentiment hook")

        # Generate sentiment hook
        sentiment_hook = get_sentiment_hook(fear_greed_value)
        print(f"💬 Sentiment Hook: '{sentiment_hook}'")

        # Prepare template context
        context = {
            'current_date': current_date,
            'current_time': current_time,
            'sentiment_hook': sentiment_hook
        }

        # Initialize template renderer
        renderer = TemplateRenderer()

        # Prepare output paths
        output_dir = Path(__file__).parent.parent.parent.parent / 'output_html'
        output_html = output_dir / '01_cover_output.html'
        output_image = Path(__file__).parent.parent.parent.parent / 'output_images' / '01_cover_output.jpg'

        # Ensure directories exist
        output_dir.mkdir(parents=True, exist_ok=True)
        output_image.parent.mkdir(parents=True, exist_ok=True)

        # Render template
        html_content = renderer.render_template('cover.html', context)

        if not html_content:
            print("❌ Failed to render cover template")
            return False

        # Save HTML
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Cover HTML generated: {output_html}")

        # Copy CSS files to output_html directory (always copy to get latest changes)
        import shutil
        base_templates_dir = Path(__file__).parent.parent.parent.parent / 'base_templates'
        css_files = ['style_cover.css', 'style_base.css']

        for css_file in css_files:
            css_source = base_templates_dir / css_file
            css_dest = output_dir / css_file
            if css_source.exists():
                shutil.copy2(css_source, css_dest)
                print(f"📁 Copied {css_file} to output_html directory")

        # Generate screenshot
        await generate_image_from_html(
            output_html_file=str(output_html),
            output_image_path=str(output_image)
        )
        print(f"✅ Cover screenshot generated: {output_image}")
        print("🎉 Cover slide generation completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Error generating cover slide: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    result = asyncio.run(generate_cover_output())
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
