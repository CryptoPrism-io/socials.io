#!/usr/bin/env python3
"""
UTF-8 encoding fix for Windows.
Import this at the top of any script to enable Unicode/emoji support.
"""
import sys
import os
import io

def fix_utf8_encoding():
    """Fix UTF-8 encoding for stdout/stderr on Windows."""

    # Set environment variable for Python IO encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'

    # Wrap stdout and stderr with UTF-8 encoding
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Auto-fix when imported
fix_utf8_encoding()

def safe_print(*args, **kwargs):
    """Safe print function with UTF-8 support."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: convert problematic characters
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode('ascii', 'replace').decode('ascii'))
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)

# Test function
def test_unicode():
    """Test Unicode functionality."""
    try:
        print("🚀 Unicode test: 💻🔥👨‍💻🌟")
        return True
    except UnicodeEncodeError:
        print("Unicode test failed - using fallback")
        return False

if __name__ == "__main__":
    print("Testing UTF-8 encoding fix...")
    success = test_unicode()
    print(f"Unicode support: {'✅ Working' if success else '❌ Failed'}")