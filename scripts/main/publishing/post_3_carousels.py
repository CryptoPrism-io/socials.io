#!/usr/bin/env python3
"""
Instagram 3-Carousel Poster - Post Split Template Collections
Carousel 1: Templates 7, 1, 2 (Market Intelligence + Top Cryptos)
Carousel 2: Templates 3.1, 3.2 (Top Gainers & Losers)
Carousel 3: Templates 4.1, 4.2 (Long/Short Call Positions)
"""

import json
import os
import sys
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired, ClientError
except ImportError:
    print("Missing instagrapi. Install with: pip install instagrapi")
    sys.exit(1)

from session_manager import InstagramSessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThreeCarouselPoster:
    """Post 3 separate carousels to Instagram"""

    def __init__(self, session_file: str = "data/instagram_session.json"):
        """Initialize poster with session file"""
        self.session_file = session_file
        self.client = None
        self.post_results = []

    def load_session_bypass(self) -> bool:
        """Load Instagram session using bypass validation"""
        try:
            logger.info("🔄 Loading Instagram session with bypass validation...")

            session_manager = InstagramSessionManager(
                session_file=self.session_file,
                username=os.getenv('INSTAGRAM_USERNAME'),
                password=os.getenv('INSTAGRAM_PASSWORD')
            )

            self.client = session_manager.get_client_bypass_validation()

            if self.client:
                logger.info("✅ Session loaded successfully using bypass method!")
                return True
            else:
                logger.error("❌ Failed to load session")
                return False

        except Exception as e:
            logger.error(f"❌ Error loading session: {e}")
            return False

    def generate_ai_caption(self, carousel_name: str, templates: List[str]) -> str:
        """Generate AI caption for specific carousel"""
        try:
            import requests

            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                logger.warning("⚠️ No OPENROUTER_API_KEY, using default caption")
                return self._get_default_caption(carousel_name)

            logger.info(f"🤖 Generating AI caption for {carousel_name}...")

            prompts = {
                "Carousel 1": """Create an engaging Instagram caption for a crypto carousel with 3 slides:
1. Bitcoin + Macro Intelligence (Fear & Greed Index + BTC price data)
2. Top Cryptocurrencies (ranks 2-24)
3. Extended Cryptocurrencies (ranks 25-48)

Caption should:
- Be professional but engaging
- Mention Bitcoin focus and comprehensive market overview
- Include 3-5 relevant hashtags
- Be under 150 characters
- Include 1-2 emojis

Just return the caption, nothing else.""",

                "Carousel 2": """Create an engaging Instagram caption for a crypto carousel showing:
1. Top Gainers (+2% or more in 24h)
2. Top Losers (-2% or more in 24h)

Caption should:
- Be energetic and market-focused
- Mention volatile movers
- Include 3-5 trading/crypto hashtags
- Be under 120 characters
- Include relevant emojis

Just return the caption, nothing else.""",

                "Carousel 3": """Create an engaging Instagram caption for a crypto trading carousel showing:
1. Long Call Positions (bullish opportunities)
2. Short Call Positions (bearish opportunities)

Caption should:
- Be professional and trading-focused
- Mention trading opportunities
- Include 3-5 trading hashtags
- Be under 120 characters
- Include relevant emojis

Just return the caption, nothing else."""
            }

            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompts.get(carousel_name, prompts["Carousel 1"])}]
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                caption = result['choices'][0]['message']['content'].strip()
                logger.info(f"✅ AI caption: {caption[:80]}...")
                return caption
            else:
                logger.warning(f"⚠️ AI failed ({response.status_code}), using default")
                return self._get_default_caption(carousel_name)

        except Exception as e:
            logger.warning(f"⚠️ Error generating AI caption: {e}")
            return self._get_default_caption(carousel_name)

    def _get_default_caption(self, carousel_name: str) -> str:
        """Get default captions for each carousel"""
        captions = {
            "Carousel 1": """📊 Bitcoin Intelligence + Market Overview

🪙 Bitcoin + Macro Intelligence
💎 Top 48 Cryptocurrencies
📈 Fear & Greed Index + Real-time Data

#bitcoin #crypto #cryptocurrency #marketanalysis #trading""",

            "Carousel 2": """🚀 Today's Biggest Movers

📈 Top Gainers (+2%+)
📉 Top Losers (-2%+)

#crypto #trading #cryptocurrency #volatility #marketmovers""",

            "Carousel 3": """📊 Trading Opportunities Alert

🟢 Long Call Positions
🔴 Short Call Positions

#cryptotrading #trading #cryptocurrency #tradingopportunities #analysis"""
        }
        return captions.get(carousel_name, captions["Carousel 1"])

    def post_carousel(self, carousel_name: str, image_paths: List[str], caption: str) -> Optional[str]:
        """Post single carousel to Instagram"""
        try:
            if not self.client:
                logger.error("❌ Client not initialized")
                return None

            # Validate images exist
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    logger.error(f"❌ Image not found: {img_path}")
                    return None

            logger.info(f"📤 Posting {carousel_name} with {len(image_paths)} images...")
            logger.info(f"📝 Caption: {caption[:100]}...")

            # Post carousel
            media = self.client.album_upload(
                paths=image_paths,
                caption=caption
            )

            media_id = str(media.pk) if hasattr(media, 'pk') else str(media)
            logger.info(f"✅ {carousel_name} posted! Media ID: {media_id}")

            return media_id

        except Exception as e:
            logger.error(f"❌ Error posting {carousel_name}: {e}")
            return None

    def post_all_carousels(self, delay_between_posts: int = 300):
        """
        Post all 3 carousels with delays between them

        Args:
            delay_between_posts: Seconds to wait between posts (default: 5 minutes)
        """
        output_dir = Path("output_images")

        # Define carousel configurations
        carousels = [
            {
                "name": "Carousel 1",
                "description": "Bitcoin Intelligence + Top Cryptos",
                "images": [
                    str(output_dir / "6_output.jpg"),  # Bitcoin + Macro Intelligence
                    str(output_dir / "1_output.jpg"),  # Top Cryptos 2-24
                    str(output_dir / "2_output.jpg"),  # Extended Cryptos 25-48
                ]
            },
            {
                "name": "Carousel 2",
                "description": "Top Gainers & Losers",
                "images": [
                    str(output_dir / "3_1_output.jpg"),  # Top Gainers
                    str(output_dir / "3_2_output.jpg"),  # Top Losers
                ]
            },
            {
                "name": "Carousel 3",
                "description": "Long/Short Call Positions",
                "images": [
                    str(output_dir / "4_1_output.jpg"),  # Long Calls
                    str(output_dir / "4_2_output.jpg"),  # Short Calls
                ]
            }
        ]

        logger.info("=" * 70)
        logger.info("🚀 Starting 3-Carousel Posting Sequence")
        logger.info("=" * 70)

        for i, carousel_config in enumerate(carousels, 1):
            carousel_name = carousel_config["name"]
            description = carousel_config["description"]
            images = carousel_config["images"]

            logger.info("")
            logger.info(f"📌 {carousel_name}: {description}")
            logger.info(f"🖼️  Images: {len(images)}")

            # Generate caption
            caption = self.generate_ai_caption(carousel_name, images)

            # Post carousel
            media_id = self.post_carousel(carousel_name, images, caption)

            # Record result
            result = {
                "carousel": carousel_name,
                "description": description,
                "media_id": media_id,
                "success": media_id is not None,
                "posted_at": datetime.now().isoformat() if media_id else None
            }
            self.post_results.append(result)

            if media_id:
                logger.info(f"✅ {carousel_name} SUCCESS - Media ID: {media_id}")
            else:
                logger.error(f"❌ {carousel_name} FAILED")

            # Wait between posts (except after last one)
            if i < len(carousels):
                logger.info(f"⏳ Waiting {delay_between_posts} seconds before next post...")
                time.sleep(delay_between_posts)

        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 POSTING SUMMARY")
        logger.info("=" * 70)

        successful = sum(1 for r in self.post_results if r['success'])
        failed = len(self.post_results) - successful

        logger.info(f"✅ Successful: {successful}/{len(self.post_results)}")
        logger.info(f"❌ Failed: {failed}/{len(self.post_results)}")

        for result in self.post_results:
            status = "✅" if result['success'] else "❌"
            logger.info(f"{status} {result['carousel']}: {result.get('media_id', 'FAILED')}")

        logger.info("=" * 70)

        return self.post_results

def main():
    """Main execution"""
    logger.info("=" * 70)
    logger.info("🎯 Instagram 3-Carousel Poster - Stale Session Method")
    logger.info("=" * 70)

    # Initialize poster
    poster = ThreeCarouselPoster()

    # Load session
    if not poster.load_session_bypass():
        logger.error("❌ Failed to load session. Exiting.")
        return

    # Post all carousels with 5-minute delays
    results = poster.post_all_carousels(delay_between_posts=300)

    # Exit with appropriate code
    if all(r['success'] for r in results):
        logger.info("🎉 All carousels posted successfully!")
        sys.exit(0)
    else:
        logger.error("⚠️ Some carousels failed to post")
        sys.exit(1)

if __name__ == "__main__":
    main()
