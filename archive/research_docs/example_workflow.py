"""Example: How the new modular system works together"""

# This demonstrates the workflow - you'd actually run complete_workflow.py

import asyncio
import sys
import os

# 1. DATABASE MODULE - Fetches crypto data
from scripts.main.data.database import fetch_top_coins, fetch_btc_snapshot, fetch_global_market_data

# 2. TEMPLATE ENGINE - Renders HTML with data
from scripts.main.content.template_engine import get_template_renderer

# 3. SCREENSHOT MODULE - Converts HTML to images
from scripts.main.media.screenshot import generate_image_from_html

# 4. AI GENERATION - Creates captions
from scripts.main.content.ai_generation import generate_social_media_caption

# 5. GOOGLE SERVICES - Loads spreadsheet data
from scripts.main.integrations.google_services import create_google_services_manager

# 6. INSTAGRAM PUBLISHER - Posts to Instagram
from scripts.main.publishing.instagram import create_instagram_publisher

async def example_complete_workflow():
    """
    Example showing how all modules work together
    """

    print("🚀 NEW MODULAR WORKFLOW EXAMPLE")
    print("=" * 50)

    # STEP 1: Database Module - Clean, focused data fetching
    print("📊 STEP 1: Fetching crypto data...")
    btc_data = fetch_btc_snapshot()
    top_coins = fetch_top_coins(2, 24)  # Ranks 2-24
    global_data = fetch_global_market_data()
    print(f"✅ Fetched {len(top_coins)} coins, BTC data, global metrics")

    # STEP 2: Template Engine - Clean HTML rendering
    print("\n🎨 STEP 2: Rendering templates...")
    renderer = get_template_renderer()

    # Render multiple pages
    pages_rendered = 0
    for page_num in range(1, 7):
        output_path = f"output_html/{page_num}_output.html"

        if page_num == 1:
            success = renderer.render_coins_page('1.html', top_coins, output_path)
        elif page_num == 6:
            news_events = {"past_24h": ["BTC holding support"], "next_24h": ["Watch resistance"]}
            success = renderer.render_btc_snapshot_page('6.html', btc_data, news_events, output_path)
        # ... other pages

        if success:
            pages_rendered += 1

    print(f"✅ Rendered {pages_rendered} HTML pages")

    # STEP 3: Media Processing - Clean screenshot generation
    print("\n📸 STEP 3: Generating screenshots...")
    screenshots_created = 0
    for page_num in range(1, 7):
        html_path = f"output_html/{page_num}_output.html"
        image_path = f"output_images/{page_num}_output.jpg"

        if os.path.exists(html_path):
            await generate_image_from_html(html_path, image_path)
            screenshots_created += 1

    print(f"✅ Created {screenshots_created} screenshots")

    # STEP 4: Google Services - Clean spreadsheet integration
    print("\n📊 STEP 4: Loading spreadsheet data...")
    google_services = create_google_services_manager()
    sheets_data = google_services.load_spreadsheet_data("your_spreadsheet_key")

    # Process the data
    top_gainer, top_loser, _, _, _, _ = google_services.process_top_coins_data(sheets_data)
    top_shorts, top_longs = google_services.process_trading_opportunities(sheets_data)

    print("✅ Processed spreadsheet data for caption generation")

    # STEP 5: AI Generation - Clean caption creation
    print("\n🤖 STEP 5: Generating AI caption...")
    caption = generate_social_media_caption(
        market_data=sheets_data.get('MarketOverview'),
        btc_data=btc_data,
        gainer_data=top_gainer,
        loser_data=top_loser,
        top_shorts=top_shorts,
        top_longs=top_longs
    )
    print(f"✅ Generated caption: {len(caption)} characters")

    # STEP 6: Instagram Publishing - Clean social media posting
    print("\n📱 STEP 6: Publishing to Instagram...")
    drive_service = google_services.get_drive_service()
    instagram_publisher = create_instagram_publisher(drive_service, "drive_file_id")

    success = instagram_publisher.publish_content(
        image_dir="output_images",
        caption=caption,
        num_slides=6
    )

    if success:
        print("✅ Successfully published to Instagram!")
    else:
        print("❌ Publishing failed")

    print("\n🎉 MODULAR WORKFLOW COMPLETE!")
    print("=" * 50)

    return success

# The beauty: Each module can be used independently!

def example_individual_usage():
    """Examples of using modules independently"""

    print("\n🔧 INDIVIDUAL MODULE USAGE EXAMPLES")
    print("=" * 50)

    # Use database module alone
    print("📊 Database Module - Get just BTC data:")
    btc_only = fetch_btc_snapshot()
    print(f"✅ BTC Price: {btc_only['price'].iloc[0] if not btc_only.empty else 'N/A'}")

    # Use AI generation alone
    print("\n🤖 AI Module - Generate caption with custom data:")
    custom_caption = generate_social_media_caption(
        btc_data=btc_only,
        # Other params optional
    )
    print(f"✅ Generated: {custom_caption[:100]}...")

    # Use template engine alone
    print("\n🎨 Template Engine - Render specific page:")
    renderer = get_template_renderer()
    # Could render any template with any data

    print("✅ Each module works independently!")

if __name__ == "__main__":
    # Run the complete example
    asyncio.run(example_complete_workflow())

    # Show individual usage
    example_individual_usage()