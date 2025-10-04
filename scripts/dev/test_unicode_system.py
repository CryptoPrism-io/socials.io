#!/usr/bin/env python3
"""
System-wide Unicode validation script.
Tests if UTF-8 encoding is working without any script-level fixes.
This should work automatically if system-level UTF-8 is properly configured.
"""
import sys
import os
import locale
import platform

def test_encoding_settings():
    """Test and display current encoding settings."""
    print("=" * 60)
    print("SYSTEM UNICODE VALIDATION")
    print("=" * 60)

    # System information
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python version: {sys.version}")
    print()

    # Encoding information
    print("ENCODING SETTINGS:")
    print(f"  Default encoding: {sys.getdefaultencoding()}")
    print(f"  Stdout encoding: {sys.stdout.encoding}")
    print(f"  Stderr encoding: {sys.stderr.encoding}")
    print(f"  Filesystem encoding: {sys.getfilesystemencoding()}")
    print(f"  Locale preferred encoding: {locale.getpreferredencoding()}")
    print()

    # Environment variables
    print("ENVIRONMENT VARIABLES:")
    pythonio = os.environ.get('PYTHONIOENCODING', 'NOT SET')
    lang = os.environ.get('LANG', 'NOT SET')
    lc_all = os.environ.get('LC_ALL', 'NOT SET')

    print(f"  PYTHONIOENCODING: {pythonio}")
    print(f"  LANG: {lang}")
    print(f"  LC_ALL: {lc_all}")
    print()

    return pythonio, sys.stdout.encoding

def test_unicode_output():
    """Test Unicode/emoji output without any encoding fixes."""
    print("UNICODE OUTPUT TESTS:")

    tests = [
        ("Basic emojis", "🚀 💻 🔥 ⭐ ✅"),
        ("Complex emojis", "👨‍💻 👩‍🎨 🏳️‍🌈"),
        ("Mixed content", "Python 🐍 + Unicode 🌟 = Success! ✨"),
        ("Special chars", "αβγδε ñüäöß 中文 العربية"),
        ("Math symbols", "π ≈ 3.14159 ∞ ∑ ∆ ∇ ∫"),
    ]

    results = []
    for test_name, test_string in tests:
        try:
            print(f"  {test_name}: {test_string}")
            results.append((test_name, True, None))
        except UnicodeEncodeError as e:
            print(f"  {test_name}: ❌ FAILED - {e}")
            results.append((test_name, False, str(e)))
        except Exception as e:
            print(f"  {test_name}: ❌ ERROR - {e}")
            results.append((test_name, False, str(e)))

    return results

def analyze_results(pythonio, stdout_encoding, test_results):
    """Analyze test results and provide recommendations."""
    print()
    print("=" * 60)
    print("ANALYSIS & RECOMMENDATIONS")
    print("=" * 60)

    # Check if system-level UTF-8 is working
    passed_tests = sum(1 for _, success, _ in test_results if success)
    total_tests = len(test_results)

    print(f"Tests passed: {passed_tests}/{total_tests}")
    print()

    if passed_tests == total_tests:
        print("🎉 EXCELLENT! System-level UTF-8 is working perfectly!")
        print("✅ All Unicode tests passed without any script-level fixes.")
        print("✅ Your system is properly configured for Unicode support.")

        if pythonio == "utf-8" and stdout_encoding == "utf-8":
            print("✅ Environment variables are correctly set.")
        else:
            print("ℹ️  Note: System works despite some encoding settings.")

        print("\n🏆 No further action needed - Unicode is working!")
        return True

    elif passed_tests > 0:
        print("⚠️  PARTIAL SUCCESS - Some Unicode tests passed.")
        print("🔧 System-level configuration may need adjustment.")

        failed_tests = [name for name, success, _ in test_results if not success]
        print(f"Failed tests: {', '.join(failed_tests)}")

    else:
        print("❌ SYSTEM-LEVEL UTF-8 NOT WORKING")
        print("🔧 System configuration needs to be fixed.")

    # Provide specific recommendations
    print("\nRECOMMENDATIONS:")

    if pythonio != "utf-8":
        print("1. Run setup script to set PYTHONIOENCODING=utf-8:")
        print("   - Windows: setup_windows_utf8.bat or setup_windows_utf8.ps1")
        print("   - Git Bash: Source updated ~/.bashrc")

    if stdout_encoding != "utf-8":
        print("2. Console encoding needs fixing:")
        print("   - Windows CMD: chcp 65001")
        print("   - PowerShell: Run setup_powershell_utf8.ps1")

    print("3. Restart terminal after running setup scripts")
    print("4. Re-run this test to verify fixes")

    return False

def main():
    """Main test function."""
    print("Testing system-wide Unicode support...")
    print("This test runs WITHOUT any script-level encoding fixes.")
    print()

    # Test encoding settings
    pythonio, stdout_encoding = test_encoding_settings()

    # Test Unicode output
    test_results = test_unicode_output()

    # Analyze and provide recommendations
    success = analyze_results(pythonio, stdout_encoding, test_results)

    print("\n" + "=" * 60)
    if success:
        print("STATUS: ✅ SYSTEM UNICODE SUPPORT IS WORKING!")
    else:
        print("STATUS: ❌ SYSTEM UNICODE SUPPORT NEEDS CONFIGURATION")
    print("=" * 60)

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())