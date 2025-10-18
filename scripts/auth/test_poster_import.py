#!/usr/bin/env python3
"""
Test that posting script can import and initialize properly
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing imports...")

try:
    from main.publishing.post_3_carousels import ThreeCarouselPoster
    print("✅ Successfully imported ThreeCarouselPoster")

    print("\nInitializing poster...")
    poster = ThreeCarouselPoster()
    print("✅ Poster initialized")

    print("\nLoading session...")
    if poster.load_session_bypass():
        print("✅ Session loaded successfully!")
        print(f"   Client authenticated: {poster.client is not None}")
        if poster.client:
            print(f"   User ID: {poster.client.user_id}")

            # Test account info call
            print("\nTesting API call...")
            try:
                account = poster.client.account_info()
                print(f"✅ API call successful!")
                print(f"   Username: {account.username}")
                print("\n🎉 Posting script is ready to use!")
            except Exception as api_err:
                print(f"❌ API call failed: {api_err}")
    else:
        print("❌ Failed to load session")

except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
