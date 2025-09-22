#!/usr/bin/env python3
"""
Environment validation script for socialio project.
Checks if all required environment variables are properly set.
"""
import os
from pathlib import Path

# Load environment variables from .env file
def load_env():
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("+ .env file loaded successfully")
    else:
        print("! .env file not found")

# Required environment variables for socialio
REQUIRED_VARS = [
    'GCP_CREDENTIALS',
    'TOGETHER_API_KEY',
    'INSTAGRAM_DRIVE_FILE_ID',
    'CRYPTO_SPREADSHEET_KEY',
    'INSTAGRAM_USERNAME',
    'INSTAGRAM_PASSWORD'
]

# Optional but recommended variables
OPTIONAL_VARS = [
    'OPENROUTER_API_KEY'
]

def validate_environment():
    """Validate all required environment variables."""
    print("=" * 50)
    print("ENVIRONMENT VARIABLES VALIDATION")
    print("=" * 50)

    load_env()

    missing_required = []
    present_required = []
    present_optional = []

    # Check required variables
    for var in REQUIRED_VARS:
        if var in os.environ and os.environ[var]:
            present_required.append(var)
            print(f"+ {var}: Present")
        else:
            missing_required.append(var)
            print(f"- {var}: Missing")

    # Check optional variables
    for var in OPTIONAL_VARS:
        if var in os.environ and os.environ[var]:
            present_optional.append(var)
            print(f"+ {var}: Present (optional)")

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Required variables present: {len(present_required)}/{len(REQUIRED_VARS)}")
    print(f"Optional variables present: {len(present_optional)}/{len(OPTIONAL_VARS)}")

    if missing_required:
        print(f"\nMissing required variables:")
        for var in missing_required:
            print(f"  - {var}")
        print(f"\nTo fix: Add these variables to your .env file")
        return False
    else:
        print(f"\n+ All required environment variables are present!")
        return True

if __name__ == "__main__":
    success = validate_environment()
    exit(0 if success else 1)