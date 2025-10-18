#!/usr/bin/env python3
"""
Quick Instagram Session Test
Verifies that the session can authenticate with Instagram
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main.publishing.session_manager import InstagramSessionManager

# Load environment
load_dotenv()

def main():
    print("=" * 60)
    print("🔍 Instagram Session Authentication Test")
    print("=" * 60)

    try:
        # Initialize session manager
        session_mgr = InstagramSessionManager(
            session_file="data/instagram_session.json",
            username=os.getenv('INSTAGRAM_USERNAME'),
            password=os.getenv('INSTAGRAM_PASSWORD')
        )

        print("\n📊 Session File Info:")
        info = session_mgr.get_session_info()
        print(f"   Session exists: {info['session_file_exists']}")

        if info.get('session_age_days') is not None:
            print(f"   Session age: {info['session_age_days']} days, {info.get('session_age_hours', 0):.1f} hours")

        metadata = info.get('metadata', {})
        if metadata:
            print(f"   Created: {metadata.get('created_at', 'Unknown')}")
            print(f"   Last validated: {metadata.get('last_validated', 'Unknown')}")
            print(f"   Login count: {metadata.get('login_count', 0)}")

        print("\n🔄 Loading session and testing authentication...")

        # Use bypass method to avoid instagrapi validation bugs
        client = session_mgr.get_client_bypass_validation()

        if client:
            print(f"✅ Session loaded successfully!")
            print(f"   User ID: {client.user_id}")

            # Try a simple API call to verify session works
            print("\n🧪 Testing API call with session...")
            try:
                # Get account info - lightweight test
                account_info = client.account_info()
                print(f"✅ API call successful!")
                print(f"   Username: {account_info.username}")
                print(f"   Full name: {account_info.full_name}")
                print(f"\n🎉 Session is VALID and working!")
                return 0

            except Exception as api_error:
                print(f"❌ API call failed: {api_error}")
                print(f"\n⚠️  Session loaded but API test failed")
                print(f"   This usually means Instagram invalidated the session")
                print(f"\n💡 Solution: Create a fresh session")
                print(f"   Run: python scripts/auth/create_instagram_session.py")
                return 1
        else:
            print(f"❌ Failed to load session")
            print(f"\n💡 Solution: Create a fresh session")
            print(f"   Run: python scripts/auth/create_instagram_session.py")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())