#!/usr/bin/env python3
"""
Instagram Story Teaser Poster
Posts a single Instagram Story to drive traffic to main carousel post

Features:
- Psychological hooks (FOMO, Urgency, Scarcity)
- Dynamic data from database (top gainer, loser, Bitcoin price)
- Automatic hook selection based on market conditions
- Instagram Story format (1080x1920)
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

from scripts.main.data.database import fetch_top_coins, fetch_btc_snapshot
from scripts.main.publishing.session_manager import InstagramSessionManager

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Missing playwright. Install with: pip install playwright")
    sys.exit(1)

try:
    from jinja2 import Template, Environment, FileSystemLoader
except ImportError:
    print("Missing jinja2. Install with: pip install jinja2")
    sys.exit(1)


class StoryTeaserPoster:
    """Generate and post Instagram Story teaser"""

    def __init__(self):
        """Initialize poster"""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.templates_dir = self.project_root / 'base_templates'
        self.output_html_dir = self.project_root / 'output_html'
        self.output_images_dir = self.project_root / 'output_images'

        # Create output directories
        self.output_html_dir.mkdir(exist_ok=True)
        self.output_images_dir.mkdir(exist_ok=True)

    def fetch_market_data(self):
        """
        Fetch market data for story teaser

        Returns:
            dict: Market data including top gainer, loser, BTC price
        """
        print("📊 Fetching market data...")

        try:
            # Fetch top 100 coins for analysis
            df = fetch_top_coins(1, 100)

            if df.empty:
                print("❌ No crypto data available")
                return None

            # Get top gainer
            top_gainer = df.nlargest(1, 'percent_change24h').iloc[0]

            # Get top loser
            top_loser = df.nsmallest(1, 'percent_change24h').iloc[0]

            # Get Bitcoin data
            btc_data = fetch_btc_snapshot()

            if btc_data.empty:
                print("❌ No Bitcoin data available")
                return None

            # Price comes as formatted string like "$123456.78", extract number
            btc_price_str = btc_data.iloc[0]['price']
            btc_price_clean = btc_price_str.replace('$', '').replace(',', '')
            btc_price_float = float(btc_price_clean)

            market_data = {
                'top_gainer_symbol': top_gainer['symbol'],
                'top_gainer_percent': abs(round(top_gainer['percent_change24h'], 1)),
                'top_loser_symbol': top_loser['symbol'],
                'top_loser_percent': round(top_loser['percent_change24h'], 1),
                'btc_price': f"{btc_price_float:,.0f}",
                'top_gainer_raw': top_gainer['percent_change24h'],
                'top_loser_raw': top_loser['percent_change24h'],
            }

            print(f"✅ Market data fetched:")
            print(f"   Top Gainer: {market_data['top_gainer_symbol']} +{market_data['top_gainer_percent']}%")
            print(f"   Top Loser: {market_data['top_loser_symbol']} {market_data['top_loser_percent']}%")
            print(f"   Bitcoin: ${market_data['btc_price']}")

            return market_data

        except Exception as e:
            print(f"❌ Error fetching market data: {e}")
            import traceback
            traceback.print_exc()
            return None

    def select_psychological_hook(self, market_data):
        """
        Select optimal psychological hook based on market conditions

        Args:
            market_data: Dict with market stats

        Returns:
            str: Hook text to use in story
        """
        top_gainer_pct = market_data['top_gainer_raw']
        top_loser_pct = abs(market_data['top_loser_raw'])

        # FOMO Hook: Big mover detected (>15%)
        if top_gainer_pct > 15:
            hook = f"While you were sleeping..."
            print(f"🎯 Selected FOMO hook (big gainer: +{top_gainer_pct:.1f}%)")

        # Urgency Hook: High volatility (big gainer OR big loser)
        elif top_gainer_pct > 10 or top_loser_pct > 10:
            hook = "⚡ Markets moving fast..."
            print(f"🎯 Selected Urgency hook (high volatility)")

        # Default: Scarcity Hook (always effective)
        else:
            hook = "While others scroll for hours..."
            print(f"🎯 Selected Scarcity hook (default)")

        return hook

    def generate_story_html(self, market_data, hook_text):
        """
        Generate HTML for Instagram Story

        Args:
            market_data: Market statistics
            hook_text: Psychological hook text

        Returns:
            str: Path to generated HTML file
        """
        print("🎨 Generating story HTML...")

        try:
            # Load Jinja2 template
            env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
            template = env.get_template('story_teaser.html')

            # Render template with data
            html_content = template.render(
                hook_text=hook_text,
                top_gainer_symbol=market_data['top_gainer_symbol'],
                top_gainer_percent=market_data['top_gainer_percent'],
                top_loser_symbol=market_data['top_loser_symbol'],
                top_loser_percent=market_data['top_loser_percent'],
                btc_price=market_data['btc_price']
            )

            # Save HTML
            output_path = self.output_html_dir / 'story_teaser_output.html'
            output_path.write_text(html_content, encoding='utf-8')

            print(f"✅ Story HTML generated: {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"❌ Error generating HTML: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def screenshot_story(self, html_path):
        """
        Generate Instagram Story screenshot from HTML

        Args:
            html_path: Path to HTML file

        Returns:
            str: Path to generated image
        """
        print("📸 Generating story screenshot...")

        output_path = self.output_images_dir / 'story_teaser_output.jpg'

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    viewport={'width': 1080, 'height': 1920},
                    device_scale_factor=1
                )

                # Load HTML file
                await page.goto(f'file:///{html_path}')

                # Wait for fonts to load
                await page.wait_for_timeout(1000)

                # Take screenshot (Instagram Story dimensions: 1080x1920)
                await page.screenshot(
                    path=str(output_path),
                    type='jpeg',
                    quality=95,
                    full_page=False
                )

                await browser.close()

            print(f"✅ Story screenshot generated: {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"❌ Error generating screenshot: {e}")
            import traceback
            traceback.print_exc()
            return None

    def post_to_instagram(self, image_path):
        """
        Post story to Instagram

        Args:
            image_path: Path to story image

        Returns:
            bool: Success status
        """
        print("\n📱 Posting story to Instagram...")

        try:
            # Initialize session manager
            session_mgr = InstagramSessionManager(
                session_file="data/instagram_session.json"
            )

            # Get Instagram client
            client = session_mgr.get_client_bypass_validation()

            print(f"👤 Logged in as: {client.username}")

            # Post story
            print("🚀 Uploading story...")
            story = client.photo_upload_to_story(
                path=image_path
            )

            print(f"✅ Story posted successfully!")
            print(f"📱 Story ID: {story.pk}")

            return True

        except Exception as e:
            print(f"❌ Error posting story: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main execution flow"""
    print("\n" + "=" * 70)
    print("📱 INSTAGRAM STORY TEASER POSTER")
    print("Drive traffic to main carousel with psychological hooks")
    print("=" * 70)

    start_time = datetime.now()

    # Initialize poster
    poster = StoryTeaserPoster()

    # Step 1: Fetch market data
    market_data = poster.fetch_market_data()

    if not market_data:
        print("\n❌ Failed to fetch market data. Aborting.")
        return 1

    # Step 2: Select psychological hook
    hook_text = poster.select_psychological_hook(market_data)

    # Step 3: Generate story HTML
    html_path = poster.generate_story_html(market_data, hook_text)

    if not html_path:
        print("\n❌ Failed to generate HTML. Aborting.")
        return 1

    # Step 4: Screenshot story
    image_path = await poster.screenshot_story(html_path)

    if not image_path:
        print("\n❌ Failed to generate screenshot. Aborting.")
        return 1

    # Step 5: Post to Instagram
    success = poster.post_to_instagram(image_path)

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 70)
    print("📊 EXECUTION SUMMARY")
    print("=" * 70)
    print(f"⏱️  Duration: {duration:.1f} seconds")
    print(f"🎯 Hook Used: {hook_text}")
    print(f"✅ Posted to Instagram: {'Yes' if success else 'No'}")
    print("=" * 70)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
