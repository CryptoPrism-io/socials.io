"""New modular Instagram content generation script."""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from workflows.instagram_pipeline import run_complete_pipeline

if __name__ == "__main__":
    """Main entry point for Instagram content generation."""
    print("🚀 Starting Modular Instagram Content Generation")

    success = asyncio.run(run_complete_pipeline())

    if success:
        print("✅ Content generation completed successfully!")
        exit(0)
    else:
        print("❌ Content generation failed!")
        exit(1)