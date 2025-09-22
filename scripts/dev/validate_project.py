#!/usr/bin/env python3
"""
Comprehensive project validation script for socialio.
Validates environment, dependencies, structure, and core functionality.
"""
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.stdout:
            print("STDOUT:")
            print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        success = result.returncode == 0
        print(f"Status: {'+ PASSED' if success else '- FAILED'}")
        return success

    except subprocess.TimeoutExpired:
        print("- FAILED (Timeout)")
        return False
    except Exception as e:
        print(f"- FAILED (Error: {e})")
        return False

def main():
    """Run comprehensive project validation."""
    print("SOCIALIO PROJECT VALIDATION")
    print("=" * 60)

    # Track test results
    results = {}

    # Environment validation
    results['env'] = run_command(
        "python validate_env.py",
        "Environment Variables Configuration"
    )

    # Structure validation
    results['structure'] = run_command(
        "python tests/test_path_structure.py",
        "Project Structure Validation"
    )

    # Comprehensive tests
    results['restructure'] = run_command(
        "python tests/test_restructure.py",
        "Restructure Validation Tests"
    )

    # Pytest execution
    results['pytest'] = run_command(
        "python -m pytest tests/ -v --tb=short",
        "PyTest Unit Tests"
    )

    # Code quality checks
    results['flake8'] = run_command(
        "flake8 config/ tests/ --max-line-length=88 --extend-ignore=E203,W503 --statistics",
        "Code Quality (Flake8)"
    )

    # Security scan
    results['bandit'] = run_command(
        "bandit -r config/ tests/ -f txt",
        "Security Scan (Bandit)"
    )

    # Dependency check
    results['packages'] = run_command(
        "pip list | grep -E '(playwright|jinja2|sqlalchemy|pandas|gspread)'",
        "Critical Package Verification"
    )

    # Final summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, success in results.items():
        status = "+ PASSED" if success else "- FAILED"
        print(f"{test_name:20}: {status}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("+ ALL VALIDATIONS PASSED! Project is ready for deployment.")
        return 0
    else:
        print("! Some validations failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)