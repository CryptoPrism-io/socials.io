#!/usr/bin/env python3
"""
Post 14-Slide Mega-Carousel to Instagram
Generates all slides and posts them as a single cohesive carousel

Order:
1. Cover
2. Index
3. Section Intro - Bitcoin
4. Bitcoin Data (Template 6)
5. Section Intro - Trading
6. Long Calls (Template 4.1)
7. Short Calls (Template 4.2)
8. Section Intro - Market Movers
9. Top Gainers (Template 3.1)
10. Top Losers (Template 3.2)
11. Section Intro - Top Cryptos
12. Top Cryptos 2-24 (Template 1)
13. Extended 25-48 (Template 2)
14. CTA
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

from scripts.main.publishing.session_manager import InstagramSessionManager
from scripts.main.content.openrouter_client import OpenRouterClient

# Import all generator functions
sys.path.insert(0, str(Path(__file__).parent.parent / 'individual_posts'))

async def generate_all_slides():
    """
    Generate all 14 slides in sequence
    Returns list of image paths in correct order
    """
    import subprocess

    print("🎬 Generating All 14 Mega-Carousel Slides...")
    print("=" * 70)

    output_images = Path(__file__).parent.parent.parent.parent / 'output_images'
    scripts_dir = Path(__file__).parent.parent / 'individual_posts'

    # Define generation sequence
    generators = [
        # (slide_number, script_name, output_file, description)
        (1, 'generate_cover_output.py', 'cover_output.jpg', 'Cover'),
        (2, 'generate_index_output.py', 'index_output.jpg', 'Index'),
        (3, 'generate_section_intro.py bitcoin', 'section_intro_bitcoin_output.jpg', 'Section Intro - Bitcoin'),
        (4, 'generate_6_output.py', '6_output.jpg', 'Bitcoin & Market Intelligence'),
        (5, 'generate_section_intro.py trading', 'section_intro_trading_output.jpg', 'Section Intro - Trading'),
        (6, 'generate_4_1_output.py', '4_1_output.jpg', 'Long Call Positions'),
        (7, 'generate_4_2_output.py', '4_2_output.jpg', 'Short Call Positions'),
        (8, 'generate_section_intro.py movers', 'section_intro_movers_output.jpg', 'Section Intro - Market Movers'),
        (9, 'generate_3_1_output.py', '3_1_output.jpg', 'Top Gainers'),
        (10, 'generate_3_2_output.py', '3_2_output.jpg', 'Top Losers'),
        (11, 'generate_section_intro.py top_cryptos', 'section_intro_top_cryptos_output.jpg', 'Section Intro - Top Cryptos'),
        (12, 'generate_1_output.py', '1_output.jpg', 'Top Cryptos 2-24'),
        (13, 'generate_2_output.py', '2_output.jpg', 'Extended Cryptos 25-48'),
        (14, 'generate_cta_output.py', 'cta_output.jpg', 'CTA'),
    ]

    slides = []

    try:
        for slide_num, script_cmd, output_file, description in generators:
            print(f"\n[{slide_num}/14] Generating {description}...")

            # Parse script command (handle scripts with arguments)
            parts = script_cmd.split()
            script_name = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            script_path = scripts_dir / script_name

            # Run generator script
            cmd = ['python', str(script_path)] + args
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ Error running {script_name}:")
                print(result.stderr)
                return None

            # Add slide path
            slide_path = output_images / output_file
            if not slide_path.exists():
                print(f"❌ ERROR: Output file not found: {slide_path}")
                return None

            slides.append(str(slide_path))
            print(f"✅ {description} generated")

        print("\n" + "=" * 70)
        print(f"✅ All {len(slides)} slides generated successfully!")
        print("=" * 70)

        return slides

    except Exception as e:
        print(f"❌ Error generating slides: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_ai_caption(slides_count=14):
    """
    Generate AI caption for mega-carousel using OpenRouter

    Args:
        slides_count: Number of slides in carousel

    Returns:
        str: Generated caption
    """
    print("\n🤖 Generating AI Caption...")

    try:
        client = OpenRouterClient()

        prompt = f"""Generate a compelling Instagram caption for a {slides_count}-slide crypto market analysis carousel.

The carousel contains:
- Cover slide with market pulse branding
- Index overview of all sections
- Bitcoin & Market Intelligence (Fear & Greed + BTC analysis)
- Trading Opportunities (Long & Short calls with DMV scores)
- Market Movers (Top gainers & losers)
- Top Cryptocurrencies (Rankings 2-48)
- Call-to-action to follow

Caption requirements:
- 2-3 sentences maximum
- Professional yet engaging tone
- Include relevant crypto hashtags (max 5)
- Emphasize data-driven insights and daily updates
- No emojis in main text (hashtags okay)

Example structure:
[Hook sentence about market intelligence]
[Value proposition]

#CryptoAnalysis #Bitcoin #Trading #MarketData #CryptoInvesting"""

        caption = client.generate_caption(
            model="openai/gpt-4o-mini",
            prompt=prompt
        )

        print(f"✅ AI Caption Generated:\n{caption}\n")
        return caption

    except Exception as e:
        print(f"⚠️  AI caption generation failed: {str(e)}")
        print("📝 Using default caption...")

        # Fallback caption
        return """Your complete crypto market intelligence for today. 14 slides covering Bitcoin analysis, trading opportunities, market movers, and top cryptocurrencies with data-driven insights.

Follow @cryptoprism.io for daily market updates.

#CryptoAnalysis #Bitcoin #Trading #MarketData #CryptoInvesting"""

def post_to_instagram(slide_paths, caption):
    """
    Post mega-carousel to Instagram

    Args:
        slide_paths: List of image file paths
        caption: Instagram caption

    Returns:
        bool: Success status
    """
    print("\n📸 Posting Mega-Carousel to Instagram...")
    print(f"📊 Slides: {len(slide_paths)}")
    print(f"💬 Caption Length: {len(caption)} characters")

    try:
        # Initialize session manager
        session_mgr = InstagramSessionManager(
            session_file="data/instagram_session.json"
        )

        # Get Instagram client (bypass validation for stale sessions)
        client = session_mgr.get_client_bypass_validation()

        print(f"👤 Logged in as: {client.username}")

        # Post carousel
        print(f"\n🚀 Uploading {len(slide_paths)} slides to Instagram...")
        media = client.album_upload(
            paths=slide_paths,
            caption=caption
        )

        print(f"\n✅ Mega-carousel posted successfully!")
        print(f"📱 Media ID: {media.pk}")
        print(f"🔗 Post URL: https://www.instagram.com/p/{media.code}/")

        return True

    except Exception as e:
        print(f"\n❌ Error posting to Instagram: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main execution flow"""
    print("\n" + "=" * 70)
    print("🎨 MEGA-CAROUSEL GENERATOR & POSTER")
    print("14-Slide Instagram Carousel")
    print("=" * 70)

    start_time = datetime.now()

    # Step 1: Generate all slides
    slide_paths = await generate_all_slides()

    if not slide_paths:
        print("\n❌ Slide generation failed. Aborting.")
        return 1

    # Step 2: Generate AI caption
    caption = generate_ai_caption(slides_count=len(slide_paths))

    # Step 3: Post to Instagram
    success = post_to_instagram(slide_paths, caption)

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 70)
    print("📊 EXECUTION SUMMARY")
    print("=" * 70)
    print(f"⏱️  Duration: {duration:.1f} seconds")
    print(f"📸 Slides Generated: {len(slide_paths)}")
    print(f"✅ Posted to Instagram: {'Yes' if success else 'No'}")
    print("=" * 70)

    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
