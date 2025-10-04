#!/usr/bin/env python3
"""
Instagram Session Status Checker
Utility script to check current session health and information
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from instagram_session_manager import InstagramSessionManager

# Load environment variables
load_dotenv()

def main():
    """Check Instagram session status and health"""
    print("📱 Instagram Session Status Checker")
    print("=" * 50)

    try:
        # Initialize session manager
        session_manager = InstagramSessionManager(
            session_file="data/instagram_session.json",
            username=os.getenv('INSTAGRAM_USERNAME'),
            password=os.getenv('INSTAGRAM_PASSWORD'),
            session_max_age_days=30
        )

        # Get session information
        session_info = session_manager.get_session_info()

        print(f"📁 Session file: {session_manager.session_file}")
        print(f"📁 File exists: {'✅' if session_info['session_file_exists'] else '❌'}")

        if session_info['session_file_exists']:
            print("\n📊 Session Information:")

            # Session age
            if 'session_age_days' in session_info:
                age_days = session_info['session_age_days']
                age_hours = session_info.get('session_age_hours', 0)

                print(f"   ⏰ Age: {age_days} days, {age_hours:.1f} hours")

                if age_days >= 30:
                    print("   ⚠️  Session is old - may need refresh")
                elif age_days >= 20:
                    print("   🟡 Session is aging - consider refresh soon")
                else:
                    print("   ✅ Session age is good")

            # Metadata
            metadata = session_info.get('metadata', {})
            if metadata:
                print(f"   👤 Username: {metadata.get('username', 'Unknown')}")
                print(f"   🔢 Login count: {metadata.get('login_count', 0)}")

                created_at = metadata.get('created_at')
                if created_at:
                    print(f"   📅 Created: {created_at}")

                last_validated = metadata.get('last_validated')
                if last_validated:
                    print(f"   ✅ Last validated: {last_validated}")

        else:
            print("\n❌ No session file found")
            print("   💡 First time usage - session will be created on first login")

        # Test session if it exists
        if session_info['session_file_exists']:
            print(f"\n🔍 Testing session validity...")

            try:
                client = session_manager.get_smart_client()

                if client:
                    print("✅ Session is valid and working!")
                    print(f"👤 Authenticated as: {client.username}")

                    # Update session info after test
                    updated_info = session_manager.get_session_info()
                    print(f"📊 Session health check completed")

                else:
                    print("❌ Session test failed")

            except Exception as e:
                print(f"❌ Session test error: {e}")

        print(f"\n📊 Rate Limiting Protection:")
        print(f"   ⏳ Min login interval: {session_manager.min_login_interval_hours} hours")

        # Check if fresh login is allowed
        if session_manager._should_attempt_fresh_login():
            print("   ✅ Fresh login allowed")
        else:
            print("   ⏳ Fresh login rate limited")

        print(f"\n💡 Tips:")
        print(f"   • Sessions are automatically managed")
        print(f"   • Fresh logins only occur when necessary")
        print(f"   • Sessions last up to 30 days")
        print(f"   • Rate limiting protects your account")

    except Exception as e:
        print(f"❌ Error checking session status: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())