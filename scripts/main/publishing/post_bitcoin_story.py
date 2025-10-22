#!/usr/bin/env python3
"""
Generate and post Bitcoin Intelligence Story to Instagram
Story format: 1080x1920 optimized for Instagram Stories
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from jinja2 import Environment, FileSystemLoader
from data.database import fetch_btc_snapshot
from media.screenshot import generate_image_from_html
from publishing.session_manager import InstagramSessionManager

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Enable UTF-8
import io
import locale
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print("Unicode support: UTF-8 encoding enabled globally")

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = PROJECT_ROOT / "base_templates"
OUTPUT_HTML_DIR = PROJECT_ROOT / "output_html"
OUTPUT_IMAGES_DIR = PROJECT_ROOT / "output_images"
SESSION_FILE = PROJECT_ROOT / "data" / "instagram_session.json"

# Output files
HTML_OUTPUT = OUTPUT_HTML_DIR / "bitcoin_story_output.html"
IMAGE_OUTPUT = OUTPUT_IMAGES_DIR / "bitcoin_story_output.jpg"

def format_large_number(value):
    """Format large numbers with B/T suffixes"""
    try:
        num = float(value)
        if num >= 1_000_000_000_000:
            return f"{num / 1_000_000_000_000:.2f}T"
        elif num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        return f"{num:.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value):
    """Format percentage values"""
    try:
        num = float(value)
        return f"{num:+.2f}"  # Include + for positive values
    except (ValueError, TypeError):
        return str(value)

def generate_bitcoin_story_html():
    """Generate Bitcoin Intelligence Story HTML"""
    print("📸 Generating Bitcoin Intelligence Story...")

    # Fetch Bitcoin snapshot
    print("🔍 Fetching Bitcoin snapshot data...")
    btc_snapshot_df = fetch_btc_snapshot()

    if btc_snapshot_df.empty:
        raise Exception("Failed to fetch Bitcoin snapshot data")

    # Convert DataFrame to dict
    btc_snapshot = btc_snapshot_df.to_dict('records')[0]

    # Format data
    btc_snapshot['price'] = format_large_number(btc_snapshot['price'])
    btc_snapshot['market_cap'] = format_large_number(btc_snapshot['market_cap'])
    btc_snapshot['volume24h'] = format_large_number(btc_snapshot['volume24h'])
    btc_snapshot['percent_change24h'] = format_percentage(btc_snapshot['percent_change24h'])
    btc_snapshot['percent_change7d'] = format_percentage(btc_snapshot['percent_change7d'])
    btc_snapshot['percent_change30d'] = format_percentage(btc_snapshot['percent_change30d'])

    # Current timestamp
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")

    # Prepare template context
    context = {
        'snap': [btc_snapshot],
        'current_time': current_time
    }

    # Render template
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template('bitcoin_story.html')
    html_content = template.render(**context)

    # Save HTML
    OUTPUT_HTML_DIR.mkdir(parents=True, exist_ok=True)
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Bitcoin Story HTML generated: {HTML_OUTPUT}")

    # Copy CSS to output directory
    import shutil
    css_source = TEMPLATES_DIR / "style_bitcoin_story.css"
    css_dest = OUTPUT_HTML_DIR / "style_bitcoin_story.css"
    shutil.copy2(css_source, css_dest)
    print(f"📁 Copied style_bitcoin_story.css to output_html directory")

    return HTML_OUTPUT

async def generate_bitcoin_story_screenshot(html_file):
    """Generate screenshot from HTML"""
    print("📸 Generating screenshot...")

    OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Generate screenshot (1080x1920 for Instagram Story)
    # First create a custom screenshot function with story dimensions
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set viewport to Instagram Story size
        await page.set_viewport_size({"width": 1080, "height": 1920})
        await page.emulate_media(media='screen')

        # Load HTML
        await page.goto('file://' + str(html_file.resolve()))

        # Capture screenshot
        await page.screenshot(
            path=str(IMAGE_OUTPUT),
            type='jpeg',
            quality=95,
            full_page=True
        )

        await browser.close()

    print(f"✅ Bitcoin Story screenshot generated: {IMAGE_OUTPUT}")
    return IMAGE_OUTPUT

def post_bitcoin_story_to_instagram(image_path):
    """Post Bitcoin Intelligence Story to Instagram"""
    print("📤 Posting Bitcoin Story to Instagram...")

    # Initialize session manager
    session_mgr = InstagramSessionManager(session_file=str(SESSION_FILE))

    # Get client (bypass validation for stale sessions)
    client = session_mgr.get_client_bypass_validation()

    # Upload story
    media = client.photo_upload_to_story(
        path=str(image_path)
    )

    print(f"✅ Bitcoin Story posted successfully!")
    print(f"📊 Story ID: {media.pk}")

    return media

async def main():
    """Main execution flow"""
    try:
        # Step 1: Generate HTML
        html_file = generate_bitcoin_story_html()

        # Step 2: Generate Screenshot
        image_file = await generate_bitcoin_story_screenshot(html_file)

        # Step 3: Post to Instagram
        media = post_bitcoin_story_to_instagram(image_file)

        print("🎉 Bitcoin Intelligence Story posted successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
