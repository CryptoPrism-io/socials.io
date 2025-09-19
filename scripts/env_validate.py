#!/usr/bin/env python3
"""
Environment Validation Script for socials.io
Tests all required credentials and connections
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from config import config
from sqlalchemy import create_engine
import pandas as pd

def test_database_connection():
    """Test PostgreSQL connection and basic functionality."""
    print("🔍 Testing database connection...")
    try:
        engine = create_engine(config.database.get_connection_url())
        df = pd.read_sql_query("SELECT 1 as test", engine)
        print("✅ Database: Connection successful")
        return True
    except Exception as e:
        print(f"❌ Database: Connection failed - {e}")
        return False

def test_openrouter_api():
    """Test OpenRouter API key format (light validation)."""
    print("🔍 Testing OpenRouter API key...")
    if hasattr(config.api, 'openrouter_api_key') and config.api.openrouter_api_key:
        if config.api.openrouter_api_key.startswith('sk-or-v1-'):
            print("✅ OpenRouter API: Key format looks correct")
            return True
        else:
            print("❌ OpenRouter API: Invalid key format")
            return False
    else:
        print("❌ OpenRouter API: Key not configured")
        return False

def test_google_credentials():
    """Test Google Cloud credentials format."""
    print("🔍 Testing Google Cloud Platform...")
    if hasattr(config.api, 'google_credentials') and config.api.google_credentials:
        try:
            import json
            creds = json.loads(config.api.google_credentials) if isinstance(config.api.google_credentials, str) else config.api.google_credentials
            if 'type' in creds and creds.get('type') == 'service_account':
                print("✅ GCP: Service account credentials found")
                return True
            else:
                print("❌ GCP: Invalid service account format")
                return False
        except (json.JSONDecodeError, TypeError):
            print("❌ GCP: Invalid JSON format in credentials")
            return False
    else:
        print("❌ GCP: Credentials not configured")
        return False

def test_together_api():
    """Test Together AI API key."""
    print("🔍 Testing Together AI API...")
    if hasattr(config.api, 'together_api_key') and config.api.together_api_key:
        if config.api.together_api_key.startswith('sk-'):
            print("✅ Together AI: API key format looks correct")
            return True
        else:
            print("❌ Together AI: Invalid key format")
            return False
    else:
        print("❌ Together AI: Key not configured")
        return False

def test_instagram_credentials():
    """Test Instagram account configuration."""
    print("🔍 Testing Instagram credentials...")
    username_ok = hasattr(config.api, 'instagram_username') and config.api.instagram_username
    password_ok = hasattr(config.api, 'instagram_password') and config.api.instagram_password

    if username_ok and password_ok:
        print("✅ Instagram: Credentials configured")
        return True
    elif username_ok or password_ok:
        print("⚠️  Instagram: Partial credentials found")
        return False
    else:
        print("❌ Instagram: Credentials not configured")
        return False

def test_google_sheets():
    """Test Google Sheets configuration."""
    print("🔍 Testing Google Sheets...")
    if hasattr(config.api, 'google_sheets_key') and config.api.google_sheets_key:
        # Basic format validation
        if len(config.api.google_sheets_key) > 20:
            print("✅ Google Sheets: Spreadsheet key configured")
            return True
        else:
            print("❌ Google Sheets: Invalid key format")
            return False
    else:
        print("❌ Google Sheets: Key not configured")
        return False

def test_google_drive():
    """Test Google Drive configuration."""
    print("🔍 Testing Google Drive...")
    if hasattr(config.api, 'google_drive_file_id') and config.api.google_drive_file_id:
        if len(config.api.google_drive_file_id) > 10:
            print("✅ Google Drive: Folder ID configured")
            return True
        else:
            print("❌ Google Drive: Invalid ID format")
            return False
    else:
        print("❌ Google Drive: ID not configured")
        return False

def main():
    """Run all environment validation tests."""
    print("🧪 socials.io Environment Validation\n")
    print("=" * 50)

    tests = [
        test_database_connection,
        test_openrouter_api,
        test_google_credentials,
        test_together_api,
        test_instagram_credentials,
        test_google_sheets,
        test_google_drive
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        test()
        print()

    # Rerun tests to count passed ones
    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
            else:
                print()
        except Exception as e:
            print(f"❌ {test.__name__.replace('_', ' ').title()}: Test failed with error - {e}")
            print()

    print("=" * 50)
    print("📊 FINAL SUMMARY:")
    print(f"✅ Passed: {passed}/{total} ({(passed/total)*100:.1f}%)")

    # Critical requirements for operation
    critical_passed = test_database_connection() and test_openrouter_api()
    if critical_passed and passed >= total * 0.8:
        print("🚀 STATUS: Ready for operation!")
    elif critical_passed:
        print("⚠️  STATUS: Core functionality ready, some optional features missing")
    else:
        print("❌ STATUS: Core functionality not ready - database or API key issues")

if __name__ == "__main__":
    main()