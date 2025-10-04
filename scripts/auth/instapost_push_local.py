#!/usr/bin/env python3
"""
Updated Instagram Post Push Script - Local JSON Storage
Simplified version using local JSON storage instead of Google Drive/GCP
Uses OpenRouter API for content generation
"""

import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image
from instagrapi import Client
import requests
import logging
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from instagram_session_manager import InstagramSessionManager

# Load environment variables
load_dotenv()

# Configuration from environment
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
INSTAGRAM_JSON_FILE = os.getenv('INSTAGRAM_JSON_FILE', 'data/instagram_content.json')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Validate environment variables
required_vars = {
    'INSTAGRAM_USERNAME': INSTAGRAM_USERNAME,
    'INSTAGRAM_PASSWORD': INSTAGRAM_PASSWORD,
    'OPENROUTER_API_KEY': OPENROUTER_API_KEY
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    print("❌ Please check your .env file!")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("✅ All environment variables loaded successfully")

class InstagramPoster:
    """Instagram poster with smart session management and local JSON storage"""

    def __init__(self):
        self.instagram_client = None
        self.session_manager = None
        self.content_file = Path(INSTAGRAM_JSON_FILE)
        self.content_file.parent.mkdir(parents=True, exist_ok=True)

    def load_content_data(self):
        """Load content data from local JSON file"""
        if self.content_file.exists():
            with open(self.content_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "generated_content": [],
                "posts_history": [],
                "last_updated": None,
                "templates_used": {},
                "statistics": {
                    "total_posts": 0,
                    "successful_posts": 0,
                    "failed_posts": 0,
                    "templates_usage": {}
                }
            }

    def save_content_data(self, data):
        """Save content data to local JSON file"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.content_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_caption_with_openrouter(self, image_path, template_context=None):
        """Generate Instagram caption using OpenRouter API"""
        try:
            # Prepare prompt based on image and context
            prompt = self._build_caption_prompt(image_path, template_context)

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-3.1-8b-instruct:free",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional crypto social media manager. Create engaging Instagram captions for cryptocurrency content."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7
                }
            )

            if response.status_code == 200:
                result = response.json()
                caption = result['choices'][0]['message']['content']
                print(f"✅ Caption generated successfully")
                return caption
            else:
                print(f"⚠️ OpenRouter API error: {response.status_code}")
                return self._get_fallback_caption()

        except Exception as e:
            print(f"⚠️ Error generating caption: {e}")
            return self._get_fallback_caption()

    def _build_caption_prompt(self, image_path, context=None):
        """Build prompt for caption generation"""
        prompt = f"""
        Create an engaging Instagram caption for a cryptocurrency post featuring an image at {image_path}.

        Requirements:
        - Professional yet engaging tone
        - Include relevant crypto hashtags
        - Keep under 200 words
        - Focus on market insights and trends
        - Use emojis strategically

        """

        if context:
            prompt += f"\nContext: {json.dumps(context, indent=2)}"

        return prompt

    def _get_fallback_caption(self):
        """Fallback caption when AI generation fails"""
        return """🚀 Crypto Market Update 📈

Stay informed with the latest cryptocurrency trends and market movements.

Follow us for daily insights! 💎

#crypto #bitcoin #ethereum #blockchain #investing #trading #cryptoprism #marketupdate #cryptocurrency #defi #web3 #hodl"""

    def smart_login_to_instagram(self):
        """Smart Instagram login with session management and rate limiting protection"""
        try:
            print("🔄 Initializing Instagram session management...")

            # Initialize session manager
            self.session_manager = InstagramSessionManager(
                session_file="data/instagram_session.json",
                username=INSTAGRAM_USERNAME,
                password=INSTAGRAM_PASSWORD,
                session_max_age_days=30
            )

            # Get authenticated client with smart session management
            self.instagram_client = self.session_manager.get_smart_client()

            if self.instagram_client:
                # Display session info
                session_info = self.session_manager.get_session_info()
                print("✅ Instagram authentication successful!")
                print(f"📊 Session age: {session_info.get('session_age_days', 0)} days")
                print(f"👤 Authenticated as: {self.instagram_client.username}")
                return True
            else:
                print("❌ Instagram authentication failed")
                print("\n💡 Possible solutions:")
                print("   • Run: python src/scripts/create_instagram_session.py")
                print("   • Check Instagram credentials in .env file")
                print("   • Disable Two-Factor Authentication temporarily")
                print("   • Log into Instagram manually first")
                print("   • Wait a few hours if rate limited")
                return False

        except Exception as e:
            print(f"❌ Instagram authentication error: {e}")
            logger.error(f"Authentication error: {e}")
            return False

    def login_to_instagram(self):
        """Legacy method - redirects to smart login"""
        return self.smart_login_to_instagram()

    def post_image_with_caption(self, image_path, caption=None, template_name=None):
        """Post image to Instagram with caption"""
        try:
            if not self.instagram_client:
                if not self.smart_login_to_instagram():
                    return False

            # Generate caption if not provided
            if not caption:
                caption = self.generate_caption_with_openrouter(image_path)

            # Post to Instagram
            print(f"🔄 Posting image: {image_path}")
            media = self.instagram_client.photo_upload(image_path, caption)

            # Save session after successful operation
            if self.session_manager and self.session_manager.client:
                try:
                    self.session_manager._save_session()
                    logger.info("✅ Session updated after successful post")
                except Exception as e:
                    logger.warning(f"⚠️ Could not save session: {e}")

            # Update content data
            content_data = self.load_content_data()
            post_record = {
                "timestamp": datetime.now().isoformat(),
                "image_path": str(image_path),
                "template_name": template_name,
                "caption": caption,
                "media_id": str(media.pk) if media else None,
                "status": "success"
            }

            content_data["posts_history"].append(post_record)
            content_data["statistics"]["total_posts"] += 1
            content_data["statistics"]["successful_posts"] += 1

            if template_name:
                content_data["statistics"]["templates_usage"][template_name] = content_data["statistics"]["templates_usage"].get(template_name, 0) + 1

            self.save_content_data(content_data)

            print(f"✅ Successfully posted to Instagram!")
            print(f"📊 Media ID: {media.pk if media else 'N/A'}")
            return True

        except Exception as e:
            print(f"❌ Error posting to Instagram: {e}")

            # Log failed attempt
            content_data = self.load_content_data()
            post_record = {
                "timestamp": datetime.now().isoformat(),
                "image_path": str(image_path),
                "template_name": template_name,
                "caption": caption,
                "error": str(e),
                "status": "failed"
            }

            content_data["posts_history"].append(post_record)
            content_data["statistics"]["total_posts"] += 1
            content_data["statistics"]["failed_posts"] += 1

            self.save_content_data(content_data)
            return False

    def find_latest_generated_images(self, output_dir="output/images"):
        """Find the latest generated images"""
        output_path = Path(output_dir)
        if not output_path.exists():
            print(f"⚠️ Output directory not found: {output_dir}")
            return []

        # Find all JPG files (Instagram posts)
        image_files = list(output_path.glob("*.jpg"))

        if not image_files:
            print(f"⚠️ No images found in {output_dir}")
            return []

        # Sort by modification time (newest first)
        image_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        print(f"✅ Found {len(image_files)} images")
        return image_files

    def post_latest_images(self, max_posts=1):
        """Post the latest generated images"""
        images = self.find_latest_generated_images()

        if not images:
            print("❌ No images to post")
            return False

        success_count = 0
        for i, image_path in enumerate(images[:max_posts]):
            print(f"\n🔄 Processing image {i+1}/{min(max_posts, len(images))}: {image_path.name}")

            # Extract template name from filename
            template_name = image_path.stem

            if self.post_image_with_caption(image_path, template_name=template_name):
                success_count += 1
                print(f"✅ Posted {image_path.name}")

                # Add delay between posts to avoid rate limiting
                if i < min(max_posts, len(images)) - 1:
                    print("⏳ Waiting 30 seconds before next post...")
                    time.sleep(30)
            else:
                print(f"❌ Failed to post {image_path.name}")

        print(f"\n📊 Successfully posted {success_count}/{min(max_posts, len(images))} images")
        return success_count > 0

def main():
    """Main execution function"""
    print("🚀 Instagram Auto-Poster (Local JSON Version)")
    print("=" * 50)

    start_time = time.time()

    # Initialize poster
    poster = InstagramPoster()

    # Post latest images
    success = poster.post_latest_images(max_posts=1)

    # Print timing
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n⏱️ Total execution time: {duration:.2f} seconds")

    if success:
        print("🎉 Instagram posting completed successfully!")
        return 0
    else:
        print("❌ Instagram posting failed!")
        return 1

if __name__ == "__main__":
    exit(main())