#!/usr/bin/env python3
"""
Verify Instagram Posting Setup
Checks that session works and can post (dry run test)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main.publishing.session_manager import InstagramSessionManager

def main():
    print("=" * 60)
    print("🔍 Instagram Posting Setup Verification")
    print("=" * 60)

    try:
        # Step 1: Load session
        print("\n📋 Step 1: Loading Instagram session...")
        session_mgr = InstagramSessionManager(
            session_file="data/instagram_session.json",
            username=os.getenv('INSTAGRAM_USERNAME'),
            password=os.getenv('INSTAGRAM_PASSWORD')
        )

        client = session_mgr.get_client_bypass_validation()

        if not client:
            print("❌ Failed to load session")
            print("\n💡 Create a fresh session:")
            print("   python scripts/auth/create_instagram_session.py")
            return 1

        print(f"✅ Session loaded successfully!")
        print(f"   User ID: {client.user_id}")

        # Step 2: Test API authentication
        print("\n📋 Step 2: Testing Instagram API authentication...")
        try:
            account_info = client.account_info()
            print(f"✅ API authenticated!")
            print(f"   Username: {account_info.username}")
            print(f"   Full name: {account_info.full_name}")
        except Exception as api_error:
            print(f"❌ API authentication failed: {api_error}")
            print("\n💡 Session might be invalidated by Instagram")
            print("   Create a fresh session:")
            print("   python scripts/auth/create_instagram_session.py")
            return 1

        # Step 3: Check required images exist
        print("\n📋 Step 3: Checking required carousel images...")
        output_dir = Path("output_images")

        required_images = [
            "6_output.jpg",   # Bitcoin Intelligence
            "1_output.jpg",   # Top Cryptos 2-24
            "2_output.jpg",   # Extended 25-48
            "3_1_output.jpg", # Top Gainers
            "3_2_output.jpg", # Top Losers
            "4_1_output.jpg", # Long Calls
            "4_2_output.jpg", # Short Calls
        ]

        all_exist = True
        for img in required_images:
            img_path = output_dir / img
            if img_path.exists():
                print(f"   ✅ {img}")
            else:
                print(f"   ❌ {img} - MISSING")
                all_exist = False

        if not all_exist:
            print("\n💡 Generate missing templates:")
            print("   See CLAUDE.md for generation commands")
            return 1

        # Step 4: Check API key
        print("\n📋 Step 4: Checking OpenRouter API key...")
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            print(f"✅ OPENROUTER_API_KEY configured")
        else:
            print(f"⚠️  OPENROUTER_API_KEY not set - will use default captions")

        # Summary
        print("\n" + "=" * 60)
        print("🎉 All checks passed!")
        print("=" * 60)
        print("\n✅ Ready to post carousels:")
        print("   python scripts/main/publishing/post_3_carousels.py")
        print("\n⏰ Posting workflow:")
        print("   • Carousel 1: Bitcoin Intelligence + Top Cryptos (3 slides)")
        print("   • Wait 5 minutes")
        print("   • Carousel 2: Top Gainers & Losers (2 slides)")
        print("   • Wait 5 minutes")
        print("   • Carousel 3: Long/Short Calls (2 slides)")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
