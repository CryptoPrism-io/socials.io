#!/usr/bin/env python3
"""
Generate and post Short Calls Story to Instagram
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
from data.database import fetch_trading_opportunities
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

def format_large_number(value):
    """Format large numbers"""
    try:
        num = float(value)
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.2f}"
        return f"{num:.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value):
    """Format percentage values"""
    try:
        num = float(value)
        return f"{num:.2f}"
    except (ValueError, TypeError):
        return str(value)

def calculate_avg_dmv(positions):
    """Calculate average DMV score"""
    total = 0
    count = 0
    for pos in positions:
        try:
            d = float(pos.get('Durability_Score', 0) or 0)
            m = float(pos.get('Momentum_Score', 0) or 0)
            v = float(pos.get('Valuation_Score', 0) or 0)
            avg = (d + m + v) / 3
            total += avg
            count += 1
        except (ValueError, TypeError):
            continue
    return total / count if count > 0 else 0

def generate_trading_story_html():
    """Generate Short Calls Story HTML"""
    call_type = 'SHORT'
    print(f"📸 Generating {call_type} Calls Story...")

    # Fetch positions
    print(f"🔍 Fetching {call_type} positions...")
    positions_df = fetch_trading_opportunities(opportunity_type=call_type.lower(), limit=15)

    if positions_df.empty:
        raise Exception(f"No {call_type} positions found")

    # Convert to list of dicts
    positions = positions_df.to_dict('records')

    # Format data
    for pos in positions:
        pos['price'] = format_large_number(pos['price'])
        pos['market_cap'] = format_large_number(pos['market_cap'])
        pos['percent_change24h'] = format_percentage(pos['percent_change24h'])

    # Calculate stats
    total_positions = len(positions)
    avg_dmv = calculate_avg_dmv(positions)

    # Current timestamp
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")

    # Prepare template context
    context = {
        'call_type': call_type.upper(),
        'top_positions': positions[:3],  # Top 3 for story
        'total_positions': total_positions,
        'avg_dmv': avg_dmv,
        'current_time': current_time
    }

    # Render template
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template('trading_calls_story.html')
    html_content = template.render(**context)

    # Save HTML
    OUTPUT_HTML_DIR.mkdir(parents=True, exist_ok=True)
    html_output = OUTPUT_HTML_DIR / f"{call_type.lower()}_calls_story_output.html"

    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ {call_type} Calls Story HTML generated: {html_output}")

    # Copy CSS to output directory
    import shutil
    css_source = TEMPLATES_DIR / "style_trading_calls_story.css"
    css_dest = OUTPUT_HTML_DIR / "style_trading_calls_story.css"
    shutil.copy2(css_source, css_dest)
    print(f"📁 Copied style_trading_calls_story.css to output_html directory")

    return html_output

async def generate_trading_story_screenshot(html_file):
    """Generate screenshot from HTML"""
    call_type = 'SHORT'
    print(f"📸 Generating {call_type} Calls screenshot...")

    OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_output = OUTPUT_IMAGES_DIR / f"{call_type.lower()}_calls_story_output.jpg"

    # Generate screenshot (1080x1920 for Instagram Story)
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
            path=str(image_output),
            type='jpeg',
            quality=95,
            full_page=True
        )

        await browser.close()

    print(f"✅ {call_type} Calls Story screenshot generated: {image_output}")
    return image_output

def post_trading_story_to_instagram(image_path):
    """Post Short Calls Story to Instagram"""
    call_type = 'SHORT'
    print(f"📤 Posting {call_type} Calls Story to Instagram...")

    # Initialize session manager
    session_mgr = InstagramSessionManager(session_file=str(SESSION_FILE))

    # Get client (bypass validation for stale sessions)
    client = session_mgr.get_client_bypass_validation()

    # Upload story
    media = client.photo_upload_to_story(
        path=str(image_path)
    )

    print(f"✅ {call_type} Calls Story posted successfully!")
    print(f"📊 Story ID: {media.pk}")

    return media

async def main():
    """Main execution flow"""
    try:
        print(f"\n{'='*60}")
        print(f"Processing SHORT CALLS Story")
        print(f"{'='*60}\n")

        # Step 1: Generate HTML
        html_file = generate_trading_story_html()

        # Step 2: Generate Screenshot
        image_file = await generate_trading_story_screenshot(html_file)

        # Step 3: Post to Instagram
        media = post_trading_story_to_instagram(image_file)

        print(f"🎉 SHORT Calls Story posted successfully!\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
