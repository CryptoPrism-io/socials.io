"""New modular Instagram publishing script."""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from workflows.publishing_workflow import run_publishing_workflow

if __name__ == "__main__":
    """Main entry point for Instagram publishing."""
    print("🚀 Starting Modular Instagram Publishing")

    success = run_publishing_workflow()

    if success:
        print("✅ Publishing completed successfully!")
        exit(0)
    else:
        print("❌ Publishing failed!")
        exit(1)